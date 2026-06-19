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
    ("/epics", "Epics"),
    ("/reviews", "Reviews"),
    ("/events", "Events"),
    ("/generated", "Generated"),
    ("/doctor", "Doctor"),
    ("/commands", "Commands"),
    ("/actions", "Actions"),
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
            self.send_header("Content-Type", "application/json; charset=utf-8")
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
        "/tasks": lambda: render_tasks(model.dashboard()),
        "/epics": lambda: render_epics(model.dashboard()),
        "/reviews": lambda: render_reviews(model.dashboard()),
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
    body = [
        '<section class="summary-grid">',
        metric("Doctor", str(doctor.get("overall_status") or "UNKNOWN")),
        metric("Current Task", task_label(current)),
        metric("Queue", "{} executable".format(len(queue))),
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


def render_tasks(data: Mapping[str, Any]) -> str:
    counts = data.get("task_counts") or {}
    body = [
        '<section class="summary-grid">',
        *[metric(str(status), str(count)) for status, count in sorted(counts.items())],
        "</section>",
        '<section class="panel">',
        "<h2>Tasks</h2>",
        task_table(data.get("tasks") or [], empty_text="No tasks."),
        "</section>",
    ]
    return render_page("Tasks", "".join(body), active="/tasks")


def render_epics(data: Mapping[str, Any]) -> str:
    rows = []
    for epic in data.get("epics") or []:
        rows.append(
            "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                escape(epic.get("key") or epic.get("id")),
                status_badge(str(epic.get("status") or "unknown")),
                escape(epic.get("initiative_id", "")),
                escape(epic.get("title", "")),
            )
        )
    body = [
        '<section class="panel">',
        "<h2>Epics</h2>",
        table(("Epic", "Status", "Initiative", "Title"), rows, "No epics."),
        "</section>",
    ]
    return render_page("Epics", "".join(body), active="/epics")


def render_reviews(data: Mapping[str, Any]) -> str:
    review_commands = data.get("review_commands") or []
    in_review = [
        task for task in data.get("tasks") or [] if task.get("status") == "in_review"
    ]
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
        "<h2>Tasks In Review</h2>",
        task_table(in_review, empty_text="No tasks are currently in review."),
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
            "evolution.create_for_task",
            [input_field("task", "Task", default_task)],
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
    return json.dumps(result.to_dict(), ensure_ascii=False, indent=2, sort_keys=True)


def render_action_error(error: WebActionError) -> str:
    return json.dumps(
        {
            "ok": False,
            "error": {
                "code": error.code,
                "message": error.message,
                "details": error.details,
            },
        },
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )


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
      min-width: 720px;
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
    .badge.pass, .badge.ready, .badge.in_progress, .badge.implemented, .badge.read, .badge.validation {{
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
      min-height: 32px;
      border: 1px solid #0d5f59;
      border-radius: 6px;
      padding: 5px 10px;
      background: var(--accent);
      color: #fff;
      font-weight: 700;
      text-decoration: none;
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
    ).format(
        status_badge(str(task.get("status") or "unknown")),
        escape(task.get("ref") or task.get("id") or ""),
        escape(task.get("title") or ""),
        escape(task.get("summary") or task.get("description") or ""),
    )


def task_table(
    tasks: Sequence[Mapping[str, Any]],
    *,
    empty_text: str,
) -> str:
    rows = []
    for task in tasks:
        rows.append(
            "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                escape(task.get("ref") or task.get("id")),
                status_badge(str(task.get("status") or "unknown")),
                escape(task.get("epic_key") or task.get("epic_id") or ""),
                escape(task.get("title", "")),
                escape(task.get("active_stage", "")),
            )
        )
    return table(("Task", "Status", "Epic", "Title", "Stage"), rows, empty_text)


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


def textarea_field(
    name: str,
    label: str,
    *,
    rows: int = 3,
    placeholder: str = "",
    wide: bool = False,
) -> str:
    placeholder_attr = (
        ' placeholder="{}"'.format(escape(placeholder)) if placeholder else ""
    )
    class_attr = ' class="wide-field"' if wide else ""
    return '<label{}>{}<textarea name="{}" rows="{}"{}></textarea></label>'.format(
        class_attr,
        escape(label),
        escape(name),
        escape(rows),
        placeholder_attr,
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
