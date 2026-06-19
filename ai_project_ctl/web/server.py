"""Standard-library loopback HTTP server for the Web Control Center."""

from __future__ import annotations

import html
import ipaddress
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence
from urllib.parse import parse_qs, urlparse

from ai_project_ctl.core.result import CommandError
from ai_project_ctl.web.actions import (
    WebActionError,
    WebActionExecutor,
    WebActionResult,
    available_actions,
)
from ai_project_ctl.web.read_model import ReadOnlyProjectModel


LOCAL_HOSTS = {"localhost"}
LOCAL_ADDRESSES = {"127.0.0.1", "::1"}

NAV_ITEMS = (
    ("/", "Dashboard"),
    ("/tasks", "Tasks"),
    ("/evolution", "Evolution"),
    ("/epics", "Epics"),
    ("/reviews", "Reviews"),
    ("/events", "Events"),
    ("/generated", "Generated"),
    ("/doctor", "Doctor"),
    ("/commands", "Commands"),
    ("/actions", "Actions"),
)

TASK_FOCUS_STATUSES = {"ready", "in_progress", "in_review", "changes_requested"}
TASK_GROUP_OPTIONS = {"none", "epic", "status"}
CHANGE_ACTION_STATUSES = {"ready", "approved", "in_progress", "in_review"}
TASK_ROW_WORKFLOWS = (
    {
        "action": "task.prepare_for_codex",
        "statuses": {"planned", "ready", "changes_requested"},
        "label": "Prepare for Codex",
    },
    {
        "action": "task.refresh_execution_context",
        "statuses": {"in_progress"},
        "label": "Refresh Context",
        "current": True,
    },
    {
        "action": "task.submit_for_review",
        "statuses": {"in_progress"},
        "label": "Submit for Review",
    },
    {
        "action": "task.close_reviewed",
        "statuses": {"in_review"},
        "label": "Approve & Done",
        "notes_label": "Approval Notes",
        "notes_placeholder": "Record the Human Owner approval basis.",
    },
    {
        "action": "task.request_changes",
        "statuses": {"in_review"},
        "label": "Request Changes",
        "notes_label": "Change Request Notes",
        "notes_placeholder": "Describe the required rework.",
    },
)


class WebServerError(CommandError):
    """Stable web server error."""


def run_server(
    root: str | Path = ".",
    *,
    host: str = "127.0.0.1",
    port: int = 8765,
    actor: str = "human_owner",
) -> None:
    """Run the local Web Control Center until interrupted."""

    _require_loopback_host(host)
    model = ReadOnlyProjectModel(root, actor=actor)
    server = ThreadingHTTPServer((host, port), make_handler(model))
    url = "http://{}:{}".format(host, server.server_address[1])
    print("Web Control Center: {}".format(url))
    print("Root: {}".format(model.root))
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("")
    finally:
        server.server_close()


def make_handler(model: ReadOnlyProjectModel) -> type[BaseHTTPRequestHandler]:
    """Create a request handler bound to one project model."""

    class ControlCenterHandler(BaseHTTPRequestHandler):
        server_version = "AIProjectControlCenter/0.1"

        def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
            self._handle_read(head_only=False)

        def do_HEAD(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
            self._handle_read(head_only=True)

        def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
            self._handle_write()

        def do_PUT(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
            self._method_not_allowed()

        def do_PATCH(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
            self._method_not_allowed()

        def do_DELETE(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
            self._method_not_allowed()

        def log_message(self, format: str, *args: Any) -> None:
            return

        def _handle_read(self, *, head_only: bool) -> None:
            parsed = urlparse(self.path)
            try:
                status, content_type, body = route(
                    parsed.path,
                    model,
                    query=parse_qs(parsed.query),
                )
            except CommandError as exc:
                status = HTTPStatus.INTERNAL_SERVER_ERROR
                content_type = "text/html; charset=utf-8"
                body = render_error(exc)
            payload = body.encode("utf-8")
            self.send_response(int(status))
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            if not head_only:
                self.wfile.write(payload)

        def _handle_write(self) -> None:
            path = urlparse(self.path).path
            if path != "/actions":
                self._not_found()
                return

            try:
                fields = self._read_action_fields()
                executor = WebActionExecutor(model.root, actor=model.actor)
                result = executor.execute(fields)
                model.invalidate_caches()
                status = HTTPStatus.OK
                body = render_action_result(result)
            except WebActionError as exc:
                status = HTTPStatus.BAD_REQUEST
                body = render_action_error(exc)

            payload = body.encode("utf-8")
            self.send_response(int(status))
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(payload)

        def _read_action_fields(self) -> dict[str, str]:
            length_header = self.headers.get("Content-Length", "0")
            try:
                length = int(length_header)
            except ValueError as exc:
                raise WebActionError(
                    "WEB_INVALID_CONTENT_LENGTH",
                    "Invalid write request content length.",
                    details={"content_length": length_header},
                ) from exc
            if length > 262144:
                raise WebActionError(
                    "WEB_ACTION_BODY_TOO_LARGE",
                    "Write request body is too large.",
                    details={"max_bytes": 262144, "content_length": length},
                )

            raw = self.rfile.read(length).decode("utf-8") if length else ""
            content_type = self.headers.get("Content-Type", "")
            if "application/json" in content_type:
                try:
                    payload = json.loads(raw or "{}")
                except json.JSONDecodeError as exc:
                    raise WebActionError(
                        "WEB_INVALID_JSON_BODY",
                        "Write request body is not valid JSON.",
                        details={"error": str(exc)},
                    ) from exc
                if not isinstance(payload, dict):
                    raise WebActionError(
                        "WEB_INVALID_ACTION_BODY",
                        "Write request JSON body must be an object.",
                    )
                return {str(key): str(value) for key, value in payload.items()}

            parsed = parse_qs(raw, keep_blank_values=True)
            return {key: values[-1] if values else "" for key, values in parsed.items()}

        def _method_not_allowed(self) -> None:
            payload = (
                "Unsupported method. This local control center accepts GET, HEAD, "
                "and confirmed POST requests to /actions only.\n"
            ).encode("utf-8")
            self.send_response(HTTPStatus.METHOD_NOT_ALLOWED)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Allow", "GET, HEAD, POST")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(payload)

        def _not_found(self) -> None:
            payload = b"Not found.\n"
            self.send_response(HTTPStatus.NOT_FOUND)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(payload)

    return ControlCenterHandler


def route(
    path: str,
    model: ReadOnlyProjectModel,
    *,
    query: Mapping[str, Sequence[str]] | None = None,
) -> tuple[HTTPStatus, str, str]:
    """Route one read-only request."""

    if "?" in path:
        parsed = urlparse(path)
        path = parsed.path
        query = parse_qs(parsed.query)
    query = query or {}
    refresh_doctor = _query_enabled(query, "refresh")

    if path == "/healthz":
        return HTTPStatus.OK, "application/json; charset=utf-8", json.dumps(
            {"ok": True, "mode": "controlled-writes", "write_route": "/actions"},
            indent=2,
            sort_keys=True,
        )
    if path == "/data.json":
        return HTTPStatus.OK, "application/json; charset=utf-8", json.dumps(
            model.dashboard(refresh_doctor=refresh_doctor),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )

    pages: dict[str, Callable[[], str]] = {
        "/": lambda: render_dashboard(model.dashboard()),
        "/tasks": lambda: render_tasks(model.dashboard(), query=query),
        "/evolution": lambda: render_evolution(model.dashboard(), query=query),
        "/epics": lambda: render_epics(model.dashboard()),
        "/reviews": lambda: render_reviews(model.dashboard(), query=query),
        "/events": lambda: render_events(model.dashboard(include_events=True)),
        "/generated": lambda: render_generated(model.dashboard()),
        "/doctor": lambda: render_doctor(
            model.dashboard(refresh_doctor=refresh_doctor)
        ),
        "/commands": lambda: render_commands(model),
        "/actions": lambda: render_actions(model.dashboard()),
    }
    if path not in pages:
        return HTTPStatus.NOT_FOUND, "text/html; charset=utf-8", render_page(
            "Not Found",
            '<section class="panel"><h2>Not found</h2><p>The requested page is not available.</p></section>',
            active="",
        )
    return HTTPStatus.OK, "text/html; charset=utf-8", pages[path]()


def render_dashboard(data: Mapping[str, Any]) -> str:
    current = data.get("current_task") or {}
    doctor = data.get("doctor") or {}
    summary = doctor.get("summary") or {}
    queue = data.get("queue") or []
    generated = data.get("generated") or []
    changes = data.get("changes") or []
    body = [
        '<section class="summary-grid">',
        metric("Doctor", str(doctor.get("overall_status") or "UNKNOWN")),
        metric("Current Task", task_label(current)),
        metric("Queue", "{} executable".format(len(queue))),
        metric("Changes", "{} proposals".format(len(changes))),
        metric("Generated", "{} derived views".format(sum(1 for item in generated if item.get("exists")))),
        "</section>",
        '<section class="panel">',
        "<h2>Current Task</h2>",
        task_detail(current),
        "</section>",
        '<section class="panel">',
        "<h2>Executable Queue</h2>",
        task_table(queue[:12], empty_text="No executable queue items."),
        "</section>",
        '<section class="panel">',
        "<h2>Project Doctor</h2>",
        '<div class="status-row">',
        status_badge(str(doctor.get("overall_status") or "UNKNOWN")),
        "<span>{} PASS</span><span>{} WARN</span><span>{} FAIL</span>".format(
            escape(summary.get("PASS", 0)),
            escape(summary.get("WARN", 0)),
            escape(summary.get("FAIL", 0)),
        ),
        doctor_cache_detail(doctor),
        '<a class="button-link" href="/doctor?refresh=1">Refresh doctor</a>',
        "</div>",
        "</section>",
    ]
    return render_page("Dashboard", "".join(body), active="/")


def render_tasks(
    data: Mapping[str, Any],
    *,
    query: Mapping[str, Sequence[str]] | None = None,
) -> str:
    counts = data.get("task_counts") or {}
    query = query or {}
    filters = task_filter_state(data, query)
    tasks = filter_tasks(data.get("tasks") or [], data, filters)
    focused = focus_tasks(data, tasks)
    body = [
        '<section class="summary-grid">',
        *[metric(str(status), str(count)) for status, count in sorted(counts.items())],
        metric("Visible", str(len(tasks))),
        "</section>",
        '<section class="panel">',
        "<h2>Task Filters</h2>",
        task_filter_form(data, filters),
        task_filter_summary(filters),
        "</section>",
        '<section class="panel">',
        "<h2>Focus Tasks</h2>",
        task_table(
            focused,
            empty_text="No current, in-progress, or review tasks match the filters.",
            data=data,
            include_actions=True,
        ),
        "</section>",
        '<section class="panel">',
        "<h2>Tasks</h2>",
        task_grouped_table(tasks, data, filters, empty_text="No tasks match the filters."),
        "</section>",
    ]
    return render_page("Tasks", "".join(body), active="/tasks")


def render_evolution(
    data: Mapping[str, Any],
    *,
    query: Mapping[str, Sequence[str]] | None = None,
) -> str:
    counts = data.get("change_counts") or {}
    query = query or {}
    filters = change_filter_state(data, query)
    changes = filter_changes(data.get("changes") or [], filters)
    current = data.get("current_task") or {}
    default_task = current.get("ref") or current.get("id") or ""
    task_options = task_select_options(data)
    body = [
        '<section class="summary-grid">',
        *[metric(str(status), str(count)) for status, count in sorted(counts.items(), key=lambda item: status_sort_key(str(item[0])))],
        metric("Visible", str(len(changes))),
        "</section>",
        '<section class="panel">',
        "<h2>Evolution Filters</h2>",
        change_filter_form(data, filters),
        change_filter_summary(filters),
        "</section>",
        '<section class="panel action-panel">',
        "<h2>Create Change For Task</h2>",
        action_form(
            "evolution.create_for_task",
            [
                select_field_values("task", "Task", task_options)
                if task_options
                else input_field("task", "Task", default_task),
            ],
            button_label="Create Evolution Change",
        ),
        "</section>",
        '<section class="panel">',
        "<h2>Change Proposals</h2>",
        change_table(changes, data, empty_text="No Change Proposals match the filters."),
        "</section>",
    ]
    return render_page("Evolution", "".join(body), active="/evolution")


def render_epics(data: Mapping[str, Any]) -> str:
    rows = []
    for epic in data.get("epics") or []:
        cells = [
            escape(epic.get("key") or epic.get("id")),
            status_badge(str(epic.get("status") or "unknown")),
            escape(epic.get("initiative_id", "")),
            escape(epic.get("title", "")),
            pipeline_hint_cell(epic),
        ]
        rows.append("<tr>{}</tr>".format("".join("<td>{}</td>".format(cell) for cell in cells)))
    body = [
        '<section class="panel">',
        "<h2>Epics</h2>",
        table(("Epic", "Status", "Initiative", "Title", "Next / Blockers"), rows, "No epics."),
        "</section>",
    ]
    return render_page("Epics", "".join(body), active="/epics")


def render_reviews(
    data: Mapping[str, Any],
    *,
    query: Mapping[str, Sequence[str]] | None = None,
) -> str:
    review_commands = data.get("review_commands") or []
    selected_task = _query_value(query or {}, "task")
    review_tasks = task_review_candidates(data, selected_task)
    command_rows = [
        "<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            escape(command.get("name")),
            status_badge(str(command.get("availability") or "planned")),
            escape(command.get("description", "")),
        )
        for command in review_commands
    ]
    body = [
        '<section class="panel">',
        "<h2>Task Review Packages</h2>",
        review_task_selector(data, selected_task),
        task_review_packages(review_tasks, data, selected_task=selected_task),
        "</section>",
        '<section class="panel">',
        "<h2>Review Registry</h2>",
        table(("Command", "Availability", "Description"), command_rows, "No review commands registered."),
        "</section>",
    ]
    return render_page("Reviews", "".join(body), active="/reviews")


def render_events(data: Mapping[str, Any]) -> str:
    sections = []
    for audit in data.get("events") or []:
        lines = audit.get("lines") or []
        if lines:
            content = "".join("<li>{}</li>".format(escape(line)) for line in lines)
        else:
            content = "<li>{}</li>".format(escape(audit.get("error") or "No recent events."))
        sections.append(
            '<section class="panel"><h2>{}</h2><ul class="event-list">{}</ul></section>'.format(
                escape(audit.get("domain", "audit").title()),
                content,
            )
        )
    return render_page("Events", "".join(sections), active="/events")


def render_generated(data: Mapping[str, Any]) -> str:
    rows = []
    for item in data.get("generated") or []:
        rows.append(
            "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                escape(item.get("label")),
                '<span class="pill">derived output</span>',
                "yes" if item.get("exists") else "no",
                escape(item.get("mtime", "")),
                escape(item.get("heading", "")),
            )
        )
    body = [
        '<section class="panel">',
        "<h2>Generated Views</h2>",
        table(("File", "Source", "Exists", "Updated", "First Line"), rows, "No generated views."),
        "</section>",
    ]
    return render_page("Generated", "".join(body), active="/generated")


def render_doctor(data: Mapping[str, Any]) -> str:
    doctor = data.get("doctor") or {}
    summary = doctor.get("summary") or {}
    rows = []
    for finding in doctor.get("findings") or []:
        rows.append(
            "<tr><td>{}</td><td>{}</td><td>{}</td><td><code>{}</code></td></tr>".format(
                status_badge(str(finding.get("status") or "UNKNOWN")),
                escape(finding.get("check", "")),
                escape(finding.get("message", "")),
                escape(finding.get("command", "")),
            )
        )
    body = [
        '<section class="panel">',
        "<h2>Project Doctor</h2>",
        '<div class="status-row">',
        status_badge(str(doctor.get("overall_status") or "UNKNOWN")),
        "<span>{} PASS</span><span>{} WARN</span><span>{} FAIL</span>".format(
            escape(summary.get("PASS", 0)),
            escape(summary.get("WARN", 0)),
            escape(summary.get("FAIL", 0)),
        ),
        doctor_cache_detail(doctor),
        '<a class="button-link" href="/doctor?refresh=1">Refresh doctor</a>',
        "</div>",
        table(("Status", "Check", "Message", "Command"), rows, "No doctor findings."),
        "</section>",
    ]
    return render_page("Doctor", "".join(body), active="/doctor")


def render_commands(model: ReadOnlyProjectModel) -> str:
    rows = []
    for command in model.command_catalog():
        read_write = command.get("read_write") or {}
        flags = []
        if read_write.get("mutates_state"):
            flags.append("writes state")
        if read_write.get("writes_events"):
            flags.append("writes events")
        if read_write.get("renders_generated"):
            flags.append("renders generated")
        if not flags:
            flags.append("read-only")
        rows.append(
            "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                escape(command.get("name", "")),
                escape(command.get("domain", "")),
                status_badge(str(command.get("kind") or "")),
                status_badge(str(command.get("availability") or "")),
                escape(", ".join(flags)),
            )
        )
    body = [
        '<section class="panel">',
        "<h2>Command Registry</h2>",
        table(("Command", "Domain", "Kind", "Availability", "Read/Write"), rows, "No commands registered."),
        "</section>",
    ]
    return render_page("Commands", "".join(body), active="/commands")


def render_actions(data: Mapping[str, Any]) -> str:
    current = data.get("current_task") or {}
    default_task = current.get("ref") or current.get("id") or ""
    epic_options = [
        (
            str(epic.get("id") or ""),
            "{} — {}".format(
                epic.get("key") or epic.get("id") or "",
                epic.get("title") or "",
            ).strip(" —"),
        )
        for epic in data.get("epics") or []
        if epic.get("id")
    ]
    workflow_rows = []
    for workflow in data.get("workflows") or []:
        step_titles = [
            "{} ({})".format(step.get("title", ""), step.get("route", ""))
            for step in workflow.get("steps") or []
        ]
        workflow_rows.append(
            "<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                escape(workflow.get("label", "")),
                escape(workflow.get("name", "")),
                escape(" -> ".join(step_titles)),
            )
        )
    action_rows = []
    for action in available_actions():
        read_write = action.get("read_write") or {}
        flags = []
        if read_write.get("mutates_state"):
            flags.append("writes state")
        if read_write.get("writes_events"):
            flags.append("writes events")
        if read_write.get("renders_generated"):
            flags.append("renders generated")
        action_rows.append(
            "<tr><td>{}</td><td><code>{}</code></td><td>{}</td></tr>".format(
                escape(action.get("label", "")),
                escape(action.get("command", "")),
                escape(", ".join(flags)),
            )
        )
    body = [
        '<section class="panel action-panel">',
        "<h2>Write Actions</h2>",
        table(("Action", "Registered Command", "Effect"), action_rows, "No write actions."),
        "</section>",
        '<section class="panel action-panel">',
        "<h2>Create Task</h2>",
        action_form(
            "task.create",
            [
                select_field_values("epic", "Epic", epic_options)
                if epic_options
                else input_field("epic", "Epic"),
                input_field("title", "Title"),
                input_field("summary", "Summary", required=False),
                textarea_field("description", "Description"),
                select_field(
                    "status",
                    "Status",
                    (
                        "planned",
                        "ready",
                        "proposed",
                    ),
                ),
                select_field(
                    "verification_mode",
                    "Verification",
                    (
                        "standard",
                        "light",
                        "manual",
                        "none",
                        "strict",
                    ),
                ),
                textarea_field("scope", "Scope"),
                textarea_field("out_of_scope", "Out of Scope"),
                textarea_field("allowed_file", "Allowed Files"),
                textarea_field("acceptance", "Acceptance"),
                textarea_field("review_instruction", "Review"),
                textarea_field("depends_on", "Depends On"),
                textarea_field("note", "Notes"),
                input_field("dependency_reason", "Dependency Reason", required=False),
            ],
        ),
        "</section>",
        '<section class="panel action-panel">',
        "<h2>Bulk Task Import</h2>",
        action_form(
            "task.import",
            [
                textarea_field(
                    "import_text",
                    "JSON Payload",
                    rows=12,
                    wide=True,
                    placeholder=(
                        '{\n'
                        '  "tasks": [\n'
                        '    {\n'
                        '      "epic": "EPIC-006",\n'
                        '      "title": "New planned task",\n'
                        '      "scope": ["Do one bounded thing"],\n'
                        '      "allowed_files": ["tests/**"],\n'
                        '      "acceptance_criteria": ["Validation passes"]\n'
                        '    }\n'
                        '  ]\n'
                        '}'
                    ),
                ),
            ],
            confirm_required=False,
            button_label="Preview / Import",
        ),
        "</section>",
        '<section class="panel action-panel">',
        "<h2>Task Workflows</h2>",
        table(("Workflow", "Command", "Step Preview"), workflow_rows, "No workflows."),
        action_form(
            "task.prepare_for_codex",
            [input_field("task", "Task", default_task)],
        ),
        action_form(
            "task.refresh_execution_context",
            [input_field("task", "Task", default_task)],
        ),
        action_form(
            "task.submit_for_review",
            [input_field("task", "Task", default_task)],
        ),
        action_form(
            "task.close_reviewed",
            [
                input_field("task", "Task", default_task),
                textarea_field("notes", "Approval Notes", required=True),
            ],
            button_label="Approve & Done",
        ),
        action_form(
            "task.request_changes",
            [
                input_field("task", "Task", default_task),
                textarea_field("notes", "Change Request Notes", required=True),
            ],
            button_label="Request Changes",
        ),
        action_form(
            "evolution.create_for_task",
            [input_field("task", "Task", default_task)],
        ),
        action_form(
            "evolution.accept_change",
            [
                input_field("change", "Change", "CHG-000"),
                textarea_field("notes", "Acceptance Notes"),
            ],
        ),
        action_form(
            "epic.close_if_complete",
            [
                select_field_values("epic", "Epic", epic_options)
                if epic_options
                else input_field("epic", "Epic"),
            ],
        ),
        "</section>",
        '<section class="panel action-panel">',
        "<h2>Task Transition</h2>",
        action_form(
            "task.transition",
            [
                input_field("task", "Task", default_task),
                select_field(
                    "to",
                    "Target",
                    (
                        "ready",
                        "in_progress",
                        "blocked",
                        "in_review",
                        "changes_requested",
                        "deferred",
                    ),
                ),
            ],
        ),
        "</section>",
        '<section class="panel action-panel">',
        "<h2>Current Task</h2>",
        action_form("current.set", [input_field("task", "Task", default_task)]),
        action_form("current.clear", []),
        "</section>",
        '<section class="panel action-panel">',
        "<h2>Generated Output</h2>",
        action_form("project.render", []),
        action_form("context.build", [input_field("task", "Task", default_task)]),
        action_form(
            "codex.prompt.build",
            [
                input_field("task", "Task", default_task),
                checkbox_field("with_context", "Include context"),
            ],
        ),
        "</section>",
    ]
    return render_page("Actions", "".join(body), active="/actions")


def render_error(error: CommandError) -> str:
    body = (
        '<section class="panel"><h2>Read Error</h2>'
        "<p>{}</p><pre>{}</pre></section>"
    ).format(
        escape(error.message),
        escape(json.dumps(error.details, indent=2, sort_keys=True)),
    )
    return render_page("Read Error", body, active="")


def render_action_result(result: WebActionResult) -> str:
    return render_page(
        "Action Result",
        action_result_panel(result.to_dict()),
        active="/actions",
    )


def render_action_error(error: WebActionError) -> str:
    payload = {
        "ok": False,
        "action": error.details.get("action", ""),
        "command": "",
        "label": "Action failed",
        "returncode": error.details.get("returncode"),
        "result": error.details.get("result"),
        "stderr": error.details.get("stderr", ""),
        "error": {
            "code": error.code,
            "message": error.message,
            "details": error.details,
        },
    }
    return render_page(
        "Action Failed",
        action_result_panel(payload),
        active="/actions",
    )


def action_result_panel(payload: Mapping[str, Any]) -> str:
    ok = bool(payload.get("ok"))
    result = _mapping(payload.get("result"))
    summary = _mapping(payload.get("summary"))
    data = _mapping(result.get("data"))
    workflow = _mapping(data.get("workflow"))
    visible_errors = _messages(result.get("errors"))
    error_info = _mapping(payload.get("error"))
    if error_info:
        visible_errors.insert(
            0,
            {
                "code": str(error_info.get("code") or "WEB_ACTION_FAILED"),
                "message": str(error_info.get("message") or "Action failed."),
                "path": "",
                "details": _mapping(error_info.get("details")),
            },
        )
    status_kind = "pass" if ok else "fail"
    sections = [
        '<section class="panel action-result action-result-{}">'.format(status_kind),
        '<div class="action-result-header">',
        "<div>",
        "<h2>{}</h2>".format(escape(payload.get("label") or payload.get("action") or "Action result")),
        '<p class="muted">{}</p>'.format(
            escape(_result_message(result, error_info) or "Action completed.")
        ),
        "</div>",
        action_result_badge("PASS" if ok else "FAIL", status_kind),
        "</div>",
        '<div class="result-meta">',
        metric("Registered command", str(payload.get("command") or "unknown")),
        metric("Workflow", _workflow_name(workflow, payload)),
        metric("Target", _result_target(data)),
        metric("Return code", str(payload.get("returncode") if payload.get("returncode") is not None else "unknown")),
        "</div>",
    ]
    sections.extend(_step_panel(_result_steps(data, summary)))
    sections.extend(_file_list_panel("Changed Files", result.get("changed_files")))
    sections.extend(_file_list_panel("Generated Files", result.get("generated_files")))
    sections.extend(_message_panel("Warnings", "warn", _messages(result.get("warnings"))))
    sections.extend(_message_panel("Errors", "fail", visible_errors))
    sections.extend(_next_actions_panel(result, summary))
    sections.append(_technical_details(payload))
    sections.append("</section>")
    return "".join(sections)


def action_result_badge(label: str, kind: str) -> str:
    return '<span class="badge {}">{}</span>'.format(
        escape(kind),
        escape(label),
    )


def _result_message(result: Mapping[str, Any], error_info: Mapping[str, Any]) -> str:
    if result.get("message"):
        return str(result.get("message"))
    return str(error_info.get("message") or "")


def _workflow_name(workflow: Mapping[str, Any], payload: Mapping[str, Any]) -> str:
    return str(
        workflow.get("name")
        or workflow.get("label")
        or payload.get("action")
        or "none"
    )


def _result_target(data: Mapping[str, Any]) -> str:
    task = _mapping(data.get("task"))
    change = _mapping(data.get("change"))
    epic = _mapping(data.get("epic"))
    for key, value in (
        ("Task", data.get("task_ref") or task.get("ref") or task.get("id")),
        ("Change", data.get("change_ref") or change.get("id")),
        ("Epic", data.get("epic_ref") or epic.get("id")),
    ):
        text = str(value or "").strip()
        if text:
            return "{} {}".format(key, text)
    return "not reported"


def _result_steps(
    data: Mapping[str, Any],
    summary: Mapping[str, Any],
) -> list[Mapping[str, Any]]:
    steps = data.get("steps")
    if isinstance(steps, list):
        return [step for step in steps if isinstance(step, Mapping)]
    summary_steps = summary.get("steps")
    if isinstance(summary_steps, list):
        return [step for step in summary_steps if isinstance(step, Mapping)]
    return []


def _step_panel(steps: Sequence[Mapping[str, Any]]) -> list[str]:
    if not steps:
        return []
    rows = []
    for index, step in enumerate(steps, start=1):
        kind, label = _step_status(str(step.get("status") or "unknown"))
        detail_bits = [
            str(step.get("command_name") or "").strip(),
            str(step.get("route") or "").strip(),
        ]
        details = " / ".join(bit for bit in detail_bits if bit)
        if step.get("skip_reason"):
            details = "{}{}".format(
                "{}; ".format(details) if details else "",
                step.get("skip_reason"),
            )
        rows.append(
            '<li class="result-step result-step-{}">'
            "{}"
            '<div><strong>{}. {}</strong>{}</div>'
            "</li>".format(
                escape(kind),
                action_result_badge(label, kind),
                index,
                escape(step.get("title") or step.get("id") or "Step"),
                '<span class="muted"> {}</span>'.format(escape(details)) if details else "",
            )
        )
    return [
        '<section class="result-section">',
        "<h3>Steps</h3>",
        '<ol class="result-steps">{}</ol>'.format("".join(rows)),
        "</section>",
    ]


def _step_status(status: str) -> tuple[str, str]:
    normalized = status.lower()
    if normalized in {"ok", "pass", "passed", "success", "completed"}:
        return "pass", "PASS"
    if normalized in {"failed", "fail", "error"}:
        return "fail", "FAIL"
    return "warn", "WARN"


def _file_list_panel(title: str, value: Any) -> list[str]:
    items = _string_items(value)
    if not items:
        return []
    return [
        '<section class="result-section">',
        "<h3>{}</h3>".format(escape(title)),
        '<ul class="result-files">{}</ul>'.format(
            "".join("<li><code>{}</code></li>".format(escape(item)) for item in items)
        ),
        "</section>",
    ]


def _message_panel(
    title: str,
    kind: str,
    messages: Sequence[Mapping[str, Any]],
) -> list[str]:
    if not messages:
        return []
    items = []
    for message in messages:
        code = str(message.get("code") or kind.upper())
        text = str(message.get("message") or "")
        path = str(message.get("path") or "")
        detail = " ".join(bit for bit in (path, text) if bit)
        items.append(
            '<li>{} <strong>{}</strong>{}</li>'.format(
                action_result_badge(kind.upper(), kind),
                escape(code),
                ": {}".format(escape(detail)) if detail else "",
            )
        )
    return [
        '<section class="result-section result-section-{}">'.format(escape(kind)),
        "<h3>{}</h3>".format(escape(title)),
        '<ul class="result-messages">{}</ul>'.format("".join(items)),
        "</section>",
    ]


def _next_actions_panel(
    result: Mapping[str, Any],
    summary: Mapping[str, Any],
) -> list[str]:
    actions = _string_items(result.get("next_actions")) or _string_items(summary.get("next_actions"))
    codex_instruction = str(summary.get("next_codex_instruction") or "")
    owner_action = str(result.get("owner_action_required") or summary.get("owner_action_required") or "")
    if codex_instruction and codex_instruction not in actions:
        actions.insert(0, codex_instruction)
    if not actions and not owner_action and not codex_instruction:
        return []
    parts = ['<section class="result-section">', "<h3>Next Actions</h3>"]
    if owner_action:
        parts.append('<p class="callout">{}</p>'.format(escape(owner_action)))
    if codex_instruction:
        parts.append(
            '<label class="copy-field">Codex instruction'
            '<textarea readonly rows="2">{}</textarea></label>'.format(
                escape(codex_instruction)
            )
        )
    if actions:
        parts.append(
            '<ul class="result-actions">{}</ul>'.format(
                "".join("<li>{}</li>".format(escape(action)) for action in actions)
            )
        )
    parts.append("</section>")
    return parts


def _technical_details(payload: Mapping[str, Any]) -> str:
    technical = _sanitize_technical(payload)
    return (
        '<details class="result-technical">'
        "<summary>Technical details</summary>"
        "<pre>{}</pre>"
        "</details>"
    ).format(escape(json.dumps(technical, ensure_ascii=False, indent=2, sort_keys=True)))


def _sanitize_technical(value: Any) -> Any:
    if isinstance(value, Mapping):
        redacted: dict[str, Any] = {}
        for key, item in value.items():
            key_text = str(key)
            if key_text in {"delegate", "registered_command", "stdout", "stderr"}:
                continue
            if key_text == "command" and isinstance(item, list):
                continue
            redacted[key_text] = _sanitize_technical(item)
        return redacted
    if isinstance(value, list):
        return [_sanitize_technical(item) for item in value]
    return value


def task_review_candidates(
    data: Mapping[str, Any],
    selected_task: str = "",
) -> list[Mapping[str, Any]]:
    tasks = [
        task
        for task in data.get("tasks") or []
        if isinstance(task, Mapping)
    ]
    if selected_task:
        return [task for task in tasks if task_ref_matches(task, selected_task)]
    return [task for task in tasks if str(task.get("status") or "") == "in_review"]


def review_task_selector(data: Mapping[str, Any], selected_task: str) -> str:
    options = [("", "Tasks in review"), *task_select_options(data)]
    return (
        '<form class="task-controls" method="get" action="/reviews">'
        "{}"
        '<button type="submit">Open</button>'
        '<a class="button-link secondary" href="/reviews">Reset</a>'
        "</form>"
    ).format(
        filter_select("task", "Task", options, selected_task),
    )


def task_review_packages(
    tasks: Sequence[Mapping[str, Any]],
    data: Mapping[str, Any],
    *,
    selected_task: str = "",
) -> str:
    if not tasks:
        if selected_task:
            return '<p class="empty">No task matches {}.</p>'.format(
                escape(selected_task)
            )
        return '<p class="empty">No tasks are currently in review.</p>'
    return "".join(task_review_package(task, data) for task in tasks)


def task_review_package(task: Mapping[str, Any], data: Mapping[str, Any]) -> str:
    status = str(task.get("status") or "unknown")
    report = _mapping(task.get("latest_report"))
    task_ref = str(task.get("ref") or task.get("id") or "")
    parts = [
        '<section class="review-package review-package-{}">'.format(
            escape(css_token(status))
        ),
        '<div class="review-package-header">',
        "<div>",
        '<h3>{}</h3>'.format(escape(task.get("title") or task_ref or "Task")),
        '<div class="status-row">{}{}{}{}</div>'.format(
            status_badge(status),
            '<strong>{}</strong>'.format(escape(task_ref)) if task_ref else "",
            '<code>{}</code>'.format(escape(task.get("legacy_id") or task.get("id") or "")),
            '<span>{}</span>'.format(escape(task.get("active_stage") or "")),
        ),
        "</div>",
        "</div>",
        task_review_context(task),
        linked_change_panel(task, data),
        codex_report_panel(report),
        review_decision_controls(task, data),
        "</section>",
    ]
    return "".join(parts)


def task_review_context(task: Mapping[str, Any]) -> str:
    rows = [
        ("Ref", escape(task.get("ref") or task.get("id") or "")),
        ("Legacy ID", escape(task.get("legacy_id") or task.get("id") or "")),
        ("Task ID", escape(task.get("id") or "")),
        ("Status", status_badge(str(task.get("status") or "unknown"))),
        ("Summary", escape(task.get("summary") or task.get("description") or "")),
        ("Scope", text_list(task.get("scope"), empty_text="No scope recorded.")),
        (
            "Acceptance",
            text_list(
                task.get("acceptance_criteria"),
                empty_text="No acceptance criteria recorded.",
            ),
        ),
    ]
    return '<div class="review-grid">{}</div>'.format(
        "".join(
            '<div class="review-field"><span>{}</span><div>{}</div></div>'.format(
                escape(label),
                value,
            )
            for label, value in rows
        )
    )


def linked_change_panel(task: Mapping[str, Any], data: Mapping[str, Any]) -> str:
    changes = linked_changes_for_task(task, data)
    if not changes:
        return (
            '<section class="review-section">'
            "<h3>Linked Evolution Change</h3>"
            '<p class="empty">No linked Evolution Change.</p>'
            "</section>"
        )
    rows = []
    for change in changes:
        rows.append(
            "<tr><td><code>{}</code></td><td>{}</td><td>{}</td></tr>".format(
                escape(change.get("id") or ""),
                status_badge(str(change.get("status") or "unknown")),
                escape(change.get("title") or ""),
            )
        )
    return (
        '<section class="review-section">'
        "<h3>Linked Evolution Change</h3>"
        "{}"
        "</section>"
    ).format(
        table(("Change", "Status", "Title"), rows, "No linked Evolution Change."),
    )


def codex_report_panel(report: Mapping[str, Any]) -> str:
    if not report:
        return (
            '<section class="review-section">'
            "<h3>Codex Execution Report</h3>"
            '<p class="empty">No Codex execution report submitted for this task.</p>'
            "</section>"
        )
    summary = str(report.get("implementation_summary") or "")
    return (
        '<section class="review-section">'
        "<h3>Codex Execution Report</h3>"
        '<div class="review-grid">'
        '<div class="review-field"><span>Report</span><div><code>{}</code></div></div>'
        '<div class="review-field"><span>Submitted</span><div>{}</div></div>'
        '<div class="review-field"><span>Owner Decision</span><div>{}</div></div>'
        '<div class="review-field wide-field"><span>Summary</span><div>{}</div></div>'
        "</div>"
        "{}{}{}{}"
        "</section>"
    ).format(
        escape(report.get("id") or ""),
        escape(report.get("submitted_at") or "not reported"),
        "required" if report.get("owner_decision_required") else "not required",
        escape(summary or "No implementation summary recorded."),
        report_file_panel("Changed Source Files", report.get("changed_files")),
        report_file_panel(
            "Generated / Project-Control Files",
            report.get("generated_files"),
        ),
        report_checks_panel(report.get("checks")),
        report_messages_panel(report),
    )


def report_file_panel(title: str, value: Any) -> str:
    return (
        '<section class="review-subsection">'
        "<h4>{}</h4>"
        "{}"
        "</section>"
    ).format(
        escape(title),
        text_list(value, empty_text="None reported.", code=True),
    )


def report_checks_panel(value: Any) -> str:
    checks = [check for check in value or [] if isinstance(check, Mapping)]
    rows = []
    for check in checks:
        blocking = "blocking" if check.get("blocking") else "advisory"
        detail = str(check.get("details") or check.get("command") or "")
        rows.append(
            "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                escape(check.get("name") or "check"),
                status_badge(str(check.get("result") or "unknown")),
                escape(blocking),
                escape(detail),
            )
        )
    return (
        '<section class="review-subsection">'
        "<h4>Checks</h4>"
        "{}"
        "</section>"
    ).format(
        table(("Check", "Result", "Type", "Details"), rows, "No checks reported."),
    )


def report_messages_panel(report: Mapping[str, Any]) -> str:
    sections = []
    for title, field in (
        ("Warnings", "warnings"),
        ("Blockers", "blockers"),
        ("Notes", "notes"),
    ):
        sections.append(
            '<section class="review-subsection">'
            "<h4>{}</h4>"
            "{}"
            "</section>".format(
                escape(title),
                text_list(report.get(field), empty_text="None reported."),
            )
        )
    return "".join(sections)


def review_decision_controls(
    task: Mapping[str, Any],
    data: Mapping[str, Any],
) -> str:
    status = str(task.get("status") or "")
    if status != "in_review":
        return (
            '<section class="review-section">'
            "<h3>Review Decision</h3>"
            '<p class="empty">Review decision controls unavailable: task status is {}.</p>'
            "</section>"
        ).format(escape(status or "unknown"))

    task_ref = str(task.get("ref") or task.get("id") or "")
    workflows = workflow_by_name(data)
    controls = []
    for action_id, label, notes_label, placeholder in (
        (
            "task.close_reviewed",
            "Approve & Done",
            "Approval Notes",
            "Record the Human Owner approval basis.",
        ),
        (
            "task.request_changes",
            "Request Changes",
            "Change Request Notes",
            "Describe the required rework.",
        ),
    ):
        controls.append(
            '<div class="review-action">'
            "<h4>{}</h4>"
            "{}"
            "{}"
            "</div>".format(
                escape(label),
                workflow_preview_html(workflows.get(action_id) or {}),
                action_form(
                    action_id,
                    [
                        hidden_field("task", task_ref),
                        textarea_field(
                            "notes",
                            notes_label,
                            rows=2,
                            placeholder=placeholder,
                            required=True,
                        ),
                    ],
                    button_label=label,
                ),
            )
        )
    return (
        '<section class="review-section">'
        "<h3>Review Decision</h3>"
        '<div class="review-actions">{}</div>'
        "</section>"
    ).format("".join(controls))


def linked_changes_for_task(
    task: Mapping[str, Any],
    data: Mapping[str, Any],
) -> list[Mapping[str, Any]]:
    refs = set(task_ref_values(task))
    matches = []
    for change in data.get("changes") or []:
        if not isinstance(change, Mapping):
            continue
        linked = set(_string_items(change.get("linked_tasks")))
        if refs.intersection(linked):
            matches.append(change)
    return matches


def task_ref_matches(task: Mapping[str, Any], value: str) -> bool:
    needle = str(value or "").strip()
    return bool(needle) and needle in set(task_ref_values(task))


def task_ref_values(task: Mapping[str, Any]) -> list[str]:
    values = [
        str(task.get("id") or ""),
        str(task.get("ref") or ""),
        str(task.get("legacy_id") or ""),
    ]
    aliases = task.get("aliases")
    if isinstance(aliases, Sequence) and not isinstance(aliases, (str, bytes)):
        values.extend(str(alias or "") for alias in aliases)
    return [value for value in values if value]


def text_list(
    value: Any,
    *,
    empty_text: str,
    code: bool = False,
) -> str:
    items = _string_items(value)
    if not items:
        return '<p class="empty">{}</p>'.format(escape(empty_text))
    if code:
        return '<ul class="compact-list">{}</ul>'.format(
            "".join("<li><code>{}</code></li>".format(escape(item)) for item in items)
        )
    return '<ul class="compact-list">{}</ul>'.format(
        "".join("<li>{}</li>".format(escape(item)) for item in items)
    )


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _messages(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _string_items(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item).strip()]


def render_page(title: str, body: str, *, active: str) -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} - AI Control Center</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f6f7f9;
      --panel: #ffffff;
      --text: #18202a;
      --muted: #5d6875;
      --line: #d9dee7;
      --accent: #0f766e;
      --accent-soft: #d9f2ee;
      --warn: #9a5b00;
      --warn-soft: #fff3d6;
      --fail: #a52828;
      --fail-soft: #ffe3e3;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font: 14px/1.5 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    header {{
      background: #17212f;
      color: #f8fbff;
      border-bottom: 1px solid #111827;
    }}
    .header-inner {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 18px 20px 16px;
    }}
    h1 {{
      margin: 0 0 12px;
      font-size: 24px;
      font-weight: 700;
      letter-spacing: 0;
    }}
    nav {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    nav a {{
      color: #dce8f6;
      text-decoration: none;
      border: 1px solid rgba(255,255,255,.22);
      border-radius: 6px;
      padding: 6px 10px;
      min-height: 32px;
    }}
    nav a.active {{
      background: #f8fbff;
      color: #17212f;
      border-color: #f8fbff;
    }}
    main {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 20px;
    }}
    .summary-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
      margin-bottom: 16px;
    }}
    .metric, .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
    }}
    .metric {{
      padding: 14px;
      min-height: 86px;
    }}
    .metric span {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: .04em;
    }}
    .metric strong {{
      display: block;
      margin-top: 8px;
      font-size: 20px;
      line-height: 1.2;
      word-break: break-word;
    }}
    .panel {{
      padding: 16px;
      margin-bottom: 16px;
      overflow-x: auto;
    }}
    h2 {{
      margin: 0 0 12px;
      font-size: 18px;
      letter-spacing: 0;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      min-width: 860px;
    }}
    th, td {{
      border-bottom: 1px solid var(--line);
      padding: 9px 8px;
      text-align: left;
      vertical-align: top;
    }}
    th {{
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: .04em;
      white-space: nowrap;
    }}
    code, pre {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 12px;
    }}
    pre {{
      white-space: pre-wrap;
      background: #f1f4f8;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 12px;
    }}
    .badge, .pill {{
      display: inline-flex;
      align-items: center;
      min-height: 24px;
      border-radius: 999px;
      padding: 2px 9px;
      font-size: 12px;
      font-weight: 700;
      background: #eef2f7;
      color: #334155;
      white-space: nowrap;
    }}
    .badge.pass, .badge.ready, .badge.in_progress, .badge.approved, .badge.accepted, .badge.implemented, .badge.read, .badge.validation {{
      background: var(--accent-soft);
      color: var(--accent);
    }}
    .badge.warn, .badge.planned, .badge.blocked, .badge.in_review {{
      background: var(--warn-soft);
      color: var(--warn);
    }}
    .badge.fail, .badge.changes_requested, .badge.write {{
      background: var(--fail-soft);
      color: var(--fail);
    }}
    .pill {{
      background: #e7edf5;
      color: #425166;
      font-weight: 600;
    }}
    .status-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: center;
    }}
    .event-list {{
      margin: 0;
      padding-left: 18px;
    }}
    .event-list li {{
      margin: 5px 0;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 12px;
      word-break: break-word;
    }}
    .compact-list {{
      margin: 0;
      padding-left: 16px;
    }}
    .compact-list li {{
      margin: 2px 0;
    }}
    .pipeline-hints {{
      display: grid;
      gap: 6px;
      min-width: 190px;
      max-width: 320px;
    }}
    .hint-next strong, .hint-change strong {{
      color: var(--text);
    }}
    .hint-list {{
      margin: 0;
      padding-left: 16px;
      color: var(--warn);
      overflow-wrap: anywhere;
    }}
    .hint-list li {{
      margin: 3px 0;
    }}
    .muted {{
      color: var(--muted);
    }}
    .action-panel form {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 10px;
      align-items: end;
      padding: 12px 0;
      border-top: 1px solid var(--line);
    }}
    .action-panel form:first-of-type {{
      border-top: 0;
      padding-top: 0;
    }}
    .task-controls {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 10px;
      align-items: end;
    }}
    .filter-summary {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 12px;
    }}
    .task-group {{
      border: 1px solid var(--line);
      border-radius: 8px;
      margin-top: 10px;
      background: #fff;
      overflow: hidden;
    }}
    .task-group summary {{
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      gap: 8px;
      padding: 10px 12px;
      cursor: pointer;
      background: #f1f4f8;
    }}
    .task-group table {{
      border-top: 1px solid var(--line);
    }}
    .row-actions {{
      display: grid;
      gap: 8px;
      min-width: 220px;
    }}
    .row-action {{
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #f8fafc;
      padding: 6px;
    }}
    .row-action summary {{
      color: #0d5f59;
      cursor: pointer;
      font-weight: 700;
    }}
    .row-action form {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
      padding-top: 8px;
    }}
    .action-preview {{
      margin: 8px 0 0;
      padding-left: 18px;
      color: var(--muted);
      font-size: 12px;
    }}
    .review-package {{
      border-top: 1px solid var(--line);
      padding-top: 16px;
      margin-top: 16px;
    }}
    .review-package:first-of-type {{
      border-top: 0;
      margin-top: 0;
    }}
    .review-package-header {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      justify-content: space-between;
      margin-bottom: 14px;
    }}
    .review-package h3 {{
      margin: 0 0 8px;
      font-size: 16px;
    }}
    .review-package h4 {{
      margin: 0 0 8px;
      font-size: 13px;
    }}
    .review-section {{
      border-top: 1px solid var(--line);
      margin-top: 16px;
      padding-top: 14px;
    }}
    .review-subsection {{
      margin-top: 12px;
    }}
    .review-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
      gap: 10px;
    }}
    .review-field {{
      min-width: 0;
    }}
    .review-field span {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0;
    }}
    .review-field div {{
      overflow-wrap: anywhere;
    }}
    .review-actions {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 12px;
    }}
    .review-action form {{
      display: grid;
      gap: 8px;
    }}
    .action-result-header {{
      display: flex;
      flex-wrap: wrap;
      align-items: flex-start;
      justify-content: space-between;
      gap: 12px;
    }}
    .action-result-header h2 {{
      margin-bottom: 4px;
    }}
    .result-meta {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 10px;
      margin-top: 14px;
    }}
    .result-section {{
      margin-top: 18px;
      padding-top: 14px;
      border-top: 1px solid var(--line);
    }}
    .result-section h3 {{
      margin: 0 0 8px;
      font-size: 14px;
    }}
    .result-steps, .result-files, .result-messages, .result-actions {{
      margin: 0;
      padding-left: 0;
      list-style: none;
    }}
    .result-step {{
      display: grid;
      grid-template-columns: 72px minmax(0, 1fr);
      gap: 10px;
      align-items: start;
      padding: 8px 0;
      border-top: 1px solid #edf1f6;
    }}
    .result-step:first-child {{
      border-top: 0;
    }}
    .result-files li, .result-messages li, .result-actions li {{
      margin: 6px 0;
      overflow-wrap: anywhere;
    }}
    .callout {{
      margin: 0 0 10px;
      padding: 10px 12px;
      border-left: 4px solid var(--accent);
      background: #f4fbf9;
    }}
    .copy-field {{
      margin: 8px 0 10px;
      text-transform: none;
    }}
    .copy-field textarea {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 12px;
    }}
    .result-technical {{
      margin-top: 18px;
      border-top: 1px solid var(--line);
      padding-top: 12px;
    }}
    .result-technical summary {{
      cursor: pointer;
      color: var(--muted);
      font-weight: 700;
    }}
    label {{
      display: grid;
      gap: 4px;
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0;
    }}
    input, select, textarea {{
      width: 100%;
      min-height: 36px;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 6px 8px;
      color: var(--text);
      background: #fff;
      font: inherit;
      text-transform: none;
    }}
    textarea {{
      resize: vertical;
    }}
    .checkline {{
      display: flex;
      gap: 8px;
      align-items: center;
      min-height: 36px;
      color: var(--text);
      text-transform: none;
      letter-spacing: 0;
    }}
    .checkline input {{
      width: auto;
      min-height: auto;
    }}
    .wide-field {{
      grid-column: 1 / -1;
    }}
    button {{
      min-height: 36px;
      border: 1px solid #0d5f59;
      border-radius: 6px;
      padding: 7px 12px;
      background: var(--accent);
      color: #fff;
      font: inherit;
      font-weight: 700;
      cursor: pointer;
    }}
    .button-link {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 32px;
      border: 1px solid #0d5f59;
      border-radius: 6px;
      padding: 5px 10px;
      background: var(--accent);
      color: #fff;
      font-weight: 700;
      text-decoration: none;
    }}
    .button-link.secondary {{
      background: #fff;
      color: #0d5f59;
    }}
    .empty {{
      color: var(--muted);
      margin: 0;
    }}
    @media (max-width: 640px) {{
      .header-inner, main {{ padding-left: 14px; padding-right: 14px; }}
      h1 {{ font-size: 21px; }}
      nav a {{ flex: 1 1 auto; text-align: center; }}
      .metric strong {{ font-size: 18px; }}
      .result-step {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="header-inner">
      <h1>AI Control Center</h1>
      {nav}
    </div>
  </header>
  <main>{body}</main>
</body>
</html>
""".format(
        title=escape(title),
        nav=render_nav(active),
        body=body,
    )


def render_nav(active: str) -> str:
    links = []
    for href, label in NAV_ITEMS:
        class_name = ' class="active"' if href == active else ""
        links.append('<a href="{}"{}>{}</a>'.format(href, class_name, escape(label)))
    return "<nav>{}</nav>".format("".join(links))


def metric(label: str, value: str) -> str:
    return '<div class="metric"><span>{}</span><strong>{}</strong></div>'.format(
        escape(label),
        escape(value),
    )


def doctor_cache_detail(doctor: Mapping[str, Any]) -> str:
    cache = doctor.get("cache") or {}
    if not cache.get("cached"):
        return '<span class="pill">doctor cache: empty</span>'

    state = "stale" if cache.get("stale") else "fresh"
    age = cache.get("age_seconds")
    if isinstance(age, (int, float)):
        age_text = "{:.1f}s old".format(float(age))
    else:
        age_text = "age unknown"
    return '<span class="pill">doctor cache: {}, {}</span>'.format(
        escape(state),
        escape(age_text),
    )


def task_filter_state(
    data: Mapping[str, Any],
    query: Mapping[str, Sequence[str]],
) -> dict[str, Any]:
    group = _query_value(query, "group") or "epic"
    if group not in TASK_GROUP_OPTIONS:
        group = "epic"
    status = _query_value(query, "status")
    return {
        "initiative": _query_value(query, "initiative"),
        "epic": _query_value(query, "epic"),
        "status": status,
        "q": _query_value(query, "q"),
        "group": group,
        "show_done": _query_enabled(query, "show_done") or status == "done",
    }


def task_filter_form(data: Mapping[str, Any], filters: Mapping[str, Any]) -> str:
    initiatives = data.get("initiatives") or []
    epics = data.get("epics") or []
    statuses = sorted(
        {
            str(task.get("status") or "unknown")
            for task in data.get("tasks") or []
            if isinstance(task, Mapping)
        },
        key=status_sort_key,
    )
    initiative_options = [
        ("", "All initiatives"),
        *[
            (
                str(initiative.get("id") or ""),
                "{} - {}".format(
                    initiative.get("id") or "",
                    initiative.get("title") or "",
                ).strip(" -"),
            )
            for initiative in initiatives
            if initiative.get("id")
        ],
    ]
    epic_options = [
        ("", "All epics"),
        *[
            (
                str(epic.get("id") or ""),
                "{} ({}) - {}".format(
                    epic.get("key") or epic.get("id") or "",
                    epic.get("id") or "",
                    epic.get("title") or "",
                ).strip(" -"),
            )
            for epic in epics
            if epic.get("id")
        ],
    ]
    status_options = [("", "All active statuses"), *[(status, status) for status in statuses]]
    group_options = (
        ("epic", "Epic"),
        ("status", "Status"),
        ("none", "None"),
    )
    checked = " checked" if filters.get("show_done") else ""
    return (
        '<form class="task-controls" method="get" action="/tasks">'
        "{}{}{}{}{}"
        '<label class="checkline"><input type="checkbox" name="show_done" value="1"{}>Show done</label>'
        '<button type="submit">Apply</button>'
        '<a class="button-link secondary" href="/tasks">Reset</a>'
        "</form>"
    ).format(
        filter_select(
            "initiative",
            "Initiative",
            initiative_options,
            str(filters.get("initiative") or ""),
        ),
        filter_select("epic", "Epic", epic_options, str(filters.get("epic") or "")),
        filter_select(
            "status",
            "Status",
            status_options,
            str(filters.get("status") or ""),
        ),
        input_field("q", "Search", str(filters.get("q") or ""), required=False),
        filter_select("group", "Group", group_options, str(filters.get("group") or "")),
        checked,
    )


def task_filter_summary(filters: Mapping[str, Any]) -> str:
    pills = []
    if filters.get("initiative"):
        pills.append("initiative {}".format(filters.get("initiative")))
    if filters.get("epic"):
        pills.append("epic {}".format(filters.get("epic")))
    if filters.get("status"):
        pills.append("status {}".format(filters.get("status")))
    if filters.get("q"):
        pills.append('search "{}"'.format(filters.get("q")))
    pills.append("grouped by {}".format(filters.get("group") or "epic"))
    if filters.get("show_done"):
        pills.append("done visible")
    else:
        pills.append("done hidden")
    return '<div class="filter-summary">{}</div>'.format(
        "".join('<span class="pill">{}</span>'.format(escape(pill)) for pill in pills)
    )


def filter_tasks(
    tasks: Sequence[Mapping[str, Any]],
    data: Mapping[str, Any],
    filters: Mapping[str, Any],
) -> list[Mapping[str, Any]]:
    epics_by_id = epics_by_id_map(data)
    selected_initiative = str(filters.get("initiative") or "")
    selected_epic = str(filters.get("epic") or "")
    selected_status = str(filters.get("status") or "")
    search = str(filters.get("q") or "").strip().lower()
    show_done = bool(filters.get("show_done"))
    selected: list[Mapping[str, Any]] = []

    for task in tasks:
        status = str(task.get("status") or "unknown")
        epic_id = str(task.get("epic_id") or "")
        epic = epics_by_id.get(epic_id) or {}
        initiative_id = str(epic.get("initiative_id") or "")

        if selected_initiative and initiative_id != selected_initiative:
            continue
        if selected_epic and epic_id != selected_epic:
            continue
        if selected_status and status != selected_status:
            continue
        if status == "done" and not show_done and not selected_status:
            continue
        if search and search not in task_search_text(task):
            continue
        selected.append(task)

    return selected


def focus_tasks(
    data: Mapping[str, Any],
    tasks: Sequence[Mapping[str, Any]],
) -> list[Mapping[str, Any]]:
    by_id = {str(task.get("id") or ""): task for task in tasks}
    selected: list[Mapping[str, Any]] = []
    seen: set[str] = set()
    current = data.get("current_task") or {}
    current_id = str(current.get("id") or "")
    if current_id in by_id:
        selected.append(by_id[current_id])
        seen.add(current_id)
    for task in tasks:
        task_id = str(task.get("id") or "")
        if task_id not in seen and task.get("status") in TASK_FOCUS_STATUSES:
            selected.append(task)
            seen.add(task_id)
    return selected


def task_select_options(data: Mapping[str, Any]) -> list[tuple[str, str]]:
    options = []
    for task in data.get("tasks") or []:
        if not isinstance(task, Mapping):
            continue
        task_ref = str(task.get("ref") or task.get("id") or "")
        if not task_ref:
            continue
        status = str(task.get("status") or "unknown")
        label = "{} - {} ({})".format(
            task_ref,
            task.get("title") or "",
            status,
        ).strip(" -")
        options.append((task_ref, label))
    return options


def change_filter_state(
    data: Mapping[str, Any],
    query: Mapping[str, Sequence[str]],
) -> dict[str, Any]:
    return {
        "status": _query_value(query, "status"),
        "type": _query_value(query, "type"),
        "q": _query_value(query, "q"),
    }


def change_filter_form(data: Mapping[str, Any], filters: Mapping[str, Any]) -> str:
    statuses = sorted(
        {
            str(change.get("status") or "unknown")
            for change in data.get("changes") or []
            if isinstance(change, Mapping)
        },
        key=status_sort_key,
    )
    types = sorted(
        {
            str(change.get("change_type") or change.get("type") or "unknown")
            for change in data.get("changes") or []
            if isinstance(change, Mapping)
        }
    )
    status_options = [("", "All statuses"), *[(status, status) for status in statuses]]
    type_options = [("", "All types"), *[(item, item) for item in types]]
    return (
        '<form class="task-controls" method="get" action="/evolution">'
        "{}{}{}"
        '<button type="submit">Apply</button>'
        '<a class="button-link secondary" href="/evolution">Reset</a>'
        "</form>"
    ).format(
        filter_select(
            "status",
            "Status",
            status_options,
            str(filters.get("status") or ""),
        ),
        filter_select("type", "Type", type_options, str(filters.get("type") or "")),
        input_field("q", "Search", str(filters.get("q") or ""), required=False),
    )


def change_filter_summary(filters: Mapping[str, Any]) -> str:
    pills = []
    if filters.get("status"):
        pills.append("status {}".format(filters.get("status")))
    if filters.get("type"):
        pills.append("type {}".format(filters.get("type")))
    if filters.get("q"):
        pills.append('search "{}"'.format(filters.get("q")))
    if not pills:
        pills.append("all changes")
    return '<div class="filter-summary">{}</div>'.format(
        "".join('<span class="pill">{}</span>'.format(escape(pill)) for pill in pills)
    )


def filter_changes(
    changes: Sequence[Mapping[str, Any]],
    filters: Mapping[str, Any],
) -> list[Mapping[str, Any]]:
    selected_status = str(filters.get("status") or "")
    selected_type = str(filters.get("type") or "")
    search = str(filters.get("q") or "").strip().lower()
    selected = []
    for change in changes:
        status = str(change.get("status") or "unknown")
        change_type = str(change.get("change_type") or change.get("type") or "unknown")
        if selected_status and status != selected_status:
            continue
        if selected_type and change_type != selected_type:
            continue
        if search and search not in change_search_text(change):
            continue
        selected.append(change)
    return selected


def change_search_text(change: Mapping[str, Any]) -> str:
    values = [
        change.get("id"),
        change.get("title"),
        change.get("status"),
        change.get("change_type"),
        change.get("problem"),
        change.get("proposal"),
    ]
    for field in ("linked_tasks", "affected_files", "risks", "impact"):
        value = change.get(field)
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            values.extend(value)
    return " ".join(str(value or "") for value in values).lower()


def change_table(
    changes: Sequence[Mapping[str, Any]],
    data: Mapping[str, Any],
    *,
    empty_text: str,
) -> str:
    rows = []
    for change in changes:
        cells = [
            change_identity_cell(change),
            status_badge(str(change.get("status") or "unknown")),
            escape(change.get("change_type") or change.get("type") or ""),
            escape(change.get("title", "")),
            change_list_cell(change.get("linked_tasks")),
            change_list_cell(change.get("affected_files")),
            change_list_cell(change.get("risks")),
            change_approval_cell(change),
            change_acceptance_cell(change),
            pipeline_hint_cell(change),
            change_row_actions(change, data),
        ]
        rows.append(
            "<tr>{}</tr>".format(
                "".join("<td>{}</td>".format(cell) for cell in cells)
            )
        )
    return table(
        (
            "Change",
            "Status",
            "Type",
            "Title",
            "Linked Tasks",
            "Affected Files",
            "Risks",
            "Approval",
            "Acceptance",
            "Next / Blockers",
            "Actions",
        ),
        rows,
        empty_text,
    )


def change_identity_cell(change: Mapping[str, Any]) -> str:
    return "<strong>{}</strong>".format(escape(change.get("id") or ""))


def change_list_cell(value: Any, *, limit: int = 3) -> str:
    items = _string_items(value)
    if not items:
        return '<span class="muted">none</span>'
    visible = items[:limit]
    remainder = len(items) - len(visible)
    html_items = "".join("<li>{}</li>".format(escape(item)) for item in visible)
    if remainder > 0:
        html_items += "<li>+{} more</li>".format(escape(remainder))
    return '<ul class="compact-list">{}</ul>'.format(html_items)


def change_approval_cell(change: Mapping[str, Any]) -> str:
    approved_by = str(change.get("owner_approved_by") or "")
    approved_at = str(change.get("owner_approved_at") or "")
    if approved_by or approved_at:
        return "{}<br>{}".format(escape(approved_by or "approved"), escape(approved_at))
    return '<span class="muted">not approved</span>'


def change_acceptance_cell(change: Mapping[str, Any]) -> str:
    accepted_by = str(change.get("accepted_by") or "")
    accepted_at = str(change.get("accepted_at") or "")
    if accepted_by or accepted_at:
        return "{}<br>{}".format(escape(accepted_by or "accepted"), escape(accepted_at))
    return '<span class="muted">not accepted</span>'


def change_row_actions(change: Mapping[str, Any], data: Mapping[str, Any]) -> str:
    specs = change_row_action_specs(change)
    if not specs:
        return '<span class="pill">No change actions</span>'
    return '<div class="row-actions">{}</div>'.format(
        "".join(change_row_action(change, data, spec) for spec in specs)
    )


def change_row_action_specs(change: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    status = str(change.get("status") or "")
    if status not in CHANGE_ACTION_STATUSES:
        return []
    specs: list[Mapping[str, Any]] = []
    if status == "ready":
        spec = {
            "action": "evolution.approve_change",
            "label": "Approve Change",
            "notes_label": "Approval Notes",
            "notes_placeholder": "Record the Human Owner approval basis.",
        }
        if entity_action_available(change, spec["action"]) is not False:
            specs.append(spec)
    if status in {"approved", "in_progress"}:
        spec = {
            "action": "evolution.move_to_review",
            "label": "Move to Review",
        }
        if entity_action_available(change, spec["action"]) is not False:
            specs.append(spec)
    if status in {"approved", "in_review"}:
        spec = {
            "action": "evolution.accept_change",
            "label": "Accept Change",
            "notes_label": "Acceptance Notes",
            "notes_placeholder": "Record Human Owner acceptance after linked tasks are complete.",
        }
        if entity_action_available(change, spec["action"]) is not False:
            specs.append(spec)
    return specs


def change_row_action(
    change: Mapping[str, Any],
    data: Mapping[str, Any],
    spec: Mapping[str, Any],
) -> str:
    action_id = str(spec.get("action") or "")
    label = str(spec.get("label") or action_id)
    workflow = workflow_by_name(data).get(action_id) or {}
    change_id = str(change.get("id") or "")
    fields = [hidden_field("change", change_id)]
    notes_label = str(spec.get("notes_label") or "")
    if notes_label:
        fields.append(
            textarea_field(
                "notes",
                notes_label,
                rows=2,
                placeholder=str(spec.get("notes_placeholder") or ""),
                required=True,
            )
        )
    return (
        '<details class="row-action row-action-{}">'
        "<summary>{}</summary>"
        "{}"
        "{}"
        "</details>"
    ).format(
        escape(css_token(action_id)),
        escape(label),
        workflow_preview_html(workflow),
        action_form(
            action_id,
            fields,
            button_label=label,
        ),
    )


def task_grouped_table(
    tasks: Sequence[Mapping[str, Any]],
    data: Mapping[str, Any],
    filters: Mapping[str, Any],
    *,
    empty_text: str,
) -> str:
    if not tasks:
        return '<p class="empty">{}</p>'.format(escape(empty_text))
    group_by = str(filters.get("group") or "epic")
    if group_by == "none":
        return task_table(
            tasks,
            empty_text=empty_text,
            data=data,
            include_actions=True,
        )

    epics_by_id = epics_by_id_map(data)
    groups: dict[str, list[Mapping[str, Any]]] = {}
    for task in tasks:
        if group_by == "status":
            key = str(task.get("status") or "unknown")
        else:
            key = str(task.get("epic_id") or "unassigned")
        groups.setdefault(key, []).append(task)

    if group_by == "status":
        ordered_keys = sorted(groups, key=status_sort_key)
    else:
        ordered_keys = sorted(groups, key=lambda key: epic_group_sort_key(key, epics_by_id))

    sections = []
    for key in ordered_keys:
        items = groups[key]
        label = (
            key
            if group_by == "status"
            else epic_group_label(key, epics_by_id)
        )
        collapsed = group_by == "status" and key == "done"
        open_attr = "" if collapsed else " open"
        sections.append(
            '<details class="task-group task-group-{}"{}>'
            "<summary><strong>{}</strong><span>{} tasks</span></summary>"
            "{}"
            "</details>".format(
                escape(css_token(key)),
                open_attr,
                escape(label),
                escape(len(items)),
                task_table(
                    items,
                    empty_text=empty_text,
                    data=data,
                    include_actions=True,
                ),
            )
        )
    return "".join(sections)


def epics_by_id_map(data: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {
        str(epic.get("id") or ""): epic
        for epic in data.get("epics") or []
        if isinstance(epic, Mapping) and epic.get("id")
    }


def epic_group_label(key: str, epics_by_id: Mapping[str, Mapping[str, Any]]) -> str:
    epic = epics_by_id.get(key) or {}
    if not epic:
        return key or "Unassigned"
    label = str(epic.get("key") or key)
    if label != key:
        label = "{} ({})".format(label, key)
    title = str(epic.get("title") or "")
    return "{} - {}".format(label, title).strip(" -")


def epic_group_sort_key(
    key: str,
    epics_by_id: Mapping[str, Mapping[str, Any]],
) -> tuple[str, int, str]:
    epic = epics_by_id.get(key) or {}
    return (
        str(epic.get("initiative_id") or ""),
        int(epic.get("order") or 0),
        key,
    )


def task_search_text(task: Mapping[str, Any]) -> str:
    values = [
        task.get("id"),
        task.get("ref"),
        task.get("legacy_id"),
        task.get("title"),
        task.get("summary"),
    ]
    aliases = task.get("aliases")
    if isinstance(aliases, Sequence) and not isinstance(aliases, (str, bytes)):
        values.extend(aliases)
    return " ".join(str(value or "") for value in values).lower()


def status_sort_key(status: str) -> tuple[int, str]:
    order = {
        "in_progress": 0,
        "in_review": 1,
        "changes_requested": 2,
        "ready": 3,
        "blocked": 4,
        "planned": 5,
        "proposed": 6,
        "deferred": 7,
        "done": 8,
    }
    return (order.get(status, 50), status)


def css_token(value: str) -> str:
    return "".join(
        char.lower() if char.isalnum() else "-"
        for char in str(value or "unknown")
    ).strip("-") or "unknown"


def task_label(task: Mapping[str, Any]) -> str:
    if not task:
        return "None"
    return "{} {}".format(task.get("ref") or task.get("id"), task.get("status", "")).strip()


def task_detail(task: Mapping[str, Any]) -> str:
    if not task:
        return '<p class="empty">No current task.</p>'
    return (
        '<div class="status-row">{}<strong>{}</strong><span>{}</span></div>'
        "<p>{}</p>"
        "{}"
    ).format(
        status_badge(str(task.get("status") or "unknown")),
        escape(task.get("ref") or task.get("id") or ""),
        escape(task.get("title") or ""),
        escape(task.get("summary") or task.get("description") or ""),
        pipeline_hint_cell(task),
    )


def task_table(
    tasks: Sequence[Mapping[str, Any]],
    *,
    empty_text: str,
    data: Mapping[str, Any] | None = None,
    include_actions: bool = False,
) -> str:
    rows = []
    for task in tasks:
        cells = [
            task_identity_cell(task),
            status_badge(str(task.get("status") or "unknown")),
            escape(task.get("epic_key") or task.get("epic_id") or ""),
            escape(task.get("title", "")),
            escape(task.get("summary", "")),
            escape(task.get("active_stage", "")),
            pipeline_hint_cell(task),
        ]
        if include_actions:
            cells.append(task_row_actions(task, data or {}))
        rows.append(
            "<tr>{}</tr>".format(
                "".join("<td>{}</td>".format(cell) for cell in cells)
            )
        )
    headers = ["Task", "Status", "Epic", "Title", "Summary", "Stage", "Next / Blockers"]
    if include_actions:
        headers.append("Actions")
    return table(tuple(headers), rows, empty_text)


def task_identity_cell(task: Mapping[str, Any]) -> str:
    primary = str(task.get("ref") or task.get("id") or "")
    legacy = str(task.get("legacy_id") or task.get("id") or "")
    if legacy and legacy != primary:
        return '<strong>{}</strong><br><code>{}</code>'.format(
            escape(primary),
            escape(legacy),
        )
    return "<strong>{}</strong>".format(escape(primary))


def task_row_actions(task: Mapping[str, Any], data: Mapping[str, Any]) -> str:
    specs = task_row_action_specs(task, data)
    if not specs:
        return '<span class="pill">No row workflows</span>'
    return '<div class="row-actions">{}</div>'.format(
        "".join(task_row_action(task, data, spec) for spec in specs)
    )


def task_row_action_specs(
    task: Mapping[str, Any],
    data: Mapping[str, Any],
) -> list[Mapping[str, Any]]:
    status = str(task.get("status") or "")
    current = data.get("current_task") or {}
    is_current = bool(task.get("id") and task.get("id") == current.get("id"))
    specs = []
    for spec in TASK_ROW_WORKFLOWS:
        statuses = spec.get("statuses") or set()
        if status in statuses or (spec.get("current") and is_current):
            if entity_action_available(task, str(spec.get("action") or "")) is False:
                continue
            specs.append(spec)
    return specs


def task_row_action(
    task: Mapping[str, Any],
    data: Mapping[str, Any],
    spec: Mapping[str, Any],
) -> str:
    action_id = str(spec.get("action") or "")
    label = str(spec.get("label") or action_id)
    workflow = workflow_by_name(data).get(action_id) or {}
    task_ref = str(task.get("ref") or task.get("id") or "")
    fields = [hidden_field("task", task_ref)]
    notes_label = str(spec.get("notes_label") or "")
    if notes_label:
        fields.append(
            textarea_field(
                "notes",
                notes_label,
                rows=2,
                placeholder=str(spec.get("notes_placeholder") or ""),
                required=True,
            )
        )
    return (
        '<details class="row-action row-action-{}">'
        "<summary>{}</summary>"
        "{}"
        "{}"
        "</details>"
    ).format(
        escape(css_token(action_id)),
        escape(label),
        workflow_preview_html(workflow),
        action_form(
            action_id,
            fields,
            button_label=label,
        ),
    )


def workflow_by_name(data: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {
        str(workflow.get("name") or ""): workflow
        for workflow in data.get("workflows") or []
        if isinstance(workflow, Mapping)
    }


def workflow_preview_html(workflow: Mapping[str, Any]) -> str:
    steps = [
        str(step.get("title") or step.get("id") or "")
        for step in workflow.get("steps") or []
        if isinstance(step, Mapping) and (step.get("title") or step.get("id"))
    ]
    if not steps:
        return ""
    return '<ol class="action-preview">{}</ol>'.format(
        "".join("<li>{}</li>".format(escape(step)) for step in steps)
    )


def pipeline_hint_cell(item: Mapping[str, Any]) -> str:
    hints = _mapping(item.get("pipeline_hints"))
    next_actions = _string_items(hints.get("next_actions"))
    blocked_reasons = _string_items(hints.get("blocked_reasons"))
    linked_changes = [
        change
        for change in hints.get("linked_changes") or []
        if isinstance(change, Mapping)
    ]
    if not next_actions and not blocked_reasons and not linked_changes:
        return '<span class="muted">No next action hints</span>'

    parts = ['<div class="pipeline-hints">']
    if next_actions:
        parts.append(
            '<div class="hint-next"><strong>Next:</strong> {}</div>'.format(
                escape(", ".join(next_actions))
            )
        )
    if linked_changes:
        change_bits = []
        for change in linked_changes:
            change_id = str(change.get("id") or "")
            status = str(change.get("status") or "unknown")
            change_bits.append("{} {}".format(change_id, status).strip())
        parts.append(
            '<div class="hint-change"><strong>Linked Change:</strong> {}</div>'.format(
                escape(", ".join(change_bits))
            )
        )
    context = _mapping(hints.get("context"))
    context_reason = str(context.get("reason") or "")
    if context_reason and "Refresh Context" in next_actions:
        parts.append(
            '<div class="hint-change"><strong>Context:</strong> {}</div>'.format(
                escape(context_reason)
            )
        )
    if blocked_reasons:
        parts.append(
            '<ul class="hint-list">{}</ul>'.format(
                "".join("<li>{}</li>".format(escape(reason)) for reason in blocked_reasons)
            )
        )
    parts.append("</div>")
    return "".join(parts)


def entity_action_available(item: Mapping[str, Any], action_id: str) -> bool | None:
    hints = _mapping(item.get("pipeline_hints"))
    actions = hints.get("actions")
    if not isinstance(actions, Sequence) or isinstance(actions, (str, bytes)):
        return None
    for action in actions:
        if isinstance(action, Mapping) and str(action.get("action") or "") == action_id:
            return bool(action.get("available"))
    return None


def table(headers: Sequence[str], rows: Sequence[str], empty_text: str) -> str:
    if not rows:
        return '<p class="empty">{}</p>'.format(escape(empty_text))
    head = "".join("<th>{}</th>".format(escape(header)) for header in headers)
    return "<table><thead><tr>{}</tr></thead><tbody>{}</tbody></table>".format(
        head,
        "".join(rows),
    )


def status_badge(value: str) -> str:
    safe = str(value or "unknown")
    class_name = safe.lower().replace(" ", "_")
    return '<span class="badge {}">{}</span>'.format(
        escape(class_name),
        escape(safe),
    )


def _query_enabled(query: Mapping[str, Sequence[str]], name: str) -> bool:
    values = query.get(name) or ()
    return any(
        str(value).lower() in {"1", "true", "yes", "refresh"} for value in values
    )


def _query_value(query: Mapping[str, Sequence[str]], name: str) -> str:
    values = query.get(name) or ()
    for value in values:
        text = str(value).strip()
        if text:
            return text
    return ""


def action_form(
    action_id: str,
    fields: Sequence[str],
    *,
    confirm_required: bool = True,
    button_label: str | None = None,
) -> str:
    confirm_required_attr = " required" if confirm_required else ""
    controls = [
        '<input type="hidden" name="action" value="{}">'.format(escape(action_id)),
        *fields,
        '<label class="checkline"><input type="checkbox" name="confirm" value="yes"{}>Confirm</label>'.format(
            confirm_required_attr
        ),
        "<button type=\"submit\">{}</button>".format(
            escape(button_label or action_id)
        ),
    ]
    return '<form method="post" action="/actions">{}</form>'.format("".join(controls))


def hidden_field(name: str, value: str) -> str:
    return '<input type="hidden" name="{}" value="{}">'.format(
        escape(name),
        escape(value),
    )


def input_field(name: str, label: str, value: str = "", *, required: bool = True) -> str:
    required_attr = " required" if required else ""
    return '<label>{}<input name="{}" value="{}"{}></label>'.format(
        escape(label),
        escape(name),
        escape(value),
        required_attr,
    )


def select_field(name: str, label: str, options: Sequence[str]) -> str:
    choices = "".join(
        '<option value="{0}">{0}</option>'.format(escape(option)) for option in options
    )
    return '<label>{}<select name="{}">{}</select></label>'.format(
        escape(label),
        escape(name),
        choices,
    )


def select_field_values(
    name: str,
    label: str,
    options: Sequence[tuple[str, str]],
) -> str:
    choices = "".join(
        '<option value="{}">{}</option>'.format(escape(value), escape(text))
        for value, text in options
    )
    return '<label>{}<select name="{}">{}</select></label>'.format(
        escape(label),
        escape(name),
        choices,
    )


def filter_select(
    name: str,
    label: str,
    options: Sequence[tuple[str, str]],
    selected: str,
) -> str:
    choices = []
    for value, text in options:
        selected_attr = ' selected' if value == selected else ""
        choices.append(
            '<option value="{}"{}>{}</option>'.format(
                escape(value),
                selected_attr,
                escape(text),
            )
        )
    return '<label>{}<select name="{}">{}</select></label>'.format(
        escape(label),
        escape(name),
        "".join(choices),
    )


def textarea_field(
    name: str,
    label: str,
    *,
    rows: int = 3,
    placeholder: str = "",
    wide: bool = False,
    required: bool = False,
) -> str:
    placeholder_attr = (
        ' placeholder="{}"'.format(escape(placeholder)) if placeholder else ""
    )
    class_attr = ' class="wide-field"' if wide else ""
    required_attr = " required" if required else ""
    return '<label{}>{}<textarea name="{}" rows="{}"{}{}></textarea></label>'.format(
        class_attr,
        escape(label),
        escape(name),
        escape(rows),
        placeholder_attr,
        required_attr,
    )


def checkbox_field(name: str, label: str) -> str:
    return '<label class="checkline"><input type="checkbox" name="{}" value="yes">{}</label>'.format(
        escape(name),
        escape(label),
    )


def escape(value: Any) -> str:
    return html.escape(str(value), quote=True)


def _require_loopback_host(host: str) -> None:
    if host in LOCAL_HOSTS or host in LOCAL_ADDRESSES:
        return
    try:
        address = ipaddress.ip_address(host)
    except ValueError as exc:
        raise WebServerError(
            "WEB_NON_LOCAL_HOST",
            "Web Control Center host must be loopback-only.",
            details={"host": host},
        ) from exc
    if not address.is_loopback:
        raise WebServerError(
            "WEB_NON_LOCAL_HOST",
            "Web Control Center host must be loopback-only.",
            details={"host": host},
        )
