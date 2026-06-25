"""Standard-library loopback HTTP server for the Web Control Center."""

from __future__ import annotations

import html
import ipaddress
import json
from datetime import datetime, timezone
from email.parser import BytesParser
from email.policy import default as email_policy
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence
from urllib.parse import parse_qs, unquote, urlparse

from ai_project_ctl.core.result import CommandError
from ai_project_ctl.core.workflows import BULK_IMPORT_MAX_BYTES
from ai_project_ctl.web.actions import (
    WebActionError,
    WebActionExecutor,
    WebActionResult,
    available_actions,
)
from ai_project_ctl.web.read_model import ReadOnlyProjectModel
from ai_project_ctl.ui_settings import (
    INTERNAL_CHANGE_GATE_BYPASS_SETTING,
    REQUIRE_CODEX_REVIEW_SETTING,
    load_ui_settings,
    ui_settings_path,
    ui_settings_source,
)


LOCAL_HOSTS = {"localhost"}
LOCAL_ADDRESSES = {"127.0.0.1", "::1"}
WEB_IMPORT_FILE_FIELD = "import_file"
WEB_IMPORT_ALLOWED_SUFFIXES = {".json", ".txt"}
WEB_IMPORT_FILE_MAX_BYTES = BULK_IMPORT_MAX_BYTES
WEB_ACTION_BODY_MAX_BYTES = WEB_IMPORT_FILE_MAX_BYTES + 16_384

NAV_ITEMS = (
    ("/", "Dashboard"),
    ("/pipeline", "Pipeline"),
    ("/settings", "Settings"),
    ("/tasks", "Tasks"),
    ("/evolution", "Evolution"),
    ("/epics", "Epics"),
    ("/reviews", "Reviews"),
    ("/commit", "Commit"),
    ("/events", "Events"),
    ("/generated", "Generated"),
    ("/doctor", "Doctor"),
    ("/commands", "Commands"),
    ("/actions", "Actions"),
)

TASK_FOCUS_STATUSES = {"ready", "in_progress", "in_review", "changes_requested"}
TASK_GROUP_OPTIONS = {"none", "epic", "status"}
CHANGE_ACTION_STATUSES = {"ready", "approved", "in_progress", "in_review"}
TASK_REPAIR_STATUSES = {"ready", "in_progress", "in_review", "changes_requested"}
PIPELINE_RUNNABLE_STATUSES = {"planned", "running"}
PIPELINE_STOPPABLE_STATUSES = {"planned", "running"}
PIPELINE_RESUMABLE_STATUSES = {"stopped", "blocked"}
PIPELINE_FLOW_GATES = (
    ("queue_planner", "Queue"),
    ("evolution_change_gate", "Change"),
    ("task_prepare_for_codex", "Prepare"),
    ("token_budget_gate", "Token Gate"),
    ("codex_execution_adapter", "Codex Execute"),
    ("codex_report_gate", "Report"),
    ("machine_review_gate", "Machine Review"),
    ("codex_review_gate", "Codex Review"),
    ("review_close_gate", "Done / Rework"),
    ("commit_gate", "Commit"),
)
PIPELINE_RAW_DEBUG_LIMIT = 12_000
PIPELINE_LOG_SNIPPET_LIMIT = 2_000
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
TASK_ROW_RUN_STATUSES = {"planned", "ready", "changes_requested"}
TASK_ROW_INACTIVE_STATUSES = {"done", "archived", "deferred"}
TASK_ROW_APPROVED_CHANGE_STATUSES = {"approved", "in_review", "accepted"}
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
            if length > WEB_ACTION_BODY_MAX_BYTES:
                raise WebActionError(
                    "WEB_ACTION_BODY_TOO_LARGE",
                    "Write request body is too large.",
                    details={
                        "max_bytes": WEB_ACTION_BODY_MAX_BYTES,
                        "content_length": length,
                    },
                )

            raw_bytes = self.rfile.read(length) if length else b""
            content_type = self.headers.get("Content-Type", "")
            if "multipart/form-data" in content_type:
                return parse_multipart_action_fields(content_type, raw_bytes)

            raw = raw_bytes.decode("utf-8") if raw_bytes else ""
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
    if path.startswith("/pipeline/sessions/"):
        session_id = unquote(path.removeprefix("/pipeline/sessions/")).strip("/")
        detail = model.pipeline_session_detail(session_id)
        if not detail.get("found"):
            return HTTPStatus.NOT_FOUND, "text/html; charset=utf-8", render_pipeline_session_detail(
                detail
            )
        return HTTPStatus.OK, "text/html; charset=utf-8", render_pipeline_session_detail(
            detail
        )

    pages: dict[str, Callable[[], str]] = {
        "/": lambda: render_dashboard(model.dashboard()),
        "/pipeline": lambda: render_pipeline(
            model.dashboard(
                include_events=True,
                pipeline_options=pipeline_query_options(query),
            ),
            query=query,
        ),
        "/settings": lambda: render_settings(model),
        "/tasks": lambda: render_tasks(model.dashboard(), query=query),
        "/evolution": lambda: render_evolution(model.dashboard(), query=query),
        "/epics": lambda: render_epics(model.dashboard()),
        "/reviews": lambda: render_reviews(model.dashboard(), query=query),
        "/commit": lambda: render_commit_readiness(
            model.commit_readiness(refresh_doctor=refresh_doctor)
        ),
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
        project_health_panel(data),
        '<section class="panel">',
        "<h2>Current Task</h2>",
        task_detail(current),
        "</section>",
        '<section class="panel execution-panel">',
        "<h2>Current Execution</h2>",
        execution_status_panel(data),
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


def render_pipeline(
    data: Mapping[str, Any],
    *,
    query: Mapping[str, Sequence[str]] | None = None,
) -> str:
    pipeline = _mapping(data.get("pipeline"))
    state = _mapping(pipeline.get("state"))
    selected_policy = _mapping(pipeline.get("selected_policy"))
    queue_preview = _mapping(pipeline.get("queue_preview"))
    categories = _mapping(queue_preview.get("categories"))
    current_session = _mapping(pipeline.get("current_session"))
    next_task = _mapping(queue_preview.get("next_task"))
    body = [
        '<section class="summary-grid">',
        metric("Current Session", str(state.get("current_session_id") or "none")),
        metric("Policy", str(selected_policy.get("name") or "unknown")),
        metric("Queue", "{} executable".format(len(categories.get("executable") or []))),
        metric("Current Step", str(current_session.get("current_step") or "none")),
        metric("Current Phase", pipeline_session_current_phase(current_session) or "none"),
        metric("Phase Status", pipeline_session_current_phase_status(current_session) or "none"),
        metric("Stop Reason", pipeline_session_stop_reason(current_session) or "none"),
        metric("Next Action", pipeline_session_next_action(current_session) or "none"),
        "</section>",
    ]
    unknown_policy = str(pipeline.get("unknown_policy") or "")
    if unknown_policy:
        body.append(
            '<section class="panel"><p class="callout">Unknown policy {}; showing dry_run.</p></section>'.format(
                escape(unknown_policy)
            )
        )
    body.extend(
        [
            '<section class="panel">',
            "<h2>Pipeline Queue Selector</h2>",
            pipeline_selector_form(data, pipeline),
            "</section>",
            '<section class="panel">',
            "<h2>Policy Preset Preview</h2>",
            pipeline_policy_preview(selected_policy),
            "</section>",
            '<section class="panel">',
            "<h2>Queue Preview</h2>",
            '<div class="status-row">',
            status_badge("next"),
            "<span>{}</span>".format(
                escape(_pipeline_task_label(next_task) if next_task else "No next task")
            ),
            "</div>",
            pipeline_queue_preview_table(queue_preview, _mapping(pipeline.get("queue_error"))),
            "</section>",
            pipeline_current_session_panel(data, pipeline),
            '<section class="panel">',
            "<h2>Sessions</h2>",
            pipeline_session_table(pipeline.get("sessions") or []),
            "</section>",
            '<section class="panel">',
            "<h2>Latest Pipeline Audit</h2>",
            pipeline_audit_table(pipeline.get("audit") or []),
            "</section>",
        ]
    )
    return render_page("Pipeline", "".join(body), active="/pipeline")


def render_pipeline_session_detail(data: Mapping[str, Any]) -> str:
    session = _mapping(data.get("session"))
    session_id = str(data.get("session_id") or session.get("id") or "")
    if not session:
        body = (
            '<section class="panel">'
            "<h2>Pipeline Session Not Found</h2>"
            '<p class="empty">No persistent pipeline session exists for <code>{}</code>.</p>'
            '<p><a class="button-link secondary" href="/pipeline">Back to Pipeline</a></p>'
            "</section>"
        ).format(escape(session_id or "unknown"))
        return render_page("Pipeline Session", body, active="/pipeline")

    status = str(session.get("status") or "unknown")
    current_task = pipeline_session_task_label(data)
    auto_refresh = "active / 2 seconds" if status == "running" else "stopped"
    body = [
        '<section class="summary-grid">',
        metric("Session", str(session.get("id") or "")),
        metric("Status", status),
        metric("Policy", str(session.get("policy") or "unknown")),
        metric("Current Task", current_task or "none"),
        metric("Current Step", str(session.get("current_step") or "none")),
        metric("Current Phase", pipeline_session_current_phase(session) or "none"),
        metric("Phase Status", pipeline_session_current_phase_status(session) or "none"),
        metric("Stop Reason", pipeline_session_stop_reason(session) or "none"),
        metric("Next Action", pipeline_session_next_action(session) or "none"),
        metric("Started", str(session.get("started_at") or "not started")),
        metric("Updated", str(session.get("updated_at") or "")),
        metric("Finished", str(session.get("finished_at") or "not finished")),
        metric("Elapsed", pipeline_elapsed_label(session)),
        metric("Auto-refresh", auto_refresh),
        "</section>",
        pipeline_session_auto_refresh(session),
        '<section class="panel">',
        "<h2>Status Overview</h2>",
        pipeline_status_overview(session),
        "</section>",
        '<section class="panel">',
        "<h2>Current Live Step</h2>",
        pipeline_live_step_panel(session),
        "</section>",
        '<section class="panel action-panel pipeline-session-actions">',
        "<h2>Actions</h2>",
        pipeline_session_action_controls(data),
        "</section>",
        '<section class="panel">',
        "<h2>Steps</h2>",
        pipeline_step_details(session),
        "</section>",
        '<section class="panel">',
        "<h2>Artifacts</h2>",
        pipeline_artifacts_panel(data),
        "</section>",
        '<section class="panel">',
        "<h2>Queue Snapshot</h2>",
        pipeline_queue_snapshot_panel(session),
        "</section>",
        '<section class="panel">',
        "<h2>Audit Events</h2>",
        pipeline_audit_table(data.get("audit") or []),
        "</section>",
        '<section class="panel">',
        "<h2>Files Changed During Session</h2>",
        pipeline_files_changed_panel(data),
        "</section>",
        '<section class="panel">',
        "<h2>Problems / Blockers</h2>",
        pipeline_blockers_panel(data),
        "</section>",
        '<section class="panel">',
        "<h2>Raw Debug</h2>",
        pipeline_raw_debug_panel(session),
        "</section>",
    ]
    return render_page(
        "Pipeline Session {}".format(session.get("id") or ""),
        "".join(body),
        active="/pipeline",
    )


def pipeline_session_auto_refresh(session: Mapping[str, Any]) -> str:
    status = str(session.get("status") or "unknown")
    if status == "running":
        return (
            '<section class="panel auto-refresh" data-auto-refresh="2" '
            'data-session-status="running">'
            '<div class="status-row">{}<strong>Auto-refresh active</strong>'
            "<span>Polling this session every 2 seconds.</span></div>"
            "<script>setTimeout(function(){{window.location.reload();}}, 2000);</script>"
            "</section>"
        ).format(status_badge(status))
    return (
        '<section class="panel auto-refresh stopped" data-session-status="{}">'
        '<div class="status-row">{}<strong>Auto-refresh stopped</strong>'
        "<span>Session state is terminal or waiting for owner action.</span></div>"
        "</section>"
    ).format(escape(status), status_badge(status))


def pipeline_status_overview(session: Mapping[str, Any]) -> str:
    phase_rows = pipeline_session_phase_rows(session)
    if phase_rows:
        return pipeline_phase_status_overview(phase_rows)

    step = pipeline_latest_step(session)
    flow = pipeline_gate_flow(step)
    completed = sum(1 for item in flow if str(item.get("status")) != "planned")
    percent = int((completed / len(flow)) * 100) if flow else 0
    rows = []
    for item in flow:
        rows.append(
            "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                escape(item.get("label") or ""),
                status_badge(str(item.get("status") or "planned")),
                escape(item.get("recorded_at") or ""),
                escape(item.get("detail") or ""),
            )
        )
    return (
        '<div class="pipeline-progress" aria-label="Pipeline progress">'
        '<span style="width: {}%"></span></div>'
        '<p class="muted">{} of {} flow checkpoints have recorded outcomes.</p>'
        "{}"
    ).format(
        escape(percent),
        escape(completed),
        escape(len(flow)),
        table(("Checkpoint", "Status", "Recorded", "Detail"), rows, "No flow checkpoints."),
    )


def pipeline_phase_status_overview(phase_rows: Sequence[Mapping[str, Any]]) -> str:
    completed = len(phase_rows)
    total = 7
    percent = min(100, int((completed / total) * 100)) if total else 0
    return (
        '<div class="pipeline-progress" aria-label="Pipeline phase progress">'
        '<span style="width: {}%"></span></div>'
        '<p class="muted">{} of {} pipeline phases have recorded outcomes.</p>'
        "{}"
    ).format(
        escape(percent),
        escape(completed),
        escape(total),
        pipeline_phase_table(phase_rows),
    )


def pipeline_live_step_panel(session: Mapping[str, Any]) -> str:
    status = str(session.get("status") or "unknown")
    step = pipeline_latest_step(session)
    if status != "running":
        return '<p class="empty">No live step is running. Session status is {}.</p>'.format(
            escape(status)
        )
    if not step:
        return '<p class="empty">Session is running, but no step record exists yet.</p>'
    return (
        '<div class="execution-grid">'
        "{}{}{}{}"
        "</div>"
        "<h3>Current Gate Flow</h3>"
        "{}"
    ).format(
        execution_status_item("Step", str(step.get("status") or "running"), str(step.get("name") or ""), ""),
        execution_status_item("Task", str(step.get("task_id") or "none"), str(session.get("current_task_ref") or ""), ""),
        execution_status_item("Started", "time", str(step.get("started_at") or ""), ""),
        execution_status_item("Elapsed", "duration", pipeline_elapsed_label(step), ""),
        pipeline_step_gate_flow_table(step),
    )


def pipeline_session_action_controls(data: Mapping[str, Any]) -> str:
    session = _mapping(data.get("session"))
    status = str(session.get("status") or "unknown")
    session_id = str(session.get("id") or "")
    safe_forms = [
        action_form("pipeline.render", [], button_label="Refresh Session"),
    ]
    guidance = pipeline_session_action_guidance(session)
    if guidance:
        safe_forms.append(guidance)
    safe_forms.extend(pipeline_session_run_action_forms(session_id, status))

    restricted = [
        '<p class="muted">Restricted actions are separated and require confirmation. '
        "Push, merge, reset, restore, clean, rebase and discard actions are not exposed.</p>"
    ]
    if status in PIPELINE_STOPPABLE_STATUSES:
        restricted.append(pipeline_session_stop_action_form(session_id))
    else:
        restricted.append(
            '<p class="empty">Stop Session is unavailable for status {}.</p>'.format(
                escape(status)
            )
        )

    return (
        '<div class="pipeline-action-groups">'
        '<div class="pipeline-action-group"><h3>Session Actions</h3>{}</div>'
        '<div class="pipeline-action-group"><h3>Owner Approval Actions</h3>{}</div>'
        '<div class="pipeline-action-group restricted-actions"><h3>Restricted Actions</h3>{}</div>'
        "</div>"
    ).format(
        "".join(safe_forms),
        pipeline_owner_approval_actions(data),
        "".join(restricted),
    )


def pipeline_owner_approval_actions(data: Mapping[str, Any]) -> str:
    session = _mapping(data.get("session"))
    task = _mapping(data.get("task"))
    task_ref = str(
        task.get("ref")
        or task.get("legacy_id")
        or task.get("id")
        or session.get("current_task_ref")
        or session.get("current_task_id")
        or ""
    )
    parts: list[str] = []
    ready_changes = [
        change
        for change in data.get("linked_changes") or []
        if isinstance(change, Mapping) and str(change.get("status") or "") == "ready"
    ]
    if ready_changes:
        for change in ready_changes:
            parts.append(
                action_form(
                    "evolution.approve_change",
                    [
                        hidden_field("change", str(change.get("id") or "")),
                        textarea_field(
                            "notes",
                            "Approval Notes",
                            rows=2,
                            placeholder="Record the Human Owner approval basis.",
                            required=True,
                        ),
                    ],
                    button_label="Approve Required Changes",
                )
            )
    else:
        parts.append('<p class="empty">No linked ready Change requires approval.</p>')

    task_status = str(task.get("status") or "")
    auto_close_enabled = bool(
        _mapping(_mapping(session.get("policy_snapshot")).get("closure")).get("auto_close_task")
    )
    if auto_close_enabled and task_ref and task_status == "in_review":
        parts.append(
            action_form(
                "task.close_reviewed",
                [
                    hidden_field("task", task_ref),
                    textarea_field(
                        "notes",
                        "Auto-close Approval Notes",
                        rows=2,
                        placeholder="Record explicit Human Owner auto-close approval.",
                        required=True,
                    ),
                ],
                button_label="Approve Auto-close",
            )
        )
    elif auto_close_enabled:
        parts.append(
            '<p class="empty">Approve Auto-close is unavailable until the selected task is in_review.</p>'
        )
    else:
        parts.append('<p class="empty">Approve Auto-close is not applicable to this policy.</p>')

    if task_ref and task_status == "in_review":
        parts.append(
            action_form(
                "task.close_reviewed",
                [
                    hidden_field("task", task_ref),
                    textarea_field(
                        "notes",
                        "Approval Notes",
                        rows=2,
                        placeholder="Record Human Owner approval before closing the reviewed task.",
                        required=True,
                    ),
                ],
                button_label="Close Reviewed Task",
            )
        )
    else:
        parts.append('<p class="empty">Close Reviewed Task is unavailable for this task state.</p>')
    return "".join(parts)


def pipeline_step_details(session: Mapping[str, Any]) -> str:
    phase_rows = pipeline_session_phase_rows(session)
    if phase_rows:
        return pipeline_phase_details(phase_rows)

    steps = [
        step
        for step in session.get("steps") or []
        if isinstance(step, Mapping)
    ]
    if not steps:
        steps = [
            {
                "name": "run_next",
                "status": "planned",
                "started_at": "",
                "finished_at": "",
                "task_id": session.get("current_task_id") or "",
                "stop_reason": "",
                "gate_outcomes": [],
            }
        ]
    html_steps = []
    latest = steps[-1] if steps else {}
    for index, step in enumerate(steps, start=1):
        open_attr = " open" if step is latest else ""
        html_steps.append(
            '<details class="pipeline-step"{}>'
            "<summary><strong>{}</strong>{}<span>{}</span></summary>"
            "{}"
            "</details>".format(
                open_attr,
                escape("{}.".format(index)),
                status_badge(str(step.get("status") or "planned")),
                escape(str(step.get("name") or "run_next")),
                pipeline_expanded_step(step, session),
            )
        )
    return "".join(html_steps)


def pipeline_phase_details(phase_rows: Sequence[Mapping[str, Any]]) -> str:
    html_phases = []
    latest = phase_rows[-1] if phase_rows else {}
    for phase in phase_rows:
        open_attr = " open" if phase is latest else ""
        html_phases.append(
            '<details class="pipeline-step"{}>'
            "<summary><strong>{}</strong>{}<span>{}</span></summary>"
            "{}"
            "</details>".format(
                open_attr,
                escape("{}.".format(phase.get("index") or "")),
                status_badge(str(phase.get("status") or "unknown")),
                escape(str(phase.get("label") or phase.get("phase") or "Unknown Phase")),
                pipeline_expanded_phase(phase),
            )
        )
    return "".join(html_phases)


def pipeline_expanded_phase(phase: Mapping[str, Any]) -> str:
    evidence = pipeline_phase_evidence_panel(phase)
    logs = pipeline_phase_log_panel(phase)
    return (
        '<div class="pipeline-step-body">'
        '<div class="review-grid">'
        "{}{}{}{}{}{}{}{}"
        "</div>"
        "{}{}"
        "</div>"
    ).format(
        review_field("Phase", escape(str(phase.get("label") or phase.get("phase") or "Unknown Phase"))),
        review_field("Status", status_badge(str(phase.get("status") or "unknown"))),
        review_field("Reason", escape(str(phase.get("reason") or ""))),
        review_field("Next Action", escape(str(phase.get("next_action") or ""))),
        review_field("Blocked By", escape(str(phase.get("blocked_by") or ""))),
        review_field("Changed Files", escape(str(phase.get("changed_files_count") or 0))),
        review_field("Generated Files", escape(str(phase.get("generated_files_count") or 0))),
        review_field("Events", escape(str(phase.get("event_count") or 0))),
        evidence,
        logs,
    )


def pipeline_phase_evidence_panel(phase: Mapping[str, Any]) -> str:
    artifacts = pipeline_phase_artifacts(phase)
    if not artifacts:
        return ""

    execute_evidence = _mapping(artifacts.get("execute_evidence"))
    adapter = _mapping(artifacts.get("adapter"))
    adapter_summary = _mapping(artifacts.get("adapter_summary"))
    prepare_artifacts = _mapping(artifacts.get("prepare_artifacts"))
    fields: list[tuple[str, str]] = []

    def add_field(label: str, *values: Any) -> None:
        text = first_nonempty_text(*values)
        if text:
            fields.append((label, text))

    add_field(
        "Error Code",
        artifacts.get("error_code"),
        execute_evidence.get("code"),
        adapter_summary.get("code"),
        adapter.get("code"),
        artifacts.get("blocked_by"),
    )
    add_field(
        "Adapter Reason",
        execute_evidence.get("reason"),
        adapter_summary.get("reason"),
        adapter.get("reason"),
    )
    add_field(
        "Command",
        execute_evidence.get("command_ref"),
        adapter_summary.get("command_ref"),
        adapter.get("command_ref"),
    )
    add_field("Timeout", artifacts.get("timeout_sec"), adapter.get("timeout_sec"))
    add_field(
        "Duration",
        execute_evidence.get("duration_sec"),
        adapter_summary.get("duration_sec"),
        adapter.get("duration_sec"),
    )
    add_field(
        "Return Code",
        execute_evidence.get("returncode"),
        adapter_summary.get("returncode"),
        adapter.get("returncode"),
    )
    add_field("Prompt Path", prepare_artifacts.get("prompt_path"), adapter.get("prompt_path"))
    add_field("Context Pack", prepare_artifacts.get("context_pack_path"))
    add_field("Report Instruction", adapter.get("report_instruction"))

    if not fields:
        return ""

    return '<h3>Execution Evidence</h3><div class="review-grid">{}</div>'.format(
        "".join(review_field(label, escape(value)) for label, value in fields)
    )


def pipeline_phase_log_panel(phase: Mapping[str, Any]) -> str:
    artifacts = pipeline_phase_artifacts(phase)
    snippets = pipeline_collect_log_snippets(
        artifacts,
        source=str(phase.get("label") or phase.get("phase") or "phase"),
    )
    if not snippets:
        return ""
    return "<h3>Logs</h3>{}".format(pipeline_log_snippets_html(snippets))


def pipeline_phase_artifacts(phase: Mapping[str, Any]) -> Mapping[str, Any]:
    return _mapping(phase.get("artifacts"))


def pipeline_expanded_step(step: Mapping[str, Any], session: Mapping[str, Any]) -> str:
    return (
        '<div class="pipeline-step-body">'
        '<div class="review-grid">'
        "{}{}{}{}{}{}"
        "</div>"
        "<h3>Gate Flow</h3>"
        "{}"
        "<h3>Gate Outcomes</h3>"
        "{}"
        "<h3>Linked Artifacts</h3>"
        "{}"
        "<h3>Logs</h3>"
        "{}"
        "</div>"
    ).format(
        review_field("Status", status_badge(str(step.get("status") or "planned"))),
        review_field("Task", escape(str(step.get("task_id") or session.get("current_task_id") or "none"))),
        review_field("Started", escape(str(step.get("started_at") or ""))),
        review_field("Finished", escape(str(step.get("finished_at") or ""))),
        review_field("Elapsed", escape(pipeline_elapsed_label(step))),
        review_field("Stop Reason", escape(str(step.get("stop_reason") or ""))),
        pipeline_step_gate_flow_table(step),
        pipeline_gate_table(step.get("gate_outcomes") or []),
        pipeline_artifact_list(pipeline_collect_artifacts(step)),
        pipeline_step_log_snippets(step),
    )


def pipeline_step_gate_flow_table(step: Mapping[str, Any]) -> str:
    rows = []
    for item in pipeline_gate_flow(step):
        rows.append(
            "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                escape(item.get("label") or ""),
                status_badge(str(item.get("status") or "planned")),
                escape(item.get("recorded_at") or ""),
                escape(item.get("detail") or ""),
            )
        )
    return table(("Checkpoint", "Status", "Recorded", "Detail"), rows, "No gate flow.")


def pipeline_phase_table(phases: Sequence[Any]) -> str:
    rows = []
    for phase in phases:
        if not isinstance(phase, Mapping):
            continue
        rows.append(
            "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                escape(phase.get("label") or phase.get("phase") or "Unknown Phase"),
                status_badge(str(phase.get("status") or "unknown")),
                escape(phase.get("reason") or phase.get("blocked_by") or ""),
                escape(phase.get("next_action") or ""),
            )
        )
    return table(("Phase", "Status", "Reason", "Next Action"), rows, "No phases recorded.")


def pipeline_gate_flow(step: Mapping[str, Any]) -> list[dict[str, str]]:
    gates_by_name = {
        str(gate.get("name") or ""): gate
        for gate in step.get("gate_outcomes") or []
        if isinstance(gate, Mapping)
    }
    flow = []
    for gate_name, label in PIPELINE_FLOW_GATES:
        gate = _mapping(gates_by_name.get(gate_name))
        details = _mapping(gate.get("details"))
        flow.append(
            {
                "name": gate_name,
                "label": label,
                "status": str(gate.get("status") or "planned"),
                "recorded_at": str(gate.get("recorded_at") or ""),
                "detail": str(
                    details.get("stop_reason")
                    or details.get("stop_code")
                    or details.get("reason")
                    or ""
                ),
            }
        )
    return flow


def pipeline_artifacts_panel(data: Mapping[str, Any]) -> str:
    session = _mapping(data.get("session"))
    artifacts = pipeline_collect_artifacts(session)
    artifacts["task_ids"].extend(
        item
        for item in (
            str(session.get("current_task_id") or ""),
            str(session.get("current_task_ref") or ""),
        )
        if item
    )
    for key, source_key in (
        ("change_ids", "linked_change_ids"),
        ("report_ids", "report_ids"),
        ("review_ids", "review_ids"),
        ("commit_ids", "commit_ids"),
    ):
        artifacts[key].extend(_string_items(session.get(source_key)))
    artifacts["generated_files"].extend(
        [
            "AI_PROJECT/generated/PIPELINE_STATUS.md",
            "AI_PROJECT/generated/PIPELINE_AUDIT.md",
        ]
    )
    artifacts["codex_prompt_paths"].append("AI_PROJECT/generated/CODEX_PROMPT.md")
    artifacts["context_pack_paths"].append("AI_PROJECT/generated/CONTEXT_PACK.md")

    rows = []
    labels = (
        ("Task IDs / Refs", "task_ids"),
        ("Change IDs", "change_ids"),
        ("Report IDs", "report_ids"),
        ("Review IDs", "review_ids"),
        ("Commit IDs", "commit_ids"),
        ("Context Pack Path", "context_pack_paths"),
        ("Codex Prompt Path", "codex_prompt_paths"),
        ("Generated Files", "generated_files"),
    )
    for label, key in labels:
        rows.append(
            "<tr><td>{}</td><td>{}</td></tr>".format(
                escape(label),
                change_list_cell(unique_strings(artifacts.get(key) or []), limit=8),
            )
        )
    return table(("Artifact", "Values"), rows, "No artifacts recorded.")


def pipeline_queue_snapshot_panel(session: Mapping[str, Any]) -> str:
    queue = _mapping(session.get("selected_queue"))
    latest_gate = pipeline_latest_gate(session)
    gate_details = _mapping(latest_gate.get("details"))
    queue_counts = _mapping(gate_details.get("queue_counts"))
    selected_task = _mapping(gate_details.get("selected_task"))
    rows = [
        ("Selection", queue.get("selection")),
        ("Task Refs", ", ".join(_string_items(queue.get("task_refs")))),
        ("Epic IDs", ", ".join(_string_items(queue.get("epic_ids")))),
        ("Statuses", ", ".join(_string_items(queue.get("statuses")))),
        ("Max Tasks", queue.get("max_tasks")),
        ("Order", queue.get("order_by")),
        ("Selected Task", _pipeline_task_label(selected_task) if selected_task else ""),
    ]
    for key in ("executable", "waiting", "blocked", "skipped"):
        if key in queue_counts:
            rows.append(("{} count".format(key), queue_counts.get(key)))
    reasons = pipeline_collect_reasons(gate_details)
    if reasons:
        rows.append(("Skip / Block Reasons", "; ".join(reasons)))
    return table(
        ("Field", "Value"),
        [
            "<tr><td>{}</td><td>{}</td></tr>".format(
                escape(label),
                escape(value if value is not None else ""),
            )
            for label, value in rows
        ],
        "No queue snapshot recorded.",
    )


def pipeline_files_changed_panel(data: Mapping[str, Any]) -> str:
    session = _mapping(data.get("session"))
    files = unique_strings(
        pipeline_collect_named_lists(session, {"changed_files", "generated_files"})
    )
    for report in data.get("reports") or []:
        if not isinstance(report, Mapping):
            continue
        files.extend(_string_items(report.get("changed_files")))
        files.extend(_string_items(report.get("generated_files")))
    files = unique_strings(files)
    if not files:
        return '<p class="empty">No changed file data is available for this session.</p>'
    return change_list_cell(files, limit=20)


def pipeline_blockers_panel(data: Mapping[str, Any]) -> str:
    session = _mapping(data.get("session"))
    blockers = []
    stop_reason = str(session.get("stop_reason") or "").strip()
    if stop_reason:
        blockers.append(stop_reason)
    blockers.extend(
        pipeline_collect_named_strings(session, {"stop_reason", "stop_code", "reason"})
    )
    for report in data.get("reports") or []:
        if isinstance(report, Mapping):
            blockers.extend(_string_items(report.get("blockers")))
            blockers.extend(_string_items(report.get("warnings")))
    blockers = unique_strings(
        [item for item in blockers if item and item != "within_token_budget"]
    )
    if not blockers:
        return '<p class="empty">No blockers or risks recorded.</p>'
    return change_list_cell(blockers, limit=20)


def pipeline_raw_debug_panel(session: Mapping[str, Any]) -> str:
    raw = _mapping(session.get("raw"))
    latest_gate = pipeline_latest_gate(session)
    return (
        '<details class="result-technical">'
        "<summary>Session JSON</summary>"
        "<pre>{}</pre>"
        "</details>"
        '<details class="result-technical">'
        "<summary>Latest Gate Details</summary>"
        "<pre>{}</pre>"
        "</details>"
    ).format(
        escape(bounded_debug_json(raw or session)),
        escape(bounded_debug_json(_mapping(latest_gate.get("details")))),
    )


def pipeline_latest_step(session: Mapping[str, Any]) -> Mapping[str, Any]:
    steps = [
        step
        for step in session.get("steps") or []
        if isinstance(step, Mapping)
    ]
    return steps[-1] if steps else {}


def pipeline_session_phase_rows(session: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    rows = [
        dict(row)
        for row in session.get("phase_rows") or []
        if isinstance(row, Mapping)
    ]
    history = pipeline_raw_phase_history(session)
    if not history:
        return rows

    enriched_rows = []
    for index, row in enumerate(rows, start=1):
        raw_phase = pipeline_raw_phase_at(history, row, index)
        artifacts = _mapping(raw_phase.get("artifacts")) if raw_phase else {}
        if artifacts:
            row["artifacts"] = artifacts
        enriched_rows.append(row)
    return enriched_rows


def pipeline_raw_phase_history(session: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    raw = _mapping(session.get("raw"))
    history = raw.get("phase_history")
    if not isinstance(history, Sequence) or isinstance(history, (str, bytes)):
        return []
    return [entry for entry in history if isinstance(entry, Mapping)]


def pipeline_raw_phase_at(
    history: Sequence[Mapping[str, Any]],
    row: Mapping[str, Any],
    index: int,
) -> Mapping[str, Any]:
    if 0 <= index - 1 < len(history):
        candidate = history[index - 1]
        if not row.get("phase") or str(candidate.get("phase") or "") == str(row.get("phase") or ""):
            return candidate
    row_phase = str(row.get("phase") or "")
    for candidate in history:
        if str(candidate.get("phase") or "") == row_phase:
            return candidate
    return {}


def pipeline_latest_phase(session: Mapping[str, Any]) -> Mapping[str, Any]:
    phase_rows = pipeline_session_phase_rows(session)
    return phase_rows[-1] if phase_rows else {}


def pipeline_session_current_phase(session: Mapping[str, Any]) -> str:
    latest_phase = pipeline_latest_phase(session)
    return str(session.get("current_phase") or latest_phase.get("phase") or "").strip()


def pipeline_session_current_phase_status(session: Mapping[str, Any]) -> str:
    latest_phase = pipeline_latest_phase(session)
    return str(session.get("current_phase_status") or latest_phase.get("status") or "").strip()


def pipeline_session_stop_reason(session: Mapping[str, Any]) -> str:
    latest_phase = pipeline_latest_phase(session)
    return str(session.get("stop_reason") or latest_phase.get("reason") or "").strip()


def pipeline_session_next_action(session: Mapping[str, Any]) -> str:
    latest_phase = pipeline_latest_phase(session)
    return str(session.get("next_action") or latest_phase.get("next_action") or "").strip()


def pipeline_session_action_guidance(session: Mapping[str, Any]) -> str:
    status = str(session.get("status") or "unknown")
    next_action = pipeline_session_next_action(session)
    if next_action:
        return '<p class="muted"><strong>Owner guidance:</strong> {}</p>'.format(
            escape(next_action)
        )
    if status == "failed":
        message = (
            "Session failed and is not running. Inspect the failure evidence before "
            "starting a new session."
        )
    elif status == "blocked":
        message = "Session is blocked and waiting for owner action."
    elif status == "stopped":
        message = "Session is stopped and can be resumed."
    elif status in {"completed", "archived"}:
        message = "Session is terminal."
    else:
        message = ""
    if not message:
        return ""
    return '<p class="muted">{}</p>'.format(escape(message))


def pipeline_session_run_action_forms(session_id: str, status: str) -> list[str]:
    if not session_id:
        return []
    if status in PIPELINE_RUNNABLE_STATUSES:
        return [
            action_form(
                "pipeline.run_next",
                [hidden_field("session_id", session_id)],
                button_label="Run Next",
            ),
            action_form(
                "pipeline.run_until_blocker",
                [hidden_field("session_id", session_id)],
                button_label="Run Until Blocker",
            ),
        ]
    if status in PIPELINE_RESUMABLE_STATUSES:
        return [
            action_form(
                "pipeline.run_next",
                [hidden_field("session_id", session_id)],
                button_label="Resume Session",
            )
        ]
    return [
        '<p class="empty">Run actions are unavailable for status {}.</p>'.format(
            escape(status)
        )
    ]


def pipeline_session_stop_action_form(session_id: str) -> str:
    return action_form(
        "pipeline.session.stop",
        [
            hidden_field("session_id", session_id),
            input_field("reason", "Reason", "Owner stop", required=True),
            filter_select(
                "status",
                "Status",
                (
                    ("stopped", "stopped"),
                    ("blocked", "blocked"),
                    ("failed", "failed"),
                ),
                "stopped",
            ),
        ],
        button_label="Stop Session",
    )


def pipeline_latest_gate(session_or_step: Mapping[str, Any]) -> Mapping[str, Any]:
    gates = [
        gate
        for gate in session_or_step.get("gate_outcomes") or []
        if isinstance(gate, Mapping)
    ]
    if gates:
        return gates[-1]
    latest_step = pipeline_latest_step(session_or_step)
    if latest_step and latest_step is not session_or_step:
        return pipeline_latest_gate(latest_step)
    return {}


def pipeline_session_task_label(data: Mapping[str, Any]) -> str:
    task = _mapping(data.get("task"))
    session = _mapping(data.get("session"))
    return str(
        task.get("ref")
        or task.get("legacy_id")
        or task.get("id")
        or session.get("current_task_ref")
        or session.get("current_task_id")
        or ""
    )


def pipeline_elapsed_label(value: Mapping[str, Any]) -> str:
    started = str(value.get("started_at") or value.get("created_at") or "")
    finished = str(value.get("finished_at") or "")
    status = str(value.get("status") or "")
    if not finished:
        finished = (
            datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z")
            if status == "running"
            else str(value.get("updated_at") or "")
        )
    start_dt = parse_timestamp(started)
    finish_dt = parse_timestamp(finished)
    if not start_dt or not finish_dt:
        return "unknown"
    seconds = max(0, int((finish_dt - start_dt).total_seconds()))
    minutes, rem = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return "{}h {}m {}s".format(hours, minutes, rem)
    if minutes:
        return "{}m {}s".format(minutes, rem)
    return "{}s".format(rem)


def parse_timestamp(value: str) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def review_field(label: str, value: str) -> str:
    return '<div class="review-field"><span>{}</span><div>{}</div></div>'.format(
        escape(label),
        value,
    )


def pipeline_step_log_snippets(step: Mapping[str, Any]) -> str:
    return pipeline_log_snippets_html(
        pipeline_collect_log_snippets(step),
        empty_message="No bounded stdout/stderr snippets recorded.",
    )


def pipeline_log_snippets_html(
    snippets: Sequence[Mapping[str, str]],
    *,
    empty_message: str = "",
) -> str:
    if not snippets:
        return '<p class="empty">{}</p>'.format(escape(empty_message)) if empty_message else ""
    parts = []
    for snippet in snippets:
        label = "{} {}".format(snippet.get("source") or "log", snippet.get("stream") or "").strip()
        ref = str(snippet.get("ref") or "")
        text = bounded_text(str(snippet.get("text") or ""), PIPELINE_LOG_SNIPPET_LIMIT)
        parts.append(
            '<details class="result-technical" open>'
            "<summary>{}</summary>"
            "{}"
            "<pre>{}</pre>"
            "</details>".format(
                escape(label),
                '<p class="muted"><code>{}</code></p>'.format(escape(ref)) if ref else "",
                escape(text),
            )
        )
    return "".join(parts)


def pipeline_collect_log_snippets(value: Any, *, source: str = "") -> list[dict[str, str]]:
    snippets: list[dict[str, str]] = []
    if isinstance(value, Mapping):
        name = str(value.get("name") or source)
        for stream in ("stdout", "stderr"):
            text = str(value.get("{}_snippet".format(stream)) or "")
            ref = str(value.get("{}_ref".format(stream)) or "")
            if text or ref:
                snippets.append(
                    {
                        "source": name,
                        "stream": stream,
                        "text": text,
                        "ref": ref,
                    }
                )
        for nested in value.values():
            snippets.extend(pipeline_collect_log_snippets(nested, source=name))
    elif isinstance(value, list):
        for nested in value:
            snippets.extend(pipeline_collect_log_snippets(nested, source=source))
    return snippets


def pipeline_collect_artifacts(value: Any) -> dict[str, list[str]]:
    artifacts: dict[str, list[str]] = {
        "task_ids": [],
        "change_ids": [],
        "report_ids": [],
        "review_ids": [],
        "commit_ids": [],
        "context_pack_paths": [],
        "codex_prompt_paths": [],
        "generated_files": [],
    }
    pipeline_collect_artifacts_into(value, artifacts)
    return {key: unique_strings(items) for key, items in artifacts.items()}


def pipeline_collect_artifacts_into(value: Any, artifacts: dict[str, list[str]]) -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            key_text = str(key)
            if key_text in {"task_id", "current_task_id"}:
                artifacts["task_ids"].extend(_scalar_or_string_items(nested))
            elif key_text in {"task_ref", "current_task_ref", "selected_ref", "ref"}:
                artifacts["task_ids"].extend(_scalar_or_string_items(nested))
            elif key_text in {"change_id", "change_ids", "linked_change_ids", "created_change_ids", "approved_change_ids"}:
                artifacts["change_ids"].extend(_scalar_or_string_items(nested))
            elif key_text in {"report_id", "report_ids"}:
                artifacts["report_ids"].extend(_scalar_or_string_items(nested))
            elif key_text in {"review_id", "review_ids"}:
                artifacts["review_ids"].extend(_scalar_or_string_items(nested))
            elif key_text in {"commit_id", "commit_ids", "commit_hash"}:
                artifacts["commit_ids"].extend(_scalar_or_string_items(nested))
            elif key_text in {"generated_files"}:
                artifacts["generated_files"].extend(_scalar_or_string_items(nested))
            elif key_text == "prompt_path":
                artifacts["codex_prompt_paths"].extend(_scalar_or_string_items(nested))
            elif key_text in {"context_pack"}:
                context_pack = _mapping(nested)
                artifacts["context_pack_paths"].extend(_scalar_or_string_items(context_pack.get("path")))
                artifacts["context_pack_paths"].extend(_scalar_or_string_items(context_pack.get("resolved_path")))
            pipeline_collect_artifacts_into(nested, artifacts)
    elif isinstance(value, list):
        for nested in value:
            pipeline_collect_artifacts_into(nested, artifacts)


def pipeline_artifact_list(artifacts: Mapping[str, list[str]]) -> str:
    rows = []
    for label, key in (
        ("Tasks", "task_ids"),
        ("Changes", "change_ids"),
        ("Reports", "report_ids"),
        ("Reviews", "review_ids"),
        ("Commits", "commit_ids"),
        ("Context Packs", "context_pack_paths"),
        ("Codex Prompts", "codex_prompt_paths"),
        ("Generated Files", "generated_files"),
    ):
        values = unique_strings(artifacts.get(key) or [])
        rows.append(
            "<tr><td>{}</td><td>{}</td></tr>".format(
                escape(label),
                change_list_cell(values, limit=6),
            )
        )
    return table(("Type", "Values"), rows, "No linked artifacts recorded.")


def pipeline_collect_named_lists(value: Any, names: set[str]) -> list[str]:
    items: list[str] = []
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if str(key) in names:
                items.extend(_scalar_or_string_items(nested))
            items.extend(pipeline_collect_named_lists(nested, names))
    elif isinstance(value, list):
        for nested in value:
            items.extend(pipeline_collect_named_lists(nested, names))
    return items


def pipeline_collect_named_strings(value: Any, names: set[str]) -> list[str]:
    items: list[str] = []
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if str(key) in names and not isinstance(nested, (Mapping, list)):
                text = str(nested or "").strip()
                if text:
                    items.append(text)
            items.extend(pipeline_collect_named_strings(nested, names))
    elif isinstance(value, list):
        for nested in value:
            items.extend(pipeline_collect_named_strings(nested, names))
    return items


def pipeline_collect_reasons(value: Any) -> list[str]:
    reasons: list[str] = []
    if isinstance(value, Mapping):
        reason_items = value.get("reasons")
        if isinstance(reason_items, list):
            for item in reason_items:
                if isinstance(item, Mapping):
                    code = str(item.get("code") or "").strip()
                    detail = str(item.get("detail") or "").strip()
                    reasons.append("{} {}".format(code, detail).strip())
                else:
                    reasons.append(str(item))
        for nested in value.values():
            reasons.extend(pipeline_collect_reasons(nested))
    elif isinstance(value, list):
        for nested in value:
            reasons.extend(pipeline_collect_reasons(nested))
    return unique_strings([reason for reason in reasons if reason])


def _scalar_or_string_items(value: Any) -> list[str]:
    if isinstance(value, list):
        return _string_items(value)
    if value is None or isinstance(value, Mapping):
        return []
    text = str(value).strip()
    return [text] if text else []


def unique_strings(values: Sequence[Any]) -> list[str]:
    seen: set[str] = set()
    selected: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if text and text not in seen:
            selected.append(text)
            seen.add(text)
    return selected


def bounded_debug_json(value: Any) -> str:
    return bounded_text(
        json.dumps(bounded_debug_value(value), ensure_ascii=False, indent=2, sort_keys=True),
        PIPELINE_RAW_DEBUG_LIMIT,
    )


def bounded_debug_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        bounded = {}
        for key, nested in value.items():
            key_text = str(key)
            if key_text in {"stdout", "stderr", "stdout_snippet", "stderr_snippet"}:
                bounded[key] = bounded_text(str(nested or ""), PIPELINE_LOG_SNIPPET_LIMIT)
            else:
                bounded[key] = bounded_debug_value(nested)
        return bounded
    if isinstance(value, list):
        return [bounded_debug_value(item) for item in value]
    return value


def bounded_text(value: str, limit: int) -> str:
    text = str(value or "")
    if len(text) <= limit:
        return text
    return "{}\n[truncated: {} bytes total]".format(text[:limit], len(text.encode("utf-8")))


def first_nonempty_text(*values: Any) -> str:
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return ""


def pipeline_selector_form(data: Mapping[str, Any], pipeline: Mapping[str, Any]) -> str:
    request = _mapping(pipeline.get("queue_request"))
    current_task = _mapping(data.get("current_task"))
    policy_options = [
        (str(policy.get("name") or ""), _pipeline_policy_option_label(policy))
        for policy in pipeline.get("policies") or []
        if isinstance(policy, Mapping) and policy.get("name")
    ]
    epic_options = [("", "Any Epic")]
    epic_options.extend(
        (
            str(epic.get("id") or ""),
            "{} - {}".format(epic.get("key") or epic.get("id") or "", epic.get("title") or "").strip(" -"),
        )
        for epic in data.get("epics") or []
        if isinstance(epic, Mapping) and epic.get("id")
    )
    status_options = [
        ("", "Any Status"),
        ("planned", "planned"),
        ("ready", "ready"),
        ("in_progress", "in_progress"),
        ("blocked", "blocked"),
        ("in_review", "in_review"),
        ("changes_requested", "changes_requested"),
    ]
    max_tasks = request.get("max_tasks")
    auto_create_missing_changes = bool(request.get("auto_create_missing_changes"))
    owner_approve_required_changes = bool(
        request.get("owner_approve_required_changes")
    )
    approval_note = str(request.get("approval_note") or "")
    auto_close_note = str(request.get("auto_close_note") or "")
    return (
        '<form class="task-controls" method="get" action="/pipeline">'
        "{}{}{}{}{}{}{}{}{}"
        '<button type="submit">Preview Queue</button>'
        '<a class="button-link secondary" href="/pipeline">Reset</a>'
        "</form>"
    ).format(
        filter_select("policy", "Policy", policy_options, str(request.get("policy") or "")),
        input_field(
            "task_ref",
            "Task Refs",
            ", ".join(_string_items(request.get("task_refs"))),
            required=False,
        ),
        filter_select(
            "epic",
            "Epic",
            epic_options,
            next(iter(_string_items(request.get("epic_ids"))), ""),
        ),
        filter_select(
            "status",
            "Status",
            status_options,
            next(iter(_string_items(request.get("statuses"))), ""),
        ),
        input_field(
            "max_tasks",
            "Max Tasks",
            "" if max_tasks is None else str(max_tasks),
            required=False,
        ),
        filter_select(
            "order_by",
            "Order",
            (("execution", "execution"), ("owner", "owner"), ("selected", "selected")),
            str(request.get("order_by") or "execution"),
        ),
        checkbox_field(
            "auto_create_missing_changes",
            "Auto-create missing Changes",
            checked=auto_create_missing_changes,
        ),
        checkbox_field(
            "owner_approve_required_changes",
            "Owner-approve required Changes for this session",
            checked=owner_approve_required_changes,
        ),
        input_field(
            "approval_note",
            "Approval Note",
            approval_note,
            required=False,
        ),
        input_field(
            "auto_close_note",
            "Auto-close Note",
            auto_close_note,
            required=False,
        ),
    )


def pipeline_policy_preview(policy: Mapping[str, Any]) -> str:
    queue = _mapping(policy.get("queue"))
    codex = _mapping(policy.get("codex"))
    token_budget = _mapping(policy.get("token_budget"))
    review = _mapping(policy.get("review"))
    evolution = _mapping(policy.get("evolution"))
    closure = _mapping(policy.get("closure"))
    commit = _mapping(policy.get("commit"))
    rows = [
        ("Name", policy.get("name")),
        ("Valid", "yes" if policy.get("valid") else "no"),
        ("Behavior", policy.get("behavior_label") or ""),
        ("Queue", "{} max {}".format(queue.get("selection"), queue.get("max_tasks"))),
        ("Codex", "{} / {}".format(codex.get("mode"), codex.get("adapter_mode"))),
        ("Token Gate", "required" if token_budget.get("require_gate_pass") else "not required"),
        (
            "Auto Create Missing Changes",
            "yes" if evolution.get("create_missing_change") else "no",
        ),
        (
            "Owner Session Change Approval",
            "yes"
            if evolution.get("owner_approve_required_changes_for_session")
            else "no",
        ),
        (
            "Approval Note Required",
            "yes"
            if evolution.get("owner_approve_required_changes_for_session")
            else "no",
        ),
        ("Review", _pipeline_review_summary(review)),
        ("Auto Close", "yes" if closure.get("auto_close_task") else "no"),
        ("Commit", str(commit.get("mode") or "disabled")),
    ]
    error_rows = []
    for issue in policy.get("errors") or []:
        if isinstance(issue, Mapping):
            error_rows.append(
                "<li><strong>{}</strong>: {}</li>".format(
                    escape(issue.get("code") or ""),
                    escape(issue.get("message") or ""),
                )
            )
    content = [
        table(
            ("Field", "Value"),
            [
                "<tr><td>{}</td><td>{}</td></tr>".format(
                    escape(label),
                    escape(value if value is not None else ""),
                )
                for label, value in rows
            ],
            "No policy selected.",
        )
    ]
    if error_rows:
        content.append('<ul class="hint-list">{}</ul>'.format("".join(error_rows)))
    return "".join(content)


def _pipeline_policy_option_label(policy: Mapping[str, Any]) -> str:
    name = str(policy.get("name") or "")
    behavior = str(policy.get("behavior_label") or "")
    if not behavior:
        return name
    return "{} ({})".format(name, behavior)


def pipeline_queue_preview_table(
    queue_preview: Mapping[str, Any],
    queue_error: Mapping[str, Any],
) -> str:
    if queue_error:
        return '<p class="empty">{}: {}</p>'.format(
            escape(queue_error.get("code") or "QUEUE_PREVIEW_FAILED"),
            escape(queue_error.get("message") or ""),
        )
    items = [
        item
        for item in queue_preview.get("items") or []
        if isinstance(item, Mapping)
    ]
    rows = []
    for item in items:
        rows.append(
            "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                status_badge(str(item.get("category") or "unknown")),
                escape(_pipeline_task_label(item)),
                status_badge(str(item.get("status") or "unknown")),
                escape(item.get("epic_id") or ""),
                escape(item.get("title") or ""),
                pipeline_reason_list(item.get("reasons") or []),
            )
        )
    return table(
        ("Category", "Task", "Status", "Epic", "Title", "Reasons"),
        rows,
        "No queue preview items.",
    )


def pipeline_current_session_panel(
    data: Mapping[str, Any],
    pipeline: Mapping[str, Any],
) -> str:
    session = _mapping(pipeline.get("current_session"))
    parts = ['<section class="panel action-panel">', "<h2>Current Session</h2>"]
    if session:
        phase_rows = [
            row
            for row in session.get("recent_phase_rows") or pipeline_session_phase_rows(session)
            if isinstance(row, Mapping)
        ]
        parts.extend(
            [
                '<div class="execution-grid">',
                metric("Session", str(session.get("id") or "")),
                metric("Status", str(session.get("status") or "")),
                metric("Policy", str(session.get("policy") or "")),
                metric("Task", str(session.get("current_task_ref") or session.get("current_task_id") or "none")),
                metric("Step", str(session.get("current_step") or "none")),
                metric("Phase", pipeline_session_current_phase(session) or "none"),
                metric("Phase Status", pipeline_session_current_phase_status(session) or "none"),
                metric("Stop", pipeline_session_stop_reason(session) or "none"),
                metric("Next Action", pipeline_session_next_action(session) or "none"),
                "</div>",
            ]
        )
        if phase_rows:
            parts.extend(["<h3>Phases</h3>", pipeline_phase_table(phase_rows)])
        else:
            parts.extend(
                [
                    "<h3>Gates</h3>",
                    pipeline_gate_table(session.get("recent_gates") or []),
                    "<h3>Steps</h3>",
                    pipeline_step_table(session.get("recent_steps") or []),
                ]
            )
        parts.extend(["<h3>References</h3>", pipeline_reference_list(session)])
    else:
        parts.append('<p class="empty">No current pipeline session.</p>')
    parts.append("<h3>Pipeline Actions</h3>")
    parts.append(pipeline_action_controls(data, pipeline))
    parts.append("</section>")
    return "".join(parts)


def pipeline_action_controls(data: Mapping[str, Any], pipeline: Mapping[str, Any]) -> str:
    request = _mapping(pipeline.get("queue_request"))
    session = _mapping(pipeline.get("current_session"))
    current_task = _mapping(data.get("current_task"))
    policy_options = [
        (str(policy.get("name") or ""), _pipeline_policy_option_label(policy))
        for policy in pipeline.get("policies") or []
        if isinstance(policy, Mapping) and policy.get("name")
    ]
    status_options = [
        ("", "Any Status"),
        ("planned", "planned"),
        ("ready", "ready"),
        ("in_progress", "in_progress"),
        ("blocked", "blocked"),
        ("in_review", "in_review"),
        ("changes_requested", "changes_requested"),
    ]
    max_tasks = request.get("max_tasks")
    auto_create_missing_changes = bool(request.get("auto_create_missing_changes"))
    owner_approve_required_changes = bool(
        request.get("owner_approve_required_changes")
    )
    approval_note = str(request.get("approval_note") or "")
    auto_close_note = str(request.get("auto_close_note") or "")
    create_fields = [
        filter_select("policy", "Policy", policy_options, str(request.get("policy") or "")),
        input_field(
            "task_ref",
            "Task Refs",
            ", ".join(_string_items(request.get("task_refs"))),
            required=False,
        ),
        input_field(
            "epic",
            "Epic",
            ", ".join(_string_items(request.get("epic_ids"))),
            required=False,
        ),
        filter_select(
            "status_filter",
            "Status Filter",
            status_options,
            next(iter(_string_items(request.get("statuses"))), ""),
        ),
        input_field(
            "max_tasks",
            "Max Tasks",
            "" if max_tasks is None else str(max_tasks),
            required=False,
        ),
        filter_select(
            "order_by",
            "Order",
            (("execution", "execution"), ("owner", "owner"), ("selected", "selected")),
            str(request.get("order_by") or "execution"),
        ),
        checkbox_field(
            "auto_create_missing_changes",
            "Auto-create missing Changes",
            checked=auto_create_missing_changes,
        ),
        checkbox_field(
            "owner_approve_required_changes",
            "Owner-approve required Changes for this session",
            checked=owner_approve_required_changes,
        ),
        input_field(
            "approval_note",
            "Approval Note",
            approval_note,
            required=False,
        ),
        input_field(
            "auto_close_note",
            "Auto-close Note",
            auto_close_note,
            required=False,
        ),
    ]
    if current_task.get("id"):
        create_fields.append(hidden_field("current_task_id", str(current_task.get("id") or "")))
        create_fields.append(hidden_field("current_task_ref", str(current_task.get("ref") or current_task.get("id") or "")))
    forms = [
        action_form(
            "pipeline.session.create",
            create_fields,
            button_label="Create Session",
        ),
        action_form("pipeline.render", [], button_label="Refresh Status"),
    ]
    session_id = str(session.get("id") or "")
    if session_id:
        session_status = str(session.get("status") or "unknown")
        guidance = pipeline_session_action_guidance(session)
        if guidance:
            forms.append(guidance)
        forms.extend(pipeline_session_run_action_forms(session_id, session_status))
        if session_status in PIPELINE_STOPPABLE_STATUSES:
            forms.append(pipeline_session_stop_action_form(session_id))
        else:
            forms.append(
                '<p class="empty">Stop Session is unavailable for status {}.</p>'.format(
                    escape(session_status)
                )
            )
    return '<div class="pipeline-actions">{}</div>'.format("".join(forms))


def pipeline_gate_table(gates: Sequence[Any]) -> str:
    rows = []
    for gate in gates:
        if not isinstance(gate, Mapping):
            continue
        details = _mapping(gate.get("details"))
        rows.append(
            "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                escape(gate.get("name") or ""),
                status_badge(str(gate.get("status") or "unknown")),
                escape(gate.get("recorded_at") or ""),
                escape(details.get("stop_reason") or details.get("stop_code") or ""),
            )
        )
    return table(("Gate", "Status", "Recorded", "Detail"), rows, "No gates recorded.")


def pipeline_step_table(steps: Sequence[Any]) -> str:
    rows = []
    for step in steps:
        if not isinstance(step, Mapping):
            continue
        rows.append(
            "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                escape(step.get("name") or ""),
                status_badge(str(step.get("status") or "unknown")),
                escape(step.get("task_id") or ""),
                escape(step.get("stop_reason") or ""),
            )
        )
    return table(("Step", "Status", "Task", "Stop Reason"), rows, "No steps recorded.")


def pipeline_reference_list(session: Mapping[str, Any]) -> str:
    refs = []
    for label, key in (
        ("Changes", "linked_change_ids"),
        ("Reports", "report_ids"),
        ("Reviews", "review_ids"),
        ("Commits", "commit_ids"),
    ):
        values = _string_items(session.get(key))
        refs.append("<li><strong>{}</strong>: {}</li>".format(escape(label), escape(", ".join(values) or "none")))
    return '<ul class="compact-list">{}</ul>'.format("".join(refs))


def pipeline_session_table(sessions: Sequence[Any]) -> str:
    rows = []
    for session in sessions:
        if not isinstance(session, Mapping):
            continue
        session_id = str(session.get("id") or "")
        rows.append(
            "<tr><td><code>{}</code></td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                '<a href="/pipeline/sessions/{0}">{0}</a>'.format(escape(session_id)),
                status_badge(str(session.get("status") or "unknown")),
                escape(session.get("policy") or ""),
                escape(session.get("current_task_ref") or session.get("current_task_id") or ""),
                escape(session.get("current_step") or ""),
                escape(session.get("stop_reason") or ""),
            )
        )
    return table(
        ("Session", "Status", "Policy", "Task", "Step", "Stop Reason"),
        rows,
        "No pipeline sessions recorded.",
    )


def pipeline_audit_table(events: Sequence[Any]) -> str:
    rows = []
    for event in events:
        if not isinstance(event, Mapping):
            continue
        rows.append(
            "<tr><td><code>{}</code></td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                escape(event.get("event_id") or ""),
                escape(event.get("timestamp") or ""),
                escape(event.get("command") or ""),
                escape(event.get("entity_id") or ""),
                escape(event.get("summary") or ""),
            )
        )
    return table(
        ("Event", "Time", "Command", "Entity", "Summary"),
        rows,
        "No pipeline audit entries.",
    )


def pipeline_reason_list(reasons: Sequence[Any]) -> str:
    items = []
    for reason in reasons:
        if isinstance(reason, Mapping):
            items.append(
                "<li><strong>{}</strong> {}</li>".format(
                    escape(reason.get("code") or ""),
                    escape(reason.get("detail") or ""),
                )
            )
    if not items:
        return '<span class="muted">none</span>'
    return '<ul class="compact-list">{}</ul>'.format("".join(items))


def _pipeline_task_label(item: Mapping[str, Any]) -> str:
    return str(
        item.get("ref")
        or item.get("legacy_id")
        or item.get("id")
        or item.get("selected_ref")
        or "unknown"
    )


def _pipeline_review_summary(review: Mapping[str, Any]) -> str:
    required = []
    if review.get("require_machine_review"):
        required.append("machine {}".format(review.get("required_machine_outcome")))
    if review.get("require_codex_review"):
        required.append("codex {}".format(review.get("required_codex_decision")))
    return ", ".join(required) or "not required"


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
    selected_task = tasks[0] if len(tasks) == 1 else {}
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
        '<section class="panel execution-panel">',
        "<h2>Current Execution</h2>",
        execution_status_panel(data, selected_task=selected_task, show_actions=False),
        "</section>",
        project_health_panel(data, selected_task=selected_task),
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
            epic_completion_cell(epic),
            epic_open_changes_cell(epic),
            pipeline_hint_cell(epic),
            epic_row_actions(epic, data),
        ]
        rows.append("<tr>{}</tr>".format("".join("<td>{}</td>".format(cell) for cell in cells)))
    body = [
        '<section class="panel">',
        "<h2>Epics</h2>",
        table(
            (
                "Epic",
                "Status",
                "Initiative",
                "Title",
                "Tasks",
                "Open Changes",
                "Next / Blockers",
                "Actions",
            ),
            rows,
            "No epics.",
        ),
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


def render_commit_readiness(data: Mapping[str, Any]) -> str:
    git = _mapping(data.get("git"))
    doctor = _mapping(data.get("doctor"))
    changed_files = [
        item
        for item in git.get("changed_files") or []
        if isinstance(item, Mapping)
    ]
    body = [
        '<section class="summary-grid">',
        metric("Readiness", str(data.get("status") or "UNKNOWN")),
        metric("Changed Files", str(len(changed_files))),
        metric("Validation", str(doctor.get("overall_status") or "UNKNOWN")),
        metric("Git", str(git.get("status") or "unknown")),
        "</section>",
        '<section class="panel">',
        "<h2>Commit Readiness</h2>",
        '<div class="status-row">',
        status_badge(str(data.get("status") or "UNKNOWN")),
        "<span>{}</span>".format(escape(data.get("message") or "")),
        doctor_cache_detail(doctor),
        '<a class="button-link" href="/commit?refresh=1">Refresh readiness checks</a>',
        "</div>",
        "</section>",
        '<section class="panel">',
        "<h2>Changed Files</h2>",
        commit_changed_files_table(git),
        '<p class="muted">Read command: <code>{}</code></p>'.format(
            escape(git.get("command") or "git status --short --untracked-files=all")
        ),
        "</section>",
        '<section class="panel">',
        "<h2>Readiness Checks</h2>",
        commit_validation_table(_mapping(data.get("validation"))),
        "</section>",
        '<section class="panel">',
        "<h2>Completed Tasks</h2>",
        commit_task_table(data.get("completed_tasks")),
        "</section>",
        '<section class="panel">',
        "<h2>Accepted Changes</h2>",
        commit_change_table(data.get("accepted_changes")),
        "</section>",
        '<section class="panel">',
        "<h2>Suggested Commit Message (not executed)</h2>",
        '<textarea readonly rows="2">{}</textarea>'.format(
            escape(data.get("suggested_commit_message") or "")
        ),
        '<p class="muted">Suggestion only. This view does not run git commit, git push, staging, reset, restore, or checkout commands.</p>',
        "</section>",
    ]
    return render_page("Commit Readiness", "".join(body), active="/commit")


def commit_changed_files_table(git: Mapping[str, Any]) -> str:
    rows = []
    for item in git.get("changed_files") or []:
        if not isinstance(item, Mapping):
            continue
        rows.append(
            "<tr><td>{}</td><td><code>{}</code></td></tr>".format(
                escape(item.get("status") or ""),
                escape(item.get("path") or ""),
            )
        )
    return table(
        ("Status", "Path"),
        rows,
        str(git.get("message") or "No changed files available."),
    )


def commit_validation_table(validation: Mapping[str, Any]) -> str:
    groups = [
        _mapping(validation.get("project")),
        _mapping(validation.get("protected_files")),
        _mapping(validation.get("generated")),
    ]
    rows = []
    for group in groups:
        if not group:
            continue
        rows.append(
            "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                escape(group.get("label") or ""),
                status_badge(str(group.get("status") or "UNKNOWN")),
                escape(group.get("message") or ""),
                commit_finding_list(group.get("findings")),
            )
        )
    return table(
        ("Area", "Status", "Signal", "Findings"),
        rows,
        "No readiness checks available.",
    )


def commit_finding_list(value: Any) -> str:
    findings = [item for item in value or [] if isinstance(item, Mapping)]
    if not findings:
        return '<p class="empty">No findings yet.</p>'
    items = []
    for finding in findings:
        label = "{}: {}".format(
            finding.get("check") or "check",
            finding.get("message") or "",
        ).strip()
        items.append(
            "<li>{} {}</li>".format(
                status_badge(str(finding.get("status") or "UNKNOWN")),
                escape(label),
            )
        )
    return '<ul class="compact-list">{}</ul>'.format("".join(items))


def commit_task_table(value: Any) -> str:
    tasks = [item for item in value or [] if isinstance(item, Mapping)]
    rows = [
        "<tr><td><code>{}</code></td><td>{}</td><td>{}</td></tr>".format(
            escape(task.get("ref") or task.get("id") or ""),
            escape(task.get("title") or ""),
            escape(task.get("updated_at") or ""),
        )
        for task in tasks
    ]
    return table(
        ("Task", "Title", "Updated"),
        rows,
        "No completed task records available.",
    )


def commit_change_table(value: Any) -> str:
    changes = [item for item in value or [] if isinstance(item, Mapping)]
    rows = [
        "<tr><td><code>{}</code></td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            escape(change.get("id") or ""),
            escape(change.get("title") or ""),
            escape(change.get("accepted_at") or change.get("updated_at") or ""),
            escape(", ".join(_string_items(change.get("linked_tasks")))),
        )
        for change in changes
    ]
    return table(
        ("Change", "Title", "Accepted", "Linked Tasks"),
        rows,
        "No accepted Change records available.",
    )


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
        project_health_panel(data),
        '<section class="panel">',
        "<h2>Generated Views</h2>",
        table(("File", "Source", "Exists", "Updated", "First Line"), rows, "No generated views."),
        "</section>",
    ]
    return render_page("Generated", "".join(body), active="/generated")


def render_settings(model: ReadOnlyProjectModel) -> str:
    settings = load_ui_settings(root=model.root)
    source = ui_settings_source(root=model.root)
    path = ui_settings_path(model.root)
    body = [
        '<section class="panel settings-panel">',
        '<form method="post" action="/actions">',
        hidden_field("action", "ui.settings.apply"),
        '<div class="settings-panel-header">',
        "<div>",
        "<h2>Settings</h2>",
        '<p class="muted">Source: <strong>{}</strong> | Path: <code>{}</code></p>'.format(
            escape(source),
            escape(str(path)),
        ),
        "</div>",
        '<span class="pill">single apply</span>',
        "</div>",
        settings_group(
            "Pipeline",
            [
                settings_text_row(
                    "command_line",
                    "Command Line",
                    settings,
                    helper="Shell-style local Codex command used by UI runs.",
                ),
                settings_text_row(
                    "default_policy",
                    "Default Policy",
                    settings,
                    helper="Pipeline policy preset used when the UI starts a run.",
                ),
            ],
        ),
        settings_group(
            "Review Gates",
            [
                settings_locked_row(
                    "Machine Review",
                    "machine_review",
                    helper="Locked ON. Machine Review remains required before close.",
                ),
                settings_checkbox_row(
                    REQUIRE_CODEX_REVIEW_SETTING,
                    "Require Codex Review before close",
                    settings,
                    helper="Disable to skip semantic LLM review and save tokens.",
                ),
            ],
        ),
        settings_group(
            "Timeouts",
            [
                settings_text_row(
                    "execution_timeout_sec",
                    "Execution Timeout",
                    settings,
                    helper="Optional local Codex execution timeout in seconds.",
                    input_type="number",
                ),
                settings_text_row(
                    "preflight_timeout_sec",
                    "Preflight Timeout",
                    settings,
                    helper="Optional readiness-check timeout in seconds.",
                    input_type="number",
                ),
            ],
        ),
        settings_group(
            "Advanced",
            [
                settings_checkbox_row(
                    INTERNAL_CHANGE_GATE_BYPASS_SETTING,
                    "Allow internal Change gate bypass",
                    settings,
                    helper=(
                        "Internal project-control tasks only. Does not approve Changes "
                        "or bypass review, report, close, or commit gates."
                    ),
                ),
            ],
        ),
        '<footer class="settings-footer">',
        '<a class="button-link secondary" href="/settings">Reset</a>',
        '<label class="checkline"><input type="checkbox" name="confirm" value="yes" required>Confirm</label>',
        '<button type="submit">Apply Settings</button>',
        "</footer>",
        "</form>",
        "</section>",
    ]
    return render_page("Settings", "".join(body), active="/settings")


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
        project_health_panel(data),
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
        if read_write.get("validates"):
            flags.append("validates")
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
        if read_write.get("validates"):
            flags.append("validates")
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
                file_input_field(
                    WEB_IMPORT_FILE_FIELD,
                    "JSON/Text File",
                    accept=".json,.txt,application/json,text/plain",
                ),
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
            multipart=True,
        ),
        "</section>",
        '<section class="panel action-panel">',
        "<h2>Health & Repair</h2>",
        action_form("project.doctor", [], button_label="Run Doctor"),
        action_form("project.protected_check", [], button_label="Check Protected Files"),
        action_form("docs.render", [], button_label="Render Docs"),
        action_form("project.render", [], button_label="Render Project Views"),
        "</section>",
        '<section class="panel action-panel">',
        "<h2>Task Workflows</h2>",
        table(("Workflow", "Command", "Step Preview"), workflow_rows, "No workflows."),
        action_form(
            "ui.run_selected_task",
            [input_field("task", "Task", default_task)],
            button_label="Run Selected Task",
        ),
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
            button_label="Close Epic If Complete",
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
        action_form("docs.render", [], button_label="Render Docs"),
        action_form("project.protected_check", [], button_label="Check Protected Files"),
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
    sections.extend(_ui_settings_result_panel(data))
    sections.extend(_message_panel("Warnings", "warn", _messages(result.get("warnings"))))
    sections.extend(_message_panel("Errors", "fail", visible_errors))
    sections.extend(_pipeline_result_panel(data))
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
        ("Setting", data.get("key")),
        ("Task", data.get("task_ref") or task.get("ref") or task.get("id")),
        ("Change", data.get("change_ref") or change.get("id")),
        ("Epic", data.get("epic_ref") or epic.get("id")),
        ("Session", data.get("session_id")),
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
    side_effects = data.get("side_effects")
    if isinstance(side_effects, list):
        return [
            {
                "id": str(effect.get("command") or ""),
                "title": str(effect.get("command") or "Pipeline side effect"),
                "status": "ok" if effect.get("ok") else "failed",
                "route": str(effect.get("message") or ""),
            }
            for effect in side_effects
            if isinstance(effect, Mapping)
        ]
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


def _ui_settings_result_panel(data: Mapping[str, Any]) -> list[str]:
    key = str(data.get("key") or "").strip()
    path = str(data.get("path") or "").strip()
    if not key or not path:
        return []
    value = str(data.get("value") or "")
    facts = [
        ("Updated key", key),
        ("New value", value),
        ("Settings path", path),
    ]
    return [
        '<section class="result-section">',
        "<h3>UI Setting</h3>",
        '<ul class="result-actions">{}</ul>'.format(
            "".join(
                "<li><strong>{}</strong>: <code>{}</code></li>".format(
                    escape(label),
                    escape(item),
                )
                for label, item in facts
            )
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


def _pipeline_result_panel(data: Mapping[str, Any]) -> list[str]:
    if not data.get("session_id"):
        return []
    sections = []
    facts = []
    for label, key in (
        ("Session", "session_id"),
        ("Stop Code", "stop_code"),
        ("Stop Reason", "stop_reason"),
        ("Current Task", "current_task_id"),
        ("Current Step", "current_step"),
        ("Step Status", "current_step_status"),
    ):
        value = str(data.get(key) or "").strip()
        if value:
            facts.append(
                "<li><strong>{}</strong>: {}</li>".format(
                    escape(label),
                    escape(value),
                )
            )
    if facts:
        session_href = str(
            data.get("session_href") or data.get("redirect_target") or ""
        ).strip()
        if session_href:
            facts.append(
                '<li><strong>Session Page</strong>: <a href="{}">{}</a></li>'.format(
                    escape(session_href),
                    escape(session_href),
                )
            )
        sections.extend(
            [
                '<section class="result-section">',
                "<h3>Pipeline Result</h3>",
                '<ul class="result-actions">{}</ul>'.format("".join(facts)),
                "</section>",
            ]
        )

    blockers = []
    for blocker in data.get("blockers") or []:
        if isinstance(blocker, Mapping):
            blockers.append(
                "<li><strong>{}</strong>: {}</li>".format(
                    escape(blocker.get("code") or "BLOCKED"),
                    escape(blocker.get("reason") or ""),
                )
            )
    if blockers:
        sections.extend(
            [
                '<section class="result-section result-section-warn">',
                "<h3>Blockers</h3>",
                '<ul class="result-messages">{}</ul>'.format("".join(blockers)),
                "</section>",
            ]
        )

    refs = []
    for label, key in (
        ("Completed Tasks", "completed_tasks"),
        ("Changed Tasks", "changed_tasks"),
        ("Requested Changes", "requested_changes"),
        ("Accepted Changes", "accepted_changes"),
        ("Reports", "report_ids"),
        ("Reviews", "review_ids"),
        ("Commits", "commits"),
    ):
        values = _string_items(data.get(key))
        if values:
            refs.append("<li><strong>{}</strong>: {}</li>".format(escape(label), escape(", ".join(values))))
    if refs:
        sections.extend(
            [
                '<section class="result-section">',
                "<h3>Pipeline References</h3>",
                '<ul class="result-actions">{}</ul>'.format("".join(refs)),
                "</section>",
            ]
        )
    return sections


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


def settings_group(title: str, rows: Sequence[str]) -> str:
    return (
        '<div class="settings-group">'
        "<h3>{}</h3>"
        '<div class="settings-rows">{}</div>'
        "</div>"
    ).format(
        escape(title),
        "".join(rows),
    )


def settings_text_row(
    key: str,
    label: str,
    settings: Mapping[str, Any],
    *,
    helper: str,
    input_type: str = "text",
) -> str:
    return (
        '<label class="setting-row setting-row-text">'
        "{}"
        '<span class="setting-control"><input type="{}" name="{}" value="{}"></span>'
        "</label>"
    ).format(
        settings_row_copy(label, key, helper),
        escape(input_type),
        escape(key),
        escape(settings_form_value(settings.get(key))),
    )


def settings_checkbox_row(
    key: str,
    label: str,
    settings: Mapping[str, Any],
    *,
    helper: str,
) -> str:
    checked_attr = " checked" if bool(settings.get(key)) else ""
    return (
        '<div class="setting-row setting-row-checkbox">'
        "{}"
        '<span class="setting-control">'
        '<input type="hidden" name="{}" value="false">'
        '<label class="checkline"><input type="checkbox" name="{}" value="true"{}>{}</label>'
        "</span>"
        "</div>"
    ).format(
        settings_row_copy(label, key, helper),
        escape(key),
        escape(key),
        checked_attr,
        escape(label),
    )


def settings_locked_row(label: str, key: str, *, helper: str) -> str:
    return (
        '<div class="setting-row setting-row-locked">'
        "{}"
        '<span class="setting-control">'
        '<label class="checkline locked-control">'
        '<input type="checkbox" checked disabled>Locked ON'
        "</label>"
        "</span>"
        "</div>"
    ).format(settings_row_copy(label, key, helper))


def settings_row_copy(label: str, key: str, helper: str) -> str:
    return (
        '<span class="setting-copy">'
        "<strong>{}</strong>"
        "<code>{}</code>"
        '<span class="setting-helper">{}</span>'
        "</span>"
    ).format(
        escape(label),
        escape(key),
        escape(helper),
    )


def settings_form_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


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
    .badge.warn, .badge.planned, .badge.blocked, .badge.in_review, .badge.stale, .badge.unknown {{
      background: var(--warn-soft);
      color: var(--warn);
    }}
    .badge.fail, .badge.changes_requested, .badge.write, .badge.missing {{
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
    .execution-status {{
      display: grid;
      gap: 14px;
    }}
    .execution-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
      gap: 10px;
    }}
    .execution-item {{
      display: grid;
      gap: 6px;
      align-content: start;
      min-height: 92px;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 10px;
      background: #fbfcfe;
    }}
    .execution-item > span {{
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: .04em;
    }}
    .execution-item code {{
      overflow-wrap: anywhere;
    }}
    .execution-item p {{
      margin: 0;
    }}
    .execution-actions {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 10px;
    }}
    .execution-actions form {{
      display: grid;
      gap: 8px;
      align-content: end;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 10px;
      background: #f8fafc;
    }}
    .execution-warnings {{
      margin: 0;
      padding-left: 18px;
      color: var(--warn);
    }}
    .execution-warnings li {{
      margin: 4px 0;
    }}
    .health-message {{
      min-width: 260px;
      overflow-wrap: anywhere;
    }}
    .health-actions form {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
      min-width: 220px;
    }}
    .health-actions button {{
      min-width: 120px;
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
    .settings-panel form {{
      display: grid;
      gap: 18px;
    }}
    .settings-panel-header {{
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      gap: 12px;
      align-items: flex-start;
    }}
    .settings-panel-header h2 {{
      margin-bottom: 4px;
    }}
    .settings-group {{
      border-top: 1px solid var(--line);
      padding-top: 14px;
    }}
    .settings-group h3 {{
      margin: 0 0 8px;
      font-size: 15px;
    }}
    .settings-rows {{
      display: grid;
    }}
    .setting-row {{
      display: grid;
      grid-template-columns: minmax(190px, 1fr) minmax(220px, 1fr);
      gap: 14px;
      align-items: center;
      padding: 12px 0;
      border-top: 1px solid #edf1f6;
      color: var(--text);
      text-transform: none;
      letter-spacing: 0;
    }}
    .setting-row:first-child {{
      border-top: 0;
    }}
    .setting-copy {{
      display: grid;
      gap: 4px;
      min-width: 0;
    }}
    .setting-copy strong {{
      font-size: 14px;
    }}
    .setting-copy code {{
      width: max-content;
      max-width: 100%;
      overflow-wrap: anywhere;
    }}
    .setting-helper {{
      color: var(--muted);
      font-size: 12px;
    }}
    .setting-control {{
      min-width: 0;
    }}
    .setting-control .checkline {{
      justify-content: flex-start;
    }}
    .locked-control {{
      color: #0d5f59;
      font-weight: 700;
    }}
    .settings-footer {{
      display: flex;
      flex-wrap: wrap;
      justify-content: flex-end;
      gap: 10px;
      align-items: center;
      border-top: 1px solid var(--line);
      padding-top: 16px;
    }}
    .pipeline-progress {{
      height: 12px;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: #eef2f7;
      overflow: hidden;
      margin-bottom: 10px;
    }}
    .pipeline-progress span {{
      display: block;
      height: 100%;
      background: var(--accent);
    }}
    .pipeline-action-groups {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 14px;
    }}
    .pipeline-action-group {{
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fbfcfe;
      padding: 12px;
      min-width: 0;
    }}
    .pipeline-action-group h3 {{
      margin: 0 0 8px;
      font-size: 14px;
    }}
    .restricted-actions {{
      border-color: #f0c7c7;
      background: #fff8f8;
    }}
    .pipeline-step {{
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
      margin-bottom: 10px;
      overflow: hidden;
    }}
    .pipeline-step summary {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: center;
      cursor: pointer;
      padding: 10px 12px;
      background: #f1f4f8;
    }}
    .pipeline-step > div {{
      padding: 12px;
    }}
    .pipeline-step h3 {{
      margin: 14px 0 8px;
      font-size: 14px;
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
      .setting-row {{ grid-template-columns: 1fr; }}
      .settings-footer {{ justify-content: stretch; }}
      .settings-footer .button-link, .settings-footer button {{ flex: 1 1 160px; }}
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


def project_health_panel(
    data: Mapping[str, Any],
    *,
    selected_task: Mapping[str, Any] | None = None,
) -> str:
    health = _mapping(data.get("health"))
    doctor = _mapping(health.get("doctor"))
    artifacts = [
        artifact
        for artifact in health.get("artifacts") or []
        if isinstance(artifact, Mapping)
    ]
    items = ([doctor] if doctor else []) + artifacts
    rows = []
    for item in items:
        detail = str(item.get("message") or item.get("reason") or "")
        path = str(item.get("path") or "")
        if path:
            detail = "{}{}".format(
                "{} ".format(detail) if detail else "",
                path,
            ).strip()
        rows.append(
            "<tr><td>{}</td><td>{}</td><td class=\"health-message\">{}</td><td class=\"health-actions\">{}</td></tr>".format(
                escape(item.get("label") or item.get("key") or ""),
                status_badge(str(item.get("status") or "UNKNOWN")),
                escape(detail),
                health_action_control(item, selected_task=selected_task),
            )
        )
    return (
        '<section class="panel health-panel">'
        "<h2>Project Health</h2>"
        "{}"
        "</section>"
    ).format(
        table(("Area", "Status", "Signal", "Repair / Check"), rows, "No health signals.")
    )


def health_action_control(
    item: Mapping[str, Any],
    *,
    selected_task: Mapping[str, Any] | None = None,
) -> str:
    action = str(item.get("action") or "")
    if not action:
        return '<p class="empty">No action.</p>'
    target_action = action in {
        "task.refresh_execution_context",
        "codex.prompt.build",
        "context.build",
    }
    if item.get("available") is False and not target_action:
        return '<p class="empty">{}</p>'.format(
            escape(item.get("reason") or "Action unavailable.")
        )

    fields: list[str] = []
    if target_action:
        task_ref, reason = health_action_task_ref(item, selected_task=selected_task)
        if not task_ref:
            return '<p class="empty">{}</p>'.format(escape(reason))
        fields.append(hidden_field("task", task_ref))
        if action == "codex.prompt.build":
            fields.append(hidden_field("with_context", "yes"))

    return action_form(
        action,
        fields,
        button_label=str(item.get("action_label") or action),
    )


def health_action_task_ref(
    item: Mapping[str, Any],
    *,
    selected_task: Mapping[str, Any] | None = None,
) -> tuple[str, str]:
    item_task = str(item.get("task") or "")
    if selected_task is not None:
        selected_ref = str(selected_task.get("ref") or selected_task.get("id") or "")
        if not selected_ref:
            return "", "No safe target task exists."

        status = str(selected_task.get("status") or "")
        if status not in TASK_REPAIR_STATUSES:
            return "", "No safe target task exists."

        selected_refs = {
            str(selected_task.get(field) or "")
            for field in ("id", "ref", "legacy_id")
            if selected_task.get(field)
        }
        if status == "in_review" and item_task not in selected_refs:
            return "", "No safe target task exists."
        return selected_ref, ""

    if item_task:
        return item_task, ""
    return "", "No safe target task exists."


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


def epic_completion_cell(epic: Mapping[str, Any]) -> str:
    completion = _mapping(epic.get("task_completion"))
    counts = _mapping(completion.get("counts"))
    total = int(completion.get("total") or 0)
    closed = int(completion.get("closed") or 0)
    open_count = int(completion.get("open") or 0)
    incomplete_tasks = [
        task
        for task in completion.get("incomplete_tasks") or []
        if isinstance(task, Mapping)
    ]
    count_items = [
        "<li>{} {}</li>".format(escape(status), escape(count))
        for status, count in sorted(counts.items(), key=lambda item: status_sort_key(str(item[0])))
    ]
    parts = [
        '<div class="epic-completion">',
        "<strong>{} / {} closed</strong>".format(escape(closed), escape(total)),
        '<span class="muted">{} open</span>'.format(escape(open_count)),
    ]
    if count_items:
        parts.append('<ul class="compact-list">{}</ul>'.format("".join(count_items)))
    if incomplete_tasks:
        parts.append(
            '<ul class="compact-list">{}</ul>'.format(
                "".join(
                    "<li>{} {}</li>".format(
                        escape(task.get("ref") or task.get("id") or ""),
                        status_badge(str(task.get("status") or "unknown")),
                    )
                    for task in incomplete_tasks[:5]
                )
            )
        )
    parts.append("</div>")
    return "".join(parts)


def epic_open_changes_cell(epic: Mapping[str, Any]) -> str:
    hints = _mapping(epic.get("pipeline_hints"))
    changes = [
        change
        for change in hints.get("linked_changes") or []
        if isinstance(change, Mapping)
    ]
    if not changes:
        return '<span class="muted">none</span>'
    items = []
    for change in changes[:5]:
        label = "{} {}".format(
            change.get("id") or "",
            change.get("status") or "unknown",
        ).strip()
        title = str(change.get("title") or "")
        items.append(
            "<li><strong>{}</strong>{}</li>".format(
                escape(label),
                " {}".format(escape(title)) if title else "",
            )
        )
    if len(changes) > 5:
        items.append("<li>+{} more</li>".format(escape(len(changes) - 5)))
    return '<ul class="compact-list">{}</ul>'.format("".join(items))


def epic_row_actions(epic: Mapping[str, Any], data: Mapping[str, Any]) -> str:
    action_id = "epic.close_if_complete"
    if entity_action_available(epic, action_id) is not True:
        return '<span class="pill">No row workflows</span>'
    epic_ref = str(epic.get("key") or epic.get("id") or "")
    workflow = workflow_by_name(data).get(action_id) or {}
    return (
        '<details class="row-action row-action-{}">'
        "<summary>Close Epic If Complete</summary>"
        "{}"
        "{}"
        "</details>"
    ).format(
        escape(css_token(action_id)),
        workflow_preview_html(workflow),
        action_form(
            action_id,
            [hidden_field("epic", epic_ref)],
            button_label="Close Epic If Complete",
        ),
    )


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


def execution_status_panel(
    data: Mapping[str, Any],
    *,
    selected_task: Mapping[str, Any] | None = None,
    show_actions: bool = True,
) -> str:
    context = _mapping(data.get("execution_context"))
    current = _mapping(context.get("current_task") or data.get("current_task"))
    prompt = _mapping(context.get("prompt"))
    pack = _mapping(context.get("context_pack"))
    warnings = _string_items(context.get("warnings"))
    selected_warning = _selected_task_warning(current, selected_task or {})
    if selected_warning:
        warnings.insert(0, selected_warning)

    parts = ['<div class="execution-status">']
    parts.append(current_execution_task_line(current))
    parts.append(
        '<div class="execution-grid">{}{}{}{} </div>'.format(
            execution_status_item(
                "Codex Prompt",
                str(prompt.get("status") or "unknown"),
                str(prompt.get("path") or "AI_PROJECT/generated/CODEX_PROMPT.md"),
                str(prompt.get("reason") or ""),
            ),
            execution_status_item(
                "Context Pack",
                str(pack.get("status") or "unknown"),
                str(pack.get("path") or "AI_PROJECT/generated/CONTEXT_PACK.md"),
                str(pack.get("reason") or ""),
            ),
            execution_status_item(
                "Prompt Code",
                str(prompt.get("code") or prompt.get("raw_status") or "unknown"),
                str(context.get("updated_at") or ""),
                "",
            ),
            execution_status_item(
                "Context Task",
                str(pack.get("task_id") or "unknown"),
                _revision_detail(pack),
                "",
            ),
        )
    )
    copy_instruction = str(prompt.get("copy_instruction") or "")
    if copy_instruction:
        parts.append(
            '<label class="copy-field">Copy Codex Instruction'
            '<textarea readonly rows="2">{}</textarea></label>'.format(
                escape(copy_instruction)
            )
        )
    if current and show_actions:
        parts.append(execution_action_controls(current))
    if warnings:
        parts.append(
            '<ul class="execution-warnings">{}</ul>'.format(
                "".join("<li>{}</li>".format(escape(warning)) for warning in warnings)
            )
        )
    parts.append("</div>")
    return "".join(parts)


def current_execution_task_line(task: Mapping[str, Any]) -> str:
    if not task:
        return '<p class="empty">No current task selected.</p>'
    return (
        '<div class="status-row execution-current">{}'
        '<strong>{}</strong><code>{}</code><span>{}</span></div>'
    ).format(
        status_badge(str(task.get("status") or "unknown")),
        escape(task.get("ref") or task.get("id") or ""),
        escape(task.get("legacy_id") or task.get("id") or ""),
        escape(task.get("title") or ""),
    )


def execution_status_item(
    label: str,
    status: str,
    detail: str,
    reason: str,
) -> str:
    return (
        '<div class="execution-item">'
        "<span>{}</span>{}<code>{}</code>{}"
        "</div>"
    ).format(
        escape(label),
        status_badge(status),
        escape(detail),
        '<p class="muted">{}</p>'.format(escape(reason)) if reason else "",
    )


def execution_action_controls(current: Mapping[str, Any]) -> str:
    task_ref = str(current.get("ref") or current.get("id") or "")
    return (
        '<div class="execution-actions">'
        "{}{}{}"
        "</div>"
    ).format(
        action_form(
            "task.refresh_execution_context",
            [hidden_field("task", task_ref)],
            button_label="Refresh Context",
        ),
        action_form(
            "codex.prompt.build",
            [
                hidden_field("task", task_ref),
                hidden_field("with_context", "yes"),
            ],
            button_label="Refresh Prompt",
        ),
        action_form(
            "current.clear",
            [],
            button_label="Clear Current",
        ),
    )


def _selected_task_warning(
    current: Mapping[str, Any],
    selected_task: Mapping[str, Any],
) -> str:
    if not selected_task:
        return ""
    selected_label = str(selected_task.get("ref") or selected_task.get("id") or "")
    if not current:
        return "Selected task {} is not the current task; no current task is selected.".format(
            selected_label
        )
    if task_ref_matches(current, selected_label):
        return ""
    current_label = str(current.get("ref") or current.get("id") or "")
    return "Selected task {} differs from current task {}.".format(
        selected_label,
        current_label,
    )


def _revision_detail(pack: Mapping[str, Any]) -> str:
    parts = []
    if pack.get("tasks_revision") is not None:
        parts.append("tasks rev {}".format(pack.get("tasks_revision")))
    if pack.get("docs_revision") is not None:
        parts.append("docs rev {}".format(pack.get("docs_revision")))
    return ", ".join(parts) or "not reported"


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
    controls = []
    run_control = task_row_run_control(task, data)
    if run_control:
        controls.append(run_control)
    controls.extend(task_row_action(task, data, spec) for spec in specs)
    if not controls:
        return '<span class="pill">No row workflows</span>'
    return '<div class="row-actions">{}</div>'.format("".join(controls))


def task_row_run_control(task: Mapping[str, Any], data: Mapping[str, Any]) -> str:
    status = str(task.get("status") or "")
    if status in TASK_ROW_INACTIVE_STATUSES:
        return ""
    if status in TASK_ROW_RUN_STATUSES:
        return task_row_start_control(task)
    if status == "in_progress":
        return task_row_continue_control(task, data)
    return ""


def task_row_start_control(task: Mapping[str, Any]) -> str:
    task_ref = str(task.get("ref") or task.get("id") or "")
    if not task_ref:
        return ""
    return (
        '<details class="row-action row-action-run">'
        "<summary>Run</summary>"
        "{}{}"
        "</details>"
    ).format(
        task_row_change_guidance(task),
        action_form(
            "ui.run_selected_task",
            [hidden_field("task", task_ref)],
            button_label="Run",
        ),
    )


def task_row_continue_control(
    task: Mapping[str, Any],
    data: Mapping[str, Any],
) -> str:
    session = task_row_pipeline_session(task, data)
    if not session:
        return (
            '<div class="row-action row-action-continue">'
            "{}"
            '<p class="muted">Continue from Pipeline after a session exists for this task.</p>'
            "</div>"
        ).format(task_row_change_guidance(task))

    session_id = str(session.get("id") or "")
    status = str(session.get("status") or "unknown")
    if session_id and status in PIPELINE_RESUMABLE_STATUSES:
        return task_row_session_control(
            task,
            session_id,
            label="Resume",
            guidance=pipeline_session_action_guidance(session),
        )
    if session_id and status in PIPELINE_RUNNABLE_STATUSES:
        return task_row_session_control(
            task,
            session_id,
            label="Continue",
            guidance=pipeline_session_action_guidance(session),
        )
    guidance = pipeline_session_action_guidance(session)
    if not guidance:
        guidance = (
            '<p class="muted">Continue is unavailable for pipeline session status {}.</p>'.format(
                escape(status)
            )
        )
    return (
        '<div class="row-action row-action-continue">'
        "{}{}"
        "</div>"
    ).format(task_row_change_guidance(task), guidance)


def task_row_session_control(
    task: Mapping[str, Any],
    session_id: str,
    *,
    label: str,
    guidance: str = "",
) -> str:
    return (
        '<details class="row-action row-action-continue">'
        "<summary>{}</summary>"
        "{}{}{}"
        "</details>"
    ).format(
        escape(label),
        task_row_change_guidance(task),
        guidance,
        action_form(
            "pipeline.run_next",
            [hidden_field("session_id", session_id)],
            button_label=label,
        ),
    )


def task_row_pipeline_session(
    task: Mapping[str, Any],
    data: Mapping[str, Any],
) -> Mapping[str, Any]:
    pipeline = _mapping(data.get("pipeline"))
    sessions: list[Mapping[str, Any]] = []
    current = _mapping(pipeline.get("current_session"))
    if current:
        sessions.append(current)
    seen = {str(current.get("id") or "")} if current else set()
    for raw_session in pipeline.get("sessions") or []:
        session = _mapping(raw_session)
        session_id = str(session.get("id") or "")
        if session and session_id not in seen:
            sessions.append(session)
            seen.add(session_id)

    matched = [
        session
        for session in sessions
        if pipeline_session_matches_task(session, task)
    ]
    for session in matched:
        status = str(session.get("status") or "")
        if status in PIPELINE_RUNNABLE_STATUSES or status in PIPELINE_RESUMABLE_STATUSES:
            return session
    return matched[0] if matched else {}


def pipeline_session_matches_task(
    session: Mapping[str, Any],
    task: Mapping[str, Any],
) -> bool:
    refs = set(task_ref_values(task))
    if not refs:
        return False
    direct_refs = {
        str(session.get("current_task_id") or ""),
        str(session.get("current_task_ref") or ""),
    }
    if refs.intersection(ref for ref in direct_refs if ref):
        return True
    queue = _mapping(session.get("selected_queue"))
    return bool(refs.intersection(_string_items(queue.get("task_refs"))))


def task_row_change_guidance(task: Mapping[str, Any]) -> str:
    hints = _mapping(task.get("pipeline_hints"))
    if not hints.get("requires_evolution_change"):
        return ""
    linked_changes = [
        change
        for change in hints.get("linked_changes") or []
        if isinstance(change, Mapping)
    ]
    if any(
        str(change.get("status") or "") in TASK_ROW_APPROVED_CHANGE_STATUSES
        for change in linked_changes
    ):
        return ""
    if linked_changes:
        detail = "Linked Change: {}.".format(
            ", ".join(
                "{} {}".format(
                    str(change.get("id") or "unknown"),
                    str(change.get("status") or "unknown"),
                ).strip()
                for change in linked_changes
            )
        )
    else:
        detail = "No linked Evolution Change is available."
    return (
        '<p class="muted"><strong>Owner guidance:</strong> '
        "Requires approved linked Evolution Change before execution. {}</p>"
    ).format(escape(detail))


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


def pipeline_query_options(query: Mapping[str, Sequence[str]]) -> dict[str, Any]:
    max_tasks_text = _query_value(query, "max_tasks")
    max_tasks = int(max_tasks_text) if max_tasks_text.isdigit() else None
    order_by = _query_value(query, "order_by") or "execution"
    if order_by not in {"execution", "owner", "selected"}:
        order_by = "execution"
    return {
        "policy_name": _query_value(query, "policy") or "dry_run",
        "task_refs": _query_items(query, "task_ref"),
        "epic_ids": _query_items(query, "epic"),
        "statuses": _query_items(query, "status"),
        "max_tasks": max_tasks,
        "order_by": order_by,
        "auto_create_missing_changes": _query_enabled(
            query,
            "auto_create_missing_changes",
        ),
        "owner_approve_required_changes": _query_enabled(
            query,
            "owner_approve_required_changes",
        ),
        "approval_note": _query_value(query, "approval_note") or "",
        "auto_close_note": _query_value(query, "auto_close_note") or "",
    }


def _query_items(query: Mapping[str, Sequence[str]], name: str) -> tuple[str, ...]:
    items: list[str] = []
    for value in query.get(name) or ():
        for line in str(value).splitlines():
            for item in line.split(","):
                text = item.strip()
                if text:
                    items.append(text)
    return tuple(items)


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
    multipart: bool = False,
) -> str:
    confirm_required_attr = " required" if confirm_required else ""
    enctype_attr = ' enctype="multipart/form-data"' if multipart else ""
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
    return '<form method="post" action="/actions"{}>{}</form>'.format(
        enctype_attr,
        "".join(controls),
    )


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


def file_input_field(name: str, label: str, *, accept: str = "") -> str:
    accept_attr = ' accept="{}"'.format(escape(accept)) if accept else ""
    return '<label>{}<input type="file" name="{}"{}></label>'.format(
        escape(label),
        escape(name),
        accept_attr,
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


def checkbox_field(name: str, label: str, *, checked: bool = False) -> str:
    checked_attr = " checked" if checked else ""
    return '<label class="checkline"><input type="checkbox" name="{}" value="yes"{}>{}</label>'.format(
        escape(name),
        checked_attr,
        escape(label),
    )


def parse_multipart_action_fields(content_type: str, body: bytes) -> dict[str, str]:
    """Parse a bounded multipart web action body without executing uploaded content."""

    header = "Content-Type: {}\r\nMIME-Version: 1.0\r\n\r\n".format(content_type)
    message = BytesParser(policy=email_policy).parsebytes(
        header.encode("utf-8", "replace") + body
    )
    if not message.is_multipart():
        raise WebActionError(
            "WEB_INVALID_MULTIPART_BODY",
            "Multipart write request body is invalid.",
        )

    fields: dict[str, str] = {}
    uploads: list[tuple[str, str, bytes]] = []
    for part in message.iter_parts():
        if part.get_content_disposition() != "form-data":
            continue
        name = part.get_param("name", header="content-disposition")
        if not name:
            continue
        payload = part.get_payload(decode=True) or b""
        filename = part.get_filename()
        if filename is None:
            try:
                fields[str(name)] = payload.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise WebActionError(
                    "WEB_MULTIPART_FIELD_NOT_UTF8",
                    "Multipart form field is not valid UTF-8.",
                    details={"field": str(name)},
                ) from exc
            continue
        if filename or payload:
            uploads.append((str(name), str(filename), payload))

    apply_import_upload(fields, uploads)
    return fields


def apply_import_upload(
    fields: dict[str, str],
    uploads: Sequence[tuple[str, str, bytes]],
) -> None:
    """Map a validated Bulk Task Import upload onto the existing import_text field."""

    if not uploads:
        return
    action = fields.get("action", "")
    if action != "task.import":
        raise WebActionError(
            "WEB_UNSUPPORTED_FILE_UPLOAD",
            "File uploads are supported only by Bulk Task Import.",
            details={"action": action or "missing"},
        )
    unexpected = sorted(
        name
        for name, _filename, _payload in uploads
        if name != WEB_IMPORT_FILE_FIELD
    )
    if unexpected:
        raise WebActionError(
            "WEB_UNSUPPORTED_FILE_UPLOAD",
            "Unsupported file upload field.",
            details={"fields": unexpected},
        )

    import_uploads = [
        (filename, payload)
        for name, filename, payload in uploads
        if name == WEB_IMPORT_FILE_FIELD
    ]
    if len(import_uploads) > 1:
        raise WebActionError(
            "WEB_IMPORT_MULTIPLE_FILES",
            "Bulk Task Import accepts one uploaded file.",
        )
    filename, payload = import_uploads[0]
    if not filename:
        raise WebActionError(
            "WEB_IMPORT_FILE_NAME_REQUIRED",
            "Uploaded import file must have a filename.",
        )
    suffix = Path(filename).suffix.lower()
    if suffix not in WEB_IMPORT_ALLOWED_SUFFIXES:
        raise WebActionError(
            "WEB_IMPORT_FILE_TYPE_REJECTED",
            "Bulk Task Import accepts only .json or .txt files.",
            details={
                "filename": filename,
                "allowed_suffixes": sorted(WEB_IMPORT_ALLOWED_SUFFIXES),
            },
        )
    if len(payload) > WEB_IMPORT_FILE_MAX_BYTES:
        raise WebActionError(
            "WEB_IMPORT_FILE_TOO_LARGE",
            "Uploaded import file is too large.",
            details={
                "filename": filename,
                "max_bytes": WEB_IMPORT_FILE_MAX_BYTES,
                "actual_bytes": len(payload),
            },
        )
    if fields.get("import_text", "").strip():
        raise WebActionError(
            "WEB_IMPORT_SOURCE_CONFLICT",
            "Use either pasted JSON or an uploaded file for Bulk Task Import.",
        )
    try:
        fields["import_text"] = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise WebActionError(
            "WEB_IMPORT_FILE_NOT_UTF8",
            "Uploaded import file must be valid UTF-8 text.",
            details={"filename": filename},
        ) from exc


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
