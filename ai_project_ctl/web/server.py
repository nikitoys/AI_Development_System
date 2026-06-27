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
from urllib.parse import parse_qs, quote, unquote, urlparse

from ai_project_ctl.core.result import CommandError
from ai_project_ctl.core.workflows import BULK_IMPORT_MAX_BYTES
from ai_project_ctl.pipeline.report_recovery import (
    draft_json,
    draft_report_from_session,
    session_supports_report_recovery,
)
from ai_project_ctl.web.actions import (
    WebActionError,
    WebActionExecutor,
    WebActionResult,
    available_actions,
)
from ai_project_ctl.web.read_model import ReadOnlyProjectModel, WebControlError
from ai_project_ctl.ui_settings import (
    ALLOW_REPORT_WARNINGS_SETTING,
    ALLOW_RELAXED_GIT_DIFF_VERIFICATION_SETTING,
    ALLOW_RELAXED_REPORT_WARNINGS_SETTING,
    BATCH_MAX_FAILURES_MAX,
    BATCH_MAX_FAILURES_MIN,
    BATCH_MAX_FAILURES_SETTING,
    BATCH_MAX_STEPS_MAX,
    BATCH_MAX_STEPS_MIN,
    BATCH_MAX_STEPS_SETTING,
    INTERNAL_CHANGE_GATE_BYPASS_SETTING,
    REQUIRE_CODEX_REVIEW_SETTING,
)


LOCAL_HOSTS = {"localhost"}
LOCAL_ADDRESSES = {"127.0.0.1", "::1"}
WEB_IMPORT_FILE_FIELD = "import_file"
WEB_IMPORT_ALLOWED_SUFFIXES = {".json", ".txt"}
WEB_IMPORT_FILE_MAX_BYTES = BULK_IMPORT_MAX_BYTES
WEB_ACTION_BODY_MAX_BYTES = WEB_IMPORT_FILE_MAX_BYTES + 16_384

NAV_GROUPS = (
    (
        "Operate",
        (
            ("/", "Owner Cockpit"),
            ("/pipeline", "Pipeline"),
            ("/tasks", "Tasks"),
            ("/reviews", "Reviews"),
            ("/commit", "Commit"),
        ),
    ),
    (
        "Plan",
        (
            ("/evolution", "Evolution"),
            ("/epics", "Epics"),
        ),
    ),
    (
        "Control",
        (
            ("/events", "Events"),
            ("/generated", "Generated"),
            ("/doctor", "Doctor"),
            ("/commands", "Commands"),
            ("/actions", "Actions"),
            ("/settings", "Settings"),
        ),
    ),
)
NAV_ITEMS = tuple(item for _, items in NAV_GROUPS for item in items)

TASK_FOCUS_STATUSES = {"ready", "in_progress", "in_review", "changes_requested"}
TASK_GROUP_OPTIONS = {"none", "epic", "status"}
TASK_VIEW_OPTIONS = {"queue", "inventory"}
TASK_QUEUE_GROUPS = (
    ("current", "Current", "Selected or in-progress work."),
    ("needs_decision", "Needs Decision", "Owner review or approval work."),
    ("ready_to_run", "Ready To Run", "Ready tasks with one safe next action."),
    ("blocked", "Blocked", "Tasks waiting on a blocker."),
    ("other_active", "Other Active", "Filtered active tasks without a primary queue action."),
)
TASK_ACTION_METRIC_GROUPS = (
    ("needs_decision", "Needs Decision"),
    ("ready_to_run", "Ready To Run"),
    ("current", "Current"),
    ("blocked", "Blocked"),
)
TASK_QUEUE_DECISION_ACTIONS = {
    "Approve Change",
    "Approve & Done",
    "Accept Change",
    "Request Changes",
}
TASK_QUEUE_DECISION_ACTION_IDS = {
    "evolution.approve_change",
    "evolution.accept_change",
    "task.close_reviewed",
    "task.request_changes",
}
TASK_QUEUE_RUN_ACTIONS = {
    "Prepare for Codex",
    "Run",
    "Run Selected Task",
    "Run selected task",
    "Run next pipeline step",
    "Run until blocker",
}
TASK_QUEUE_RUN_ACTION_IDS = {
    "task.prepare_for_codex",
    "ui.run_selected_task",
    "pipeline.run_next",
    "pipeline.run_until_blocker",
}
TASK_QUEUE_RUN_ACTION_PREFIXES = ("ui.run_", "pipeline.run_")
TASK_QUEUE_DONE_STATUSES = {"done", "archived"}
REVIEW_QUEUE_GROUPS = (
    (
        "awaiting_owner_review",
        "Awaiting Owner Review",
        "Tasks in review where the Human Owner can approve or request changes.",
    ),
    (
        "changes_requested",
        "Changes Requested",
        "Review decisions that already requested rework.",
    ),
    (
        "current",
        "Current",
        "Current or in-progress work that may become reviewable next.",
    ),
    (
        "history",
        "History",
        "Reviewed or reported tasks kept for package inspection.",
    ),
)
REVIEW_QUEUE_HISTORY_STATUSES = {"approved", "done", "archived"}
CHANGE_ACTION_STATUSES = {"ready", "approved", "in_progress", "in_review"}
CHANGE_QUEUE_APPROVED_STATUSES = {"approved", "in_progress"}
CHANGE_QUEUE_GROUPS = (
    (
        "needs_approval",
        "Needs Approval",
        "Ready Change Proposals waiting for the Human Owner approval decision.",
    ),
    (
        "approved",
        "Approved",
        "Approved or in-progress Changes that need review movement, acceptance, or inspection.",
    ),
    (
        "in_review",
        "In Review",
        "Changes whose implementation is under review and may be accepted when gates pass.",
    ),
    (
        "accepted",
        "Accepted",
        "Completed Change Proposals kept available for traceability.",
    ),
    (
        "blocked_or_other",
        "Blocked / Other",
        "Draft, deferred, rejected, superseded, archived, or otherwise blocked Changes.",
    ),
)
TASK_REPAIR_STATUSES = {"ready", "in_progress", "in_review", "changes_requested"}
PIPELINE_RUNNABLE_STATUSES = {"planned", "running"}
PIPELINE_STOPPABLE_STATUSES = {"planned", "running"}
PIPELINE_RESUMABLE_STATUSES = {"stopped", "blocked"}
PIPELINE_STATUS_POLL_STOP_STATUSES = ("blocked", "failed", "completed", "stopped")
INCOMPLETE_RUN_CONFIRM_FIELD = "incomplete_run_confirm"
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
PIPELINE_LIVE_LOG_BROWSER_LIMIT = 65_536
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
TASK_PRIMARY_TASK_ACTION_LABELS = {
    "task.prepare_for_codex": "Prepare",
    "task.refresh_execution_context": "Refresh",
    "task.submit_for_review": "Submit",
    "task.close_reviewed": "Approve & Done",
    "task.request_changes": "Request Changes",
    "evolution.create_for_task": "Create Change",
}
TASK_PRIMARY_CHANGE_ACTION_LABELS = {
    "evolution.approve_change": "Approve",
    "evolution.accept_change": "Accept Change",
}
TASK_PRIMARY_NOTE_SPECS = {
    "task.close_reviewed": {
        "notes_label": "Approval Notes",
        "notes_placeholder": "Record the Human Owner approval basis.",
    },
    "task.request_changes": {
        "notes_label": "Change Request Notes",
        "notes_placeholder": "Describe the required rework.",
    },
    "evolution.approve_change": {
        "notes_label": "Approval Notes",
        "notes_placeholder": "Record the Human Owner approval basis.",
    },
    "evolution.accept_change": {
        "notes_label": "Acceptance Notes",
        "notes_placeholder": "Record Human Owner acceptance after linked tasks are complete.",
    },
}
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
    log_tail = _pipeline_log_tail_parts(path)
    if log_tail is not None:
        session_id, phase, stream = log_tail
        try:
            payload = model.pipeline_runtime_log_tail(
                session_id,
                phase,
                stream,
                offset=_query_value(query, "offset"),
            )
            return _json_response(HTTPStatus.OK, payload)
        except WebControlError as exc:
            return _json_error_response(exc)
    status_session_id = _pipeline_session_status_id(path)
    if status_session_id is not None:
        try:
            return _json_response(
                HTTPStatus.OK,
                model.pipeline_session_live_status(status_session_id),
            )
        except WebControlError as exc:
            return _json_error_response(exc)
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
        "/tasks": lambda: render_tasks(model.dashboard(include_events=True), query=query),
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
    body = [
        owner_cockpit_summary(data),
        current_execution_bar(data),
        project_health_panel(data, compact=True),
        current_execution_details_panel(data),
        owner_queue_section(
            data,
            "needs_decision",
            "Needs Decision",
            "Owner approvals, review choices, and acceptance decisions waiting now.",
            "No owner decisions are waiting.",
            limit=6,
        ),
        owner_queue_section(
            data,
            "current",
            "Current",
            "Active task and pipeline work already in motion.",
            "No current work is active.",
            limit=4,
        ),
        owner_queue_section(
            data,
            "ready_to_run",
            "Ready To Run",
            "Work that can move forward without scanning the full task table.",
            "No runnable work is ready.",
            limit=4,
        ),
        owner_queue_section(
            data,
            "blocked",
            "Blocked",
            "Items that need a blocker removed before normal execution can continue.",
            "No blocked owner queue items.",
            limit=4,
        ),
        owner_recent_signals_panel(data),
    ]
    return render_page("Owner Cockpit", "".join(body), active="/")


def render_pipeline(
    data: Mapping[str, Any],
    *,
    query: Mapping[str, Sequence[str]] | None = None,
) -> str:
    pipeline = _mapping(data.get("pipeline"))
    selected_policy = _mapping(pipeline.get("selected_policy"))
    queue_preview = _mapping(pipeline.get("queue_preview"))
    body = [
        pipeline_run_summary_grid(pipeline),
        pipeline_run_monitor_panel(data, pipeline),
        pipeline_queue_compact_panel(pipeline),
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
            pipeline_compact_section(
                "Queue Selector and Session Setup",
                pipeline_queue_setup_panel(data, pipeline),
                summary=pipeline_queue_selector_summary(pipeline),
            ),
            pipeline_compact_section(
                "Policy Preset Preview",
                pipeline_policy_preview(selected_policy),
                summary=pipeline_policy_summary_text(selected_policy),
            ),
            pipeline_compact_section(
                "Full Queue Preview",
                pipeline_queue_preview_table(
                    queue_preview,
                    _mapping(pipeline.get("queue_error")),
                ),
                summary=pipeline_queue_full_summary(queue_preview),
            ),
            pipeline_compact_section(
                "Sessions",
                pipeline_session_table(pipeline.get("sessions") or []),
                summary=pipeline_sessions_summary(pipeline),
            ),
            pipeline_compact_section(
                "Latest Pipeline Audit",
                pipeline_audit_table(pipeline.get("audit") or []),
                summary=pipeline_audit_summary(pipeline),
            ),
        ]
    )
    return render_page("Pipeline", "".join(body), active="/pipeline")


def pipeline_run_summary_grid(pipeline: Mapping[str, Any]) -> str:
    state = _mapping(pipeline.get("state"))
    session = _mapping(pipeline.get("current_session"))
    return (
        '<section class="summary-grid pipeline-run-summary">'
        "{}{}{}{}{}{}{}{}"
        "</section>"
    ).format(
        metric("Current Session", str(state.get("current_session_id") or session.get("id") or "none")),
        metric("Session Status", str(session.get("status") or "idle")),
        metric("Current Phase", pipeline_session_current_phase(session) or "none"),
        metric("Phase Status", pipeline_session_current_phase_status(session) or "none"),
        metric("Stop Reason", pipeline_session_stop_reason(session) or "none"),
        metric("Next Action", pipeline_session_next_action(session) or "none"),
        metric("Run Health", pipeline_run_health_label(session)),
        metric("Live Logs", pipeline_live_log_label(session)),
    )


def pipeline_run_monitor_panel(data: Mapping[str, Any], pipeline: Mapping[str, Any]) -> str:
    session = _mapping(pipeline.get("current_session"))
    if session:
        progress = pipeline_status_overview(session)
        references = pipeline_compact_subsection(
            "Session References",
            pipeline_reference_list(session),
            open_panel=False,
        )
    else:
        progress = '<p class="empty">No current pipeline session.</p>'
        references = ""
    return (
        '<section class="panel pipeline-run-monitor">'
        '<div class="pipeline-run-header">'
        "<div><h2>Current Run Monitor</h2>{}</div>"
        '<div class="pipeline-run-links">{}</div>'
        "</div>"
        '<div class="pipeline-run-layout">'
        '<div class="pipeline-run-progress"><h3>Phase Progress</h3>{}</div>'
        '<div class="pipeline-run-next"><h3>Next Safe Action</h3>{}</div>'
        "</div>"
        "{}{}"
        "</section>"
    ).format(
        pipeline_current_session_identity(session),
        pipeline_session_detail_button(session),
        progress,
        pipeline_action_controls(data, pipeline),
        pipeline_current_live_log_access(session),
        references,
    )


def pipeline_current_session_identity(session: Mapping[str, Any]) -> str:
    if not session:
        return '<p class="empty">Pipeline is idle until a session is created.</p>'
    return (
        '<div class="status-row pipeline-session-identity">{}<strong>{}</strong>'
        '<span>{}</span></div>'
    ).format(
        status_badge(str(session.get("status") or "unknown")),
        escape(str(session.get("id") or "unknown session")),
        escape(
            str(
                session.get("current_task_ref")
                or session.get("current_task_id")
                or "No selected task"
            )
        ),
    )


def pipeline_session_detail_button(session: Mapping[str, Any]) -> str:
    session_id = str(session.get("id") or "")
    if not session_id:
        return '<a class="button-link secondary" href="/pipeline">Refresh Session</a>'
    href = "/pipeline/sessions/{}".format(quote(session_id, safe=""))
    return '<a class="button-link" href="{}">Open Session Detail</a>'.format(escape(href))


def pipeline_run_health_label(session: Mapping[str, Any]) -> str:
    if not session:
        return "idle"
    status = str(session.get("status") or "unknown")
    if status == "running" and pipeline_session_has_live_execute_logs(session):
        return "running, live logs"
    if status == "running":
        return "running"
    if status in {"blocked", "failed", "stopped"}:
        reason = pipeline_session_stop_reason(session)
        return "{}{}".format(status, ": {}".format(reason) if reason else "")
    if status in {"completed", "archived"}:
        return "terminal"
    return status


def pipeline_live_log_label(session: Mapping[str, Any]) -> str:
    if not session:
        return "none"
    if pipeline_session_has_live_execute_logs(session):
        return "streaming"
    if str(session.get("status") or "") == "running":
        return "session running"
    return "not running"


def pipeline_current_live_log_access(session: Mapping[str, Any]) -> str:
    if not session:
        return ""
    live_panel = ""
    if str(session.get("status") or "") == "running":
        live_panel = pipeline_current_live_log_panel(session)
    return (
        '<div class="pipeline-live-access">'
        '<div class="pipeline-live-access-header">'
        "<h3>Live Logs</h3>{}"
        "</div>"
        "{}"
        "</div>"
    ).format(
        pipeline_session_detail_button(session),
        live_panel
        or '<p class="empty">No live execute stream is attached to the current phase.</p>',
    )


def pipeline_current_live_log_panel(session: Mapping[str, Any]) -> str:
    for phase in reversed(pipeline_session_phase_rows(session)):
        artifacts = pipeline_phase_artifacts(phase)
        panel = pipeline_live_execute_log_panel(phase, session, artifacts)
        if panel:
            return panel
    return ""


def pipeline_queue_compact_panel(pipeline: Mapping[str, Any]) -> str:
    queue_preview = _mapping(pipeline.get("queue_preview"))
    queue_error = _mapping(pipeline.get("queue_error"))
    next_task = _mapping(queue_preview.get("next_task"))
    if queue_error:
        content = '<p class="empty">{}: {}</p>'.format(
            escape(queue_error.get("code") or "QUEUE_PREVIEW_FAILED"),
            escape(queue_error.get("message") or ""),
        )
    else:
        content = (
            '<div class="pipeline-queue-strip">'
            '<div class="pipeline-queue-next">{}<strong>{}</strong></div>'
            '<div class="pipeline-queue-counts">{}</div>'
            "</div>"
            "{}"
        ).format(
            status_badge("next"),
            escape(_pipeline_task_label(next_task) if next_task else "No next task"),
            pipeline_queue_count_pills(queue_preview),
            pipeline_queue_compact_table(queue_preview),
        )
    return (
        '<section class="panel pipeline-queue-compact">'
        '<div class="owner-section-header"><div><h2>Compact Queue Preview</h2>'
        '<p>Next task and near-term queue health.</p></div></div>'
        "{}"
        "</section>"
    ).format(content)


def pipeline_queue_count_pills(queue_preview: Mapping[str, Any]) -> str:
    categories = _mapping(queue_preview.get("categories"))
    pills = []
    for name, values in categories.items():
        if isinstance(values, Sequence) and not isinstance(values, (str, bytes)):
            count = len(values)
        else:
            count = 0
        pills.append(
            '<span class="pill">{}: {}</span>'.format(
                escape(str(name).replace("_", " ")),
                escape(count),
            )
        )
    return "".join(pills) or '<span class="pill">queue: 0</span>'


def pipeline_queue_compact_table(queue_preview: Mapping[str, Any]) -> str:
    items = [
        item
        for item in queue_preview.get("items") or []
        if isinstance(item, Mapping)
    ][:4]
    rows = [
        "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            status_badge(str(item.get("category") or "unknown")),
            escape(_pipeline_task_label(item)),
            status_badge(str(item.get("status") or "unknown")),
            escape(item.get("title") or ""),
        )
        for item in items
    ]
    return table(
        ("Category", "Task", "Status", "Title"),
        rows,
        "No queue preview items.",
    )


def pipeline_queue_setup_panel(data: Mapping[str, Any], pipeline: Mapping[str, Any]) -> str:
    return (
        '<div class="pipeline-detail-stack">'
        "<h3>Pipeline Queue Selector</h3>{}"
        "<h3>Session Setup</h3>{}"
        "</div>"
    ).format(
        pipeline_selector_form(data, pipeline),
        pipeline_session_create_form(data, pipeline),
    )


def pipeline_compact_section(title: str, content: str, *, summary: str = "") -> str:
    return (
        '<details class="panel pipeline-compact-section">'
        '<summary><span>{}</span><span>{}</span></summary>'
        '<div class="pipeline-compact-body">{}</div>'
        "</details>"
    ).format(
        escape(title),
        escape(summary),
        content,
    )


def pipeline_compact_subsection(title: str, content: str, *, open_panel: bool) -> str:
    open_attr = " open" if open_panel else ""
    return (
        '<details class="pipeline-compact-subsection"{}>'
        "<summary>{}</summary>{}"
        "</details>"
    ).format(open_attr, escape(title), content)


def pipeline_queue_selector_summary(pipeline: Mapping[str, Any]) -> str:
    request = _mapping(pipeline.get("queue_request"))
    policy = str(request.get("policy_name") or request.get("policy") or "dry_run")
    max_tasks = request.get("max_tasks")
    return "{} policy, max {}".format(policy, max_tasks if max_tasks is not None else "default")


def pipeline_policy_summary_text(policy: Mapping[str, Any]) -> str:
    name = str(policy.get("name") or "unknown")
    behavior = str(policy.get("behavior_label") or "")
    return "{}{}".format(name, " - {}".format(behavior) if behavior else "")


def pipeline_queue_full_summary(queue_preview: Mapping[str, Any]) -> str:
    items = [
        item
        for item in queue_preview.get("items") or []
        if isinstance(item, Mapping)
    ]
    return "{} preview items".format(len(items))


def pipeline_sessions_summary(pipeline: Mapping[str, Any]) -> str:
    sessions = [
        session
        for session in pipeline.get("sessions") or []
        if isinstance(session, Mapping)
    ]
    return "{} sessions".format(len(sessions))


def pipeline_audit_summary(pipeline: Mapping[str, Any]) -> str:
    events = [
        event
        for event in pipeline.get("audit") or []
        if isinstance(event, Mapping)
    ]
    return "{} audit entries".format(len(events))


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
    session_id = str(session.get("id") or "")
    body = [
        '<section class="summary-grid" data-pipeline-session-summary>',
        metric("Session", session_id),
        metric("Status", status, data_field="status"),
        metric("Policy", str(session.get("policy") or "unknown")),
        metric("Current Task", current_task or "none"),
        metric("Current Step", str(session.get("current_step") or "none")),
        metric("Current Phase", pipeline_session_current_phase(session) or "none", data_field="current_phase"),
        metric("Phase Status", pipeline_session_current_phase_status(session) or "none", data_field="current_phase_status"),
        metric("Stop Reason", pipeline_session_stop_reason(session) or "none", data_field="stop_reason"),
        metric("Next Action", pipeline_session_next_action(session) or "none", data_field="next_action"),
        metric("Started", str(session.get("started_at") or "not started")),
        metric("Updated", str(session.get("updated_at") or ""), data_field="updated_at"),
        metric("Finished", str(session.get("finished_at") or "not finished")),
        metric("Elapsed", pipeline_elapsed_label(session)),
        metric("Auto-refresh", auto_refresh, data_field="polling"),
        "</section>",
        pipeline_session_auto_refresh(session),
        '<section class="panel">',
        "<h2>Status Overview</h2>",
        '<div data-pipeline-status-overview-content>',
        pipeline_status_overview(session),
        "</div>",
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
    attrs = pipeline_session_poll_attrs(session)
    if status == "running":
        if pipeline_session_has_live_execute_logs(session):
            return (
                '<section class="panel auto-refresh" {} data-live-log-refresh="active">'
                '<div class="status-row">{}<strong data-pipeline-poll-state-label>Status polling active</strong>'
                '<span data-pipeline-poll-state-detail>Polling status every 2 seconds while Codex Execute logs are streaming.</span></div>'
                "{}"
                "</section>"
            ).format(attrs, status_badge(status), pipeline_session_status_script())
        return (
            '<section class="panel auto-refresh" {}>'
            '<div class="status-row">{}<strong data-pipeline-poll-state-label>Status polling active</strong>'
            '<span data-pipeline-poll-state-detail>Polling this session every 2 seconds.</span></div>'
            "{}"
            "</section>"
        ).format(attrs, status_badge(status), pipeline_session_status_script())
    return (
        '<section class="panel auto-refresh stopped" {}>'
        '<div class="status-row">{}<strong data-pipeline-poll-state-label>Auto-refresh stopped</strong>'
        '<span data-pipeline-poll-state-detail>Session state is terminal or waiting for owner action.</span></div>'
        "</section>"
    ).format(attrs, status_badge(status))


def pipeline_session_poll_attrs(session: Mapping[str, Any]) -> str:
    session_id = str(session.get("id") or "")
    status = str(session.get("status") or "unknown")
    status_url = "/pipeline/sessions/{}/status.json".format(quote(session_id, safe=""))
    poll_enabled = "1" if status == "running" else "0"
    stop_statuses = " ".join(PIPELINE_STATUS_POLL_STOP_STATUSES)
    auto_refresh_attr = ' data-auto-refresh="2"' if poll_enabled == "1" else ""
    return (
        'data-pipeline-session-poll{auto_refresh_attr} data-session-id="{session_id}" '
        'data-status-url="{status_url}" data-poll-ms="2000" '
        'data-stop-statuses="{stop_statuses}" data-poll-enabled="{poll_enabled}" '
        'data-session-status="{status}"'
    ).format(
        auto_refresh_attr=auto_refresh_attr,
        session_id=escape(session_id),
        status_url=escape(status_url),
        stop_statuses=escape(stop_statuses),
        poll_enabled=escape(poll_enabled),
        status=escape(status),
    )


def pipeline_session_status_script() -> str:
    return """
<script>
(function() {
  function startPipelineSessionStatusPolling() {
    var panels = document.querySelectorAll("[data-pipeline-session-poll]");
    panels.forEach(function(panel) {
      if (panel.dataset.pollStarted === "1") {
        return;
      }
      panel.dataset.pollStarted = "1";
      var pollMs = Number(panel.dataset.pollMs || "2000");
      var statusUrl = panel.dataset.statusUrl || "";
      var stopStatuses = {};
      String(panel.dataset.stopStatuses || "").split(/\\s+/).forEach(function(status) {
        if (status) {
          stopStatuses[status] = true;
        }
      });
      function normalized(value) {
        return String(value || "unknown").trim().toLowerCase();
      }
      function shouldStop(status) {
        return Boolean(stopStatuses[normalized(status)]);
      }
      function cssToken(value) {
        return normalized(value).replace(/\\s+/g, "_");
      }
      function clear(element) {
        while (element && element.firstChild) {
          element.removeChild(element.firstChild);
        }
      }
      function updateMetric(name, value) {
        var target = document.querySelector(
          '[data-pipeline-status-field="' + name + '"] strong'
        );
        if (target) {
          target.textContent = value || "none";
        }
      }
      function updatePollBadge(status) {
        var badge = panel.querySelector(".status-row .badge");
        if (badge) {
          badge.className = "badge " + cssToken(status);
          badge.textContent = status || "unknown";
        }
      }
      function setPollState(label, detail) {
        var labelTarget = panel.querySelector("[data-pipeline-poll-state-label]");
        var detailTarget = panel.querySelector("[data-pipeline-poll-state-detail]");
        if (labelTarget) {
          labelTarget.textContent = label;
        }
        if (detailTarget) {
          detailTarget.textContent = detail;
        }
      }
      function statusBadge(status) {
        var element = document.createElement("span");
        element.className = "badge " + cssToken(status);
        element.textContent = status || "unknown";
        return element;
      }
      function appendCell(row, value) {
        var cell = document.createElement("td");
        cell.textContent = value || "";
        row.appendChild(cell);
        return cell;
      }
      function updatePhaseOverview(payload) {
        var target = document.querySelector("[data-pipeline-status-overview-content]");
        if (!target) {
          return;
        }
        var phaseHistory = payload.phase_history || {};
        var total = Number(phaseHistory.total || "0");
        var denominator = 7;
        var percent = denominator ? Math.min(100, Math.floor((total / denominator) * 100)) : 0;
        var recent = Array.isArray(phaseHistory.recent) ? phaseHistory.recent : [];
        if (!total && !recent.length) {
          return;
        }
        clear(target);

        var progress = document.createElement("div");
        progress.className = "pipeline-progress";
        progress.setAttribute("aria-label", "Pipeline phase progress");
        var fill = document.createElement("span");
        fill.style.width = String(percent) + "%";
        progress.appendChild(fill);
        target.appendChild(progress);

        var summary = document.createElement("p");
        summary.className = "muted";
        summary.textContent = String(total) + " of " + String(denominator)
          + " pipeline phases have recorded outcomes.";
        target.appendChild(summary);

        if (!recent.length) {
          var empty = document.createElement("p");
          empty.className = "empty";
          empty.textContent = "No phases recorded.";
          target.appendChild(empty);
          return;
        }

        var table = document.createElement("table");
        var thead = document.createElement("thead");
        var headRow = document.createElement("tr");
        ["Phase", "Status", "Reason", "Next Action"].forEach(function(label) {
          var head = document.createElement("th");
          head.textContent = label;
          headRow.appendChild(head);
        });
        thead.appendChild(headRow);
        table.appendChild(thead);

        var tbody = document.createElement("tbody");
        recent.forEach(function(phase) {
          var row = document.createElement("tr");
          appendCell(row, phase.label || phase.phase || "Unknown Phase");
          var statusCell = document.createElement("td");
          statusCell.appendChild(statusBadge(phase.status || "unknown"));
          row.appendChild(statusCell);
          appendCell(row, phase.reason || phase.blocked_by || "");
          appendCell(row, phase.next_action || "");
          tbody.appendChild(row);
        });
        table.appendChild(tbody);
        target.appendChild(table);
      }
      function ownerMessage(payload) {
        var status = normalized(payload.status);
        if (payload.next_action) {
          return {prefix: "Owner guidance:", text: payload.next_action};
        }
        if (status === "failed") {
          return {
            text: "Session failed and is not running. Inspect the failure evidence before starting a new session."
          };
        }
        if (status === "blocked") {
          return {text: "Session is blocked and waiting for owner action."};
        }
        if (status === "stopped") {
          return {text: "Session is stopped and can be resumed."};
        }
        if (status === "completed" || status === "archived") {
          return {text: "Session is terminal."};
        }
        return null;
      }
      function updateOwnerNextAction(payload) {
        var target = document.querySelector("[data-pipeline-owner-next-action]");
        if (!target) {
          return;
        }
        var message = ownerMessage(payload);
        clear(target);
        if (!message) {
          target.hidden = true;
          return;
        }
        target.hidden = false;
        var paragraph = document.createElement("p");
        paragraph.className = "muted";
        if (message.prefix) {
          var strong = document.createElement("strong");
          strong.textContent = message.prefix;
          paragraph.appendChild(strong);
          paragraph.appendChild(document.createTextNode(" " + message.text));
        } else {
          paragraph.textContent = message.text;
        }
        target.appendChild(paragraph);
      }
      function applyStatus(payload) {
        if (!payload || !payload.ok) {
          throw new Error("status payload failed");
        }
        var status = payload.status || "unknown";
        panel.dataset.sessionStatus = status;
        updatePollBadge(status);
        updateMetric("status", status);
        updateMetric("current_phase", payload.current_phase || "none");
        updateMetric("current_phase_status", payload.current_phase_status || "none");
        updateMetric("stop_reason", payload.stop_reason || "none");
        updateMetric("next_action", payload.next_action || "none");
        updatePhaseOverview(payload);
        updateOwnerNextAction(payload);
        if (shouldStop(status)) {
          updateMetric("polling", "stopped");
          setPollState(
            "Auto-refresh stopped",
            "Session state is terminal or waiting for owner action."
          );
        }
      }
      function tick() {
        fetch(statusUrl, {cache: "no-store", headers: {"Accept": "application/json"}})
          .then(function(response) { return response.json(); })
          .then(function(payload) {
            applyStatus(payload);
            if (!shouldStop(payload.status)) {
              window.setTimeout(tick, pollMs);
            }
          })
          .catch(function(error) {
            setPollState("Status polling paused", error.message);
            window.setTimeout(tick, 5000);
          });
      }
      if (!statusUrl || panel.dataset.pollEnabled !== "1" || shouldStop(panel.dataset.sessionStatus)) {
        return;
      }
      window.setTimeout(tick, pollMs);
    });
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", startPipelineSessionStatusPolling);
  } else {
    startPipelineSessionStatusPolling();
  }
})();
</script>"""


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
        pipeline_session_owner_next_action(session),
    ]
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

    report_recovery = pipeline_report_recovery_action(data)
    if report_recovery:
        parts.append(report_recovery)

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


def pipeline_report_recovery_action(data: Mapping[str, Any]) -> str:
    session = _mapping(data.get("session"))
    raw_session = _mapping(session.get("raw")) or session
    if not raw_session or not session_supports_report_recovery(raw_session):
        return ""
    task = _mapping(data.get("task"))
    if not task:
        return (
            '<section class="report-recovery">'
            "<h4>Report Recovery</h4>"
            '<p class="empty">Report recovery is unavailable because the selected task was not found.</p>'
            "</section>"
        )

    draft = draft_report_from_session(raw_session, task)
    warning_items = "".join(
        "<li>{}</li>".format(escape(warning)) for warning in draft.warnings
    )
    inferred = ", ".join(draft.inferred_fields) or "none"
    return (
        '<section class="report-recovery">'
        "<h4>Report Recovery</h4>"
        '<p class="callout">REPORT_MISSING recovery draft. Review before confirming; '
        "the draft uses inferred fields and estimated token_usage.</p>"
        '<div class="review-grid">{}{}{}</div>'
        '<ul class="hint-list">{}</ul>'
        '<details class="result-technical" open>'
        "<summary>Draft structured report JSON</summary>"
        "<pre>{}</pre>"
        "</details>"
        "{}"
        "</section>"
    ).format(
        review_field("Selected Task ID", escape(draft.task_id)),
        review_field("Selected Task Ref", escape(draft.task_ref)),
        review_field("Inferred Fields", escape(inferred)),
        warning_items,
        escape(draft_json(draft)),
        action_form(
            "pipeline.report_recovery.submit",
            [
                hidden_field("session_id", draft.session_id),
                hidden_field("task_id", draft.task_id),
                hidden_field("task_ref", draft.task_ref),
            ],
            button_label="Submit recovered report",
        ),
    )


def pipeline_step_details(session: Mapping[str, Any]) -> str:
    phase_rows = pipeline_session_phase_rows(session)
    if phase_rows:
        return pipeline_phase_details(phase_rows, session)

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


def pipeline_phase_details(
    phase_rows: Sequence[Mapping[str, Any]],
    session: Mapping[str, Any],
) -> str:
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
                pipeline_expanded_phase(phase, session),
            )
        )
    return "".join(html_phases)


def pipeline_expanded_phase(
    phase: Mapping[str, Any],
    session: Mapping[str, Any],
) -> str:
    evidence = pipeline_phase_evidence_panel(phase)
    logs = pipeline_phase_log_panel(phase, session)
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


def pipeline_phase_log_panel(
    phase: Mapping[str, Any],
    session: Mapping[str, Any],
) -> str:
    artifacts = pipeline_phase_artifacts(phase)
    live_panel = pipeline_live_execute_log_panel(phase, session, artifacts)
    snippets = pipeline_collect_log_snippets(
        artifacts,
        source=str(phase.get("label") or phase.get("phase") or "phase"),
    )
    captured_panel = pipeline_log_snippets_html(snippets)
    if not live_panel and not captured_panel:
        return ""
    return "<h3>Logs</h3>{}{}".format(live_panel, captured_panel)


def pipeline_phase_artifacts(phase: Mapping[str, Any]) -> Mapping[str, Any]:
    return _mapping(phase.get("artifacts"))


def pipeline_session_has_live_execute_logs(session: Mapping[str, Any]) -> bool:
    for phase in pipeline_session_phase_rows(session):
        artifacts = pipeline_phase_artifacts(phase)
        if (
            pipeline_is_execute_phase(phase)
            and pipeline_runtime_log_streams(artifacts)
            and pipeline_execute_phase_running(phase, session)
        ):
            return True
    return False


def pipeline_live_execute_log_panel(
    phase: Mapping[str, Any],
    session: Mapping[str, Any],
    artifacts: Mapping[str, Any],
) -> str:
    if not pipeline_is_execute_phase(phase):
        return ""
    streams = pipeline_runtime_log_streams(artifacts)
    if not streams:
        return ""

    running = pipeline_execute_phase_running(phase, session)
    status_label = "Codex Execute running" if running else "Codex Execute log tail"
    state_label = "running" if running else "catching up"
    session_id = str(session.get("id") or "")
    phase_name = str(phase.get("phase") or "execute")
    fields = [
        ("Command", pipeline_execute_command_ref(artifacts)),
        ("Elapsed", pipeline_execute_elapsed_text(artifacts)),
        ("Timeout", pipeline_execute_timeout_text(artifacts, session)),
        ("Running", "yes" if running else "no"),
    ]
    stream_panels = [
        pipeline_live_log_stream_panel(
            session_id=session_id,
            phase=phase_name,
            stream=stream,
            metadata=metadata,
        )
        for stream, metadata in streams.items()
    ]
    return (
        '<section class="pipeline-live-log" data-live-log-panel '
        'data-session-id="{session_id}" data-phase="{phase}" data-poll-ms="1500" '
        'data-max-bytes="{max_bytes}">'
        '<div class="status-row">{badge}<strong>{status_label}</strong>'
        '<span>status: <strong data-live-log-state>{state_label}</strong></span></div>'
        '<div class="review-grid">{fields}</div>'
        '<div class="pipeline-live-log-streams">{streams}</div>'
        "{script}"
        "</section>"
    ).format(
        session_id=escape(session_id),
        phase=escape(phase_name),
        max_bytes=PIPELINE_LIVE_LOG_BROWSER_LIMIT,
        badge=status_badge("running" if running else str(phase.get("status") or "complete")),
        status_label=escape(status_label),
        state_label=escape(state_label),
        fields="".join(
            review_field(label, escape(value or "not recorded")) for label, value in fields
        ),
        streams="".join(stream_panels),
        script=pipeline_live_log_script(),
    )


def pipeline_live_log_stream_panel(
    *,
    session_id: str,
    phase: str,
    stream: str,
    metadata: Mapping[str, Any],
) -> str:
    start_offset = pipeline_log_offset(metadata.get("start_offset"))
    log_url = "/pipeline/sessions/{}/logs/{}/{}".format(
        quote(session_id, safe=""),
        quote(phase, safe=""),
        quote(stream, safe=""),
    )
    return (
        '<section class="pipeline-live-log-stream" data-live-log-stream="{stream}" '
        'data-log-url="{url}" data-offset="{offset}" data-received="0" '
        'data-max-bytes="{max_bytes}">'
        '<div class="status-row"><strong>{label}</strong>'
        '<span data-live-log-offset>{offset} bytes</span></div>'
        '<pre class="pipeline-live-log-output" data-live-log-output="{stream}"></pre>'
        "</section>"
    ).format(
        stream=escape(stream),
        url=escape(log_url),
        offset=escape(start_offset),
        max_bytes=PIPELINE_LIVE_LOG_BROWSER_LIMIT,
        label=escape(stream.upper()),
    )


def pipeline_live_log_script() -> str:
    return """
<script>
(function() {
  function startPipelineLiveLogs() {
    var panels = document.querySelectorAll("[data-live-log-panel]");
    panels.forEach(function(panel) {
      if (panel.dataset.liveLogStarted === "1") {
        return;
      }
      panel.dataset.liveLogStarted = "1";
      var pollMs = Number(panel.dataset.pollMs || "1500");
      var state = panel.querySelector("[data-live-log-state]");
      var streams = Array.prototype.slice.call(
        panel.querySelectorAll("[data-live-log-stream]")
      );
      function setState(value) {
        if (state) {
          state.textContent = value;
        }
      }
      function pollStream(streamEl) {
        var output = streamEl.querySelector("[data-live-log-output]");
        var offsetLabel = streamEl.querySelector("[data-live-log-offset]");
        var received = Number(streamEl.dataset.received || "0");
        var maxBytes = Number(streamEl.dataset.maxBytes || panel.dataset.maxBytes || "65536");
        if (received >= maxBytes) {
          return Promise.resolve({running: false, eof: true, limited: true});
        }
        var url = streamEl.dataset.logUrl + "?offset=" + encodeURIComponent(
          streamEl.dataset.offset || "0"
        );
        return fetch(url, {cache: "no-store"})
          .then(function(response) { return response.json(); })
          .then(function(payload) {
            if (!payload.ok) {
              throw new Error(
                payload.error && payload.error.message
                  ? payload.error.message
                  : "log tail failed"
              );
            }
            var chunk = payload.chunk || "";
            var remaining = Math.max(0, maxBytes - received);
            if (chunk && output && remaining > 0) {
              output.textContent += chunk.slice(0, remaining);
              received += chunk.slice(0, remaining).length;
              streamEl.dataset.received = String(received);
            }
            streamEl.dataset.offset = String(payload.next_offset);
            if (offsetLabel) {
              offsetLabel.textContent = String(payload.next_offset) + " bytes";
            }
            return {
              running: Boolean(payload.running),
              eof: Boolean(payload.eof) || received >= maxBytes,
              limited: received >= maxBytes
            };
          });
      }
      function tick() {
        Promise.all(streams.map(pollStream))
          .then(function(results) {
            var running = results.some(function(item) { return item.running; });
            var open = results.some(function(item) { return !item.eof; });
            var limited = results.some(function(item) { return item.limited; });
            if (running) {
              setState("running");
            } else if (open) {
              setState("catching up");
            } else if (limited) {
              setState("browser limit reached");
            } else {
              setState("complete");
            }
            if (running || open) {
              window.setTimeout(tick, pollMs);
            }
          })
          .catch(function(error) {
            setState("paused: " + error.message);
            window.setTimeout(tick, 5000);
          });
      }
      tick();
    });
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", startPipelineLiveLogs);
  } else {
    startPipelineLiveLogs();
  }
})();
</script>"""


def pipeline_is_execute_phase(phase: Mapping[str, Any]) -> bool:
    return str(phase.get("phase") or "").strip() == "execute"


def pipeline_runtime_log_streams(
    artifacts: Mapping[str, Any],
) -> dict[str, Mapping[str, Any]]:
    streams: dict[str, Mapping[str, Any]] = {}
    candidates = (
        artifacts.get("runtime_logs"),
        _mapping(artifacts.get("execute_evidence")).get("runtime_logs"),
        _mapping(artifacts.get("adapter")).get("runtime_logs"),
        _mapping(artifacts.get("adapter_summary")).get("runtime_logs"),
    )
    for candidate in candidates:
        logs = _mapping(candidate)
        for stream in ("stdout", "stderr"):
            metadata = _mapping(logs.get(stream))
            if metadata and stream not in streams:
                streams[stream] = metadata
    return streams


def pipeline_execute_command_ref(artifacts: Mapping[str, Any]) -> str:
    execute_evidence = _mapping(artifacts.get("execute_evidence"))
    adapter = _mapping(artifacts.get("adapter"))
    adapter_summary = _mapping(artifacts.get("adapter_summary"))
    return first_nonempty_text(
        artifacts.get("command_ref"),
        execute_evidence.get("command_ref"),
        adapter_summary.get("command_ref"),
        adapter.get("command_ref"),
    )


def pipeline_execute_timeout_text(
    artifacts: Mapping[str, Any],
    session: Mapping[str, Any],
) -> str:
    execute_evidence = _mapping(artifacts.get("execute_evidence"))
    adapter = _mapping(artifacts.get("adapter"))
    adapter_summary = _mapping(artifacts.get("adapter_summary"))
    policy_codex = _mapping(_mapping(session.get("policy_snapshot")).get("codex"))
    return first_nonempty_text(
        artifacts.get("timeout_sec"),
        execute_evidence.get("timeout_sec"),
        adapter_summary.get("timeout_sec"),
        adapter.get("timeout_sec"),
        policy_codex.get("timeout_sec"),
    )


def pipeline_execute_elapsed_text(artifacts: Mapping[str, Any]) -> str:
    execute_evidence = _mapping(artifacts.get("execute_evidence"))
    adapter = _mapping(artifacts.get("adapter"))
    adapter_summary = _mapping(artifacts.get("adapter_summary"))
    duration = first_nonempty_text(
        artifacts.get("duration_sec"),
        execute_evidence.get("duration_sec"),
        adapter_summary.get("duration_sec"),
        adapter.get("duration_sec"),
    )
    if duration:
        return "{}s".format(duration)
    started = first_nonempty_text(
        artifacts.get("execute_started_at"),
        execute_evidence.get("started_at"),
        adapter_summary.get("started_at"),
        adapter.get("started_at"),
    )
    finished = first_nonempty_text(
        artifacts.get("execute_finished_at"),
        execute_evidence.get("finished_at"),
        adapter_summary.get("finished_at"),
        adapter.get("finished_at"),
    )
    return pipeline_elapsed_between(started, finished)


def pipeline_execute_phase_running(
    phase: Mapping[str, Any],
    session: Mapping[str, Any],
) -> bool:
    if str(session.get("status") or "") != "running":
        return False
    current_phase = str(session.get("current_phase") or phase.get("phase") or "").strip()
    if current_phase != str(phase.get("phase") or "").strip():
        return False
    current_status = str(session.get("current_phase_status") or phase.get("status") or "").strip()
    return current_status in {"active", "in_progress", "running"}


def pipeline_elapsed_between(started: str, finished: str) -> str:
    start_dt = parse_timestamp(started)
    if not start_dt:
        return ""
    finish_dt = parse_timestamp(finished) or datetime.now(timezone.utc)
    seconds = max(0, int((finish_dt - start_dt).total_seconds()))
    return duration_seconds_label(seconds)


def duration_seconds_label(seconds: int) -> str:
    minutes, rem = divmod(max(0, int(seconds)), 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return "{}h {}m {}s".format(hours, minutes, rem)
    if minutes:
        return "{}m {}s".format(minutes, rem)
    return "{}s".format(rem)


def pipeline_log_offset(value: Any) -> int:
    if isinstance(value, int) and not isinstance(value, bool):
        return max(0, value)
    text = str(value or "").strip()
    return int(text) if text.isdigit() else 0


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


def pipeline_session_owner_next_action(session: Mapping[str, Any]) -> str:
    guidance = pipeline_session_action_guidance(session)
    if guidance:
        return '<div data-pipeline-owner-next-action>{}</div>'.format(guidance)
    return '<div data-pipeline-owner-next-action hidden></div>'


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
            text = str(
                value.get("{}_snippet".format(stream))
                or value.get("{}_summary".format(stream))
                or ""
            )
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


def pipeline_session_create_form(data: Mapping[str, Any], pipeline: Mapping[str, Any]) -> str:
    request = _mapping(pipeline.get("queue_request"))
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
    return action_form(
        "pipeline.session.create",
        create_fields,
        button_label="Create Session",
    )


def pipeline_action_controls(data: Mapping[str, Any], pipeline: Mapping[str, Any]) -> str:
    session = _mapping(pipeline.get("current_session"))
    session_id = str(session.get("id") or "")
    session_status = str(session.get("status") or "unknown")
    safe_forms = [action_form("pipeline.render", [], button_label="Refresh Session")]
    guidance = pipeline_session_action_guidance(session)
    if guidance:
        safe_forms.append(guidance)

    run_forms: list[str] = []
    if session_id:
        run_forms.extend(pipeline_session_run_action_forms(session_id, session_status))
    else:
        run_forms.append(
            '<p class="empty">Create a session from Queue Selector and Session Setup before running the queue.</p>'
        )

    restricted = [
        '<p class="muted">Restricted actions are separated and require confirmation. '
        "Push, merge, reset, restore, clean, rebase and discard actions are not exposed.</p>"
    ]
    if session_id:
        if session_status in PIPELINE_STOPPABLE_STATUSES:
            restricted.append(pipeline_session_stop_action_form(session_id))
        else:
            restricted.append(
                '<p class="empty">Stop Session is unavailable for status {}.</p>'.format(
                    escape(session_status)
                )
            )
    else:
        restricted.append('<p class="empty">Stop Session is unavailable until a session exists.</p>')

    return (
        '<div class="pipeline-action-groups pipeline-action-groups-safety">'
        '<div class="pipeline-action-group safe-actions"><h3>Refresh Status</h3>{}</div>'
        '<div class="pipeline-action-group progress-actions"><h3>Guarded Run / Resume</h3>{}</div>'
        '<div class="pipeline-action-group restricted-actions"><h3>Restricted Stop</h3>{}</div>'
        "</div>"
    ).format(
        "".join(safe_forms),
        "".join(run_forms),
        "".join(restricted),
    )


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


def dashboard_effective_policy_summary(data: Mapping[str, Any]) -> Mapping[str, Any]:
    ui_settings = _mapping(data.get("ui_settings"))
    policy_catalog = _mapping(ui_settings.get("policy_catalog"))
    return _mapping(policy_catalog.get("effective_policy"))


def policy_confirmation_summary(summary: Mapping[str, Any]) -> str:
    summary = _mapping(summary)
    if not summary:
        return ""
    return "; ".join(
        "{}: {}".format(label, value)
        for label, value in effective_policy_summary_rows(summary)
        if value
    )


def policy_requires_auto_close_note(summary: Mapping[str, Any]) -> bool:
    close = _mapping(_mapping(summary).get("close"))
    return bool(close.get("auto_close_task")) and not bool(
        close.get("owner_approval_note_present")
    )


def effective_policy_summary_panel(
    summary: Mapping[str, Any],
    *,
    title: str,
    compact: bool = False,
) -> str:
    summary = _mapping(summary)
    if not summary:
        return ""
    rows = effective_policy_summary_rows(summary)
    row_html = "".join(
        "<div><dt>{}</dt><dd>{}</dd></div>".format(
            escape(label),
            escape(value),
        )
        for label, value in rows
    )
    heading = "h4" if compact else "h2"
    classes = "effective-policy-summary"
    if compact:
        classes += " effective-policy-summary-compact"
    content = (
        '<div class="effective-policy-summary-header">'
        "<{heading}>{title}</{heading}>"
        '<span class="pill">read-only</span>'
        "</div>"
        '<dl class="effective-policy-summary-grid">{rows}</dl>'
    ).format(
        heading=heading,
        title=escape(title),
        rows=row_html,
    )
    if compact:
        return '<div class="{}" data-effective-policy-summary>{}</div>'.format(
            classes,
            content,
        )
    return '<section class="panel {}" data-effective-policy-summary>{}</section>'.format(
        classes,
        content,
    )


def incomplete_run_warning_panel(
    summary: Mapping[str, Any],
    *,
    compact: bool = False,
    include_confirmation: bool = False,
) -> str:
    warning = _mapping(_mapping(summary).get("incomplete_run_warning"))
    if not warning.get("enabled"):
        return ""

    classes = "incomplete-run-warning"
    if compact:
        classes += " incomplete-run-warning-compact"
    missing = ", ".join(str(label) for label in warning.get("missing_phase_labels") or [])
    missing_html = ""
    if missing:
        missing_html = '<p class="muted">Not reached in one batch: {}</p>'.format(
            escape(missing)
        )
    confirmation_html = ""
    if include_confirmation:
        confirmation_html = (
            '<label class="checkline incomplete-run-confirm">'
            '<input type="checkbox" name="{}" value="yes" required>'
            "Confirm this partial Web run"
            "</label>"
        ).format(escape(INCOMPLETE_RUN_CONFIRM_FIELD))
    return (
        '<div class="{}" role="alert" data-incomplete-run-warning>'
        "<strong>Incomplete Web Run</strong>"
        "<p>{}</p>"
        "{}{}"
        "</div>"
    ).format(
        classes,
        escape(str(warning.get("message") or "")),
        missing_html,
        confirmation_html,
    )


def effective_policy_summary_rows(summary: Mapping[str, Any]) -> list[tuple[str, str]]:
    batch = _mapping(summary.get("batch"))
    review = _mapping(summary.get("review"))
    close = _mapping(summary.get("close"))
    commit = _mapping(summary.get("commit"))
    verify = _mapping(summary.get("verify"))
    return [
        ("Policy", str(summary.get("name") or "unknown")),
        ("batch.max_steps", _policy_number(batch.get("max_steps"))),
        ("batch.max_failures", _policy_number(batch.get("max_failures"))),
        ("Machine Review", _policy_machine_review_label(review)),
        ("Codex Review", _policy_codex_review_label(review)),
        ("Auto-close", _policy_auto_close_label(close)),
        ("Local Commit", _policy_commit_label(commit)),
        ("Report Warnings", _policy_report_warning_label(verify)),
        ("Git Diff Gates", _policy_git_diff_label(verify)),
    ]


def _policy_number(value: Any) -> str:
    return "" if value is None else str(value)


def _policy_machine_review_label(review: Mapping[str, Any]) -> str:
    if review.get("machine_review_required"):
        return "required ({})".format(review.get("machine_review_outcome") or "pass")
    return "not required"


def _policy_codex_review_label(review: Mapping[str, Any]) -> str:
    if review.get("codex_review_required"):
        return "required ({})".format(review.get("codex_review_decision") or "approve")
    return "skipped"


def _policy_auto_close_label(close: Mapping[str, Any]) -> str:
    if not close.get("auto_close_task"):
        return "disabled"
    if close.get("owner_approval_note_present"):
        return "enabled (note present)"
    return "enabled (note required)"


def _policy_commit_label(commit: Mapping[str, Any]) -> str:
    if not commit.get("create_local_commit"):
        return "disabled"
    return "enabled ({})".format(commit.get("mode") or "local_only")


def _policy_report_warning_label(verify: Mapping[str, Any]) -> str:
    allow = bool(verify.get("allow_report_warnings"))
    block = bool(verify.get("block_report_warnings", True))
    if allow and not block:
        return "relaxed (allowed / advisory)"
    if allow:
        return "relaxed (allowed)"
    if not block:
        return "relaxed (advisory)"
    return "strict (blocking)"


def _policy_git_diff_label(verify: Mapping[str, Any]) -> str:
    if verify.get("run_git_diff_gates", True):
        return "strict (required)"
    return "relaxed (not run)"


def render_tasks(
    data: Mapping[str, Any],
    *,
    query: Mapping[str, Sequence[str]] | None = None,
) -> str:
    query = query or {}
    filters = task_filter_state(data, query)
    tasks = filter_tasks(data.get("tasks") or [], data, filters)
    selected_task = selected_task_for_drawer(data, tasks, query)
    view = str(filters.get("view") or "queue")
    if view == "inventory":
        task_sections = [
            '<section class="panel">',
            "<h2>Focus Tasks</h2>",
            task_table(
                focus_tasks(data, tasks),
                empty_text="No current, in-progress, or review tasks match the filters.",
                data=data,
                include_actions=True,
                filters=filters,
            ),
            "</section>",
            '<section class="panel">',
            "<h2>Full Inventory</h2>",
            task_grouped_table(tasks, data, filters, empty_text="No tasks match the filters."),
            "</section>",
        ]
    else:
        task_sections = [
            '<section class="panel task-action-queue-panel">',
            '<div class="owner-section-header">'
            "<div><h2>Action Queue</h2>"
            "<p>Compact owner-action view grouped by the next useful task state.</p></div>"
            '<a class="button-link secondary" href="{}">Open Full Inventory</a>'
            "</div>".format(escape(task_inventory_href(filters))),
            task_action_queue(tasks, data, filters),
            "</section>",
        ]
    body = [
        current_execution_bar(data, selected_task=selected_task),
        '<section class="summary-grid">',
        *task_summary_metrics(data, tasks, filters),
        "</section>",
        '<section class="panel">',
        "<h2>Task Filters</h2>",
        task_filter_form(data, filters),
        task_filter_summary(filters),
        "</section>",
        project_health_panel(data, selected_task=selected_task, compact=True),
        '<div class="task-page-layout">',
        '<div class="task-page-main">',
        *task_sections,
        "</div>",
        task_detail_drawer(selected_task, data, filters),
        "</div>",
    ]
    return render_page(
        "Tasks",
        "".join(body),
        active="/tasks",
        confirm_policy_summary=policy_confirmation_summary(
            dashboard_effective_policy_summary(data)
        ),
    )


def task_summary_metrics(
    data: Mapping[str, Any],
    tasks: Sequence[Mapping[str, Any]],
    filters: Mapping[str, Any],
) -> list[str]:
    if str(filters.get("view") or "queue") == "inventory":
        return task_inventory_summary_metrics(tasks)
    return task_action_summary_metrics(data, tasks)


def task_inventory_summary_metrics(tasks: Sequence[Mapping[str, Any]]) -> list[str]:
    counts: dict[str, int] = {}
    for task in tasks:
        status = str(task.get("status") or "unknown")
        counts[status] = counts.get(status, 0) + 1
    return [
        *[
            metric(str(status), str(count))
            for status, count in sorted(
                counts.items(),
                key=lambda item: status_sort_key(str(item[0])),
            )
        ],
        metric("Visible", str(len(tasks))),
    ]


def task_action_summary_metrics(
    data: Mapping[str, Any],
    tasks: Sequence[Mapping[str, Any]],
) -> list[str]:
    counts = task_action_metric_counts(tasks, data)
    return [
        *[
            metric(label, str(counts.get(key, 0)))
            for key, label in TASK_ACTION_METRIC_GROUPS
        ],
        metric("Health Issues", str(counts.get("health_issues", 0))),
    ]


def task_action_metric_counts(
    tasks: Sequence[Mapping[str, Any]],
    data: Mapping[str, Any],
) -> dict[str, int]:
    groups = task_action_queue_groups(tasks, data)
    counts = {
        key: len(groups.get(key, []))
        for key, _ in TASK_ACTION_METRIC_GROUPS
    }
    counts["health_issues"] = task_health_issue_count(data)
    return counts


def task_health_issue_count(data: Mapping[str, Any]) -> int:
    return sum(
        1
        for item in project_health_items(data)
        if health_summary_status(item.get("status")) != "PASS"
    )


def selected_task_for_drawer(
    data: Mapping[str, Any],
    visible_tasks: Sequence[Mapping[str, Any]],
    query: Mapping[str, Sequence[str]],
) -> Mapping[str, Any]:
    selected = _query_value(query, "task")
    if selected:
        for task in data.get("tasks") or []:
            if isinstance(task, Mapping) and task_ref_matches(task, selected):
                return task
    if len(visible_tasks) == 1:
        return visible_tasks[0]
    current = _mapping(data.get("current_task"))
    current_ref = str(current.get("ref") or current.get("id") or "")
    if current_ref:
        for task in visible_tasks:
            if task_ref_matches(task, current_ref):
                return task
    return {}


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
    groups = change_decision_groups(changes)
    visible_count = sum(len(items) for items in groups.values())
    body = [
        '<section class="summary-grid">',
        *[metric(str(status), str(count)) for status, count in sorted(counts.items(), key=lambda item: status_sort_key(str(item[0])))],
        metric("Visible", str(visible_count)),
        metric("Needs Approval", str(len(groups.get("needs_approval", [])))),
        metric("Approved", str(len(groups.get("approved", [])))),
        metric("In Review", str(len(groups.get("in_review", [])))),
        "</section>",
        '<section class="panel">',
        "<h2>Evolution Filters</h2>",
        change_filter_form(data, filters),
        change_filter_summary(filters),
        "</section>",
        change_decision_queue(groups, data),
        create_change_for_task_panel(
            task_options,
            default_task,
            compact=visible_count > 0,
        ),
    ]
    return render_page("Evolution", "".join(body), active="/evolution")


def inspection_intro(title: str, purpose: str, detail: str = "") -> str:
    detail_html = (
        '<p class="muted inspection-intro-detail">{}</p>'.format(escape(detail))
        if detail
        else ""
    )
    return (
        '<section class="panel inspection-intro">'
        '<div class="owner-section-header"><div><h2>{}</h2><p>{}</p></div></div>'
        "{}"
        "</section>"
    ).format(
        escape(title),
        escape(purpose),
        detail_html,
    )


def inspection_panel(
    title: str,
    content: str,
    *,
    description: str = "",
    class_name: str = "",
) -> str:
    classes = "panel inspection-panel"
    if class_name:
        classes = "{} {}".format(classes, class_name)
    description_html = (
        "<p>{}</p>".format(escape(description))
        if description
        else ""
    )
    return (
        '<section class="{}">'
        '<div class="owner-section-header"><div><h2>{}</h2>{}</div></div>'
        "{}"
        "</section>"
    ).format(
        classes,
        escape(title),
        description_html,
        content,
    )


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
        inspection_intro(
            "Epics",
            "Delivery planning containers with completion, linked-change, and action diagnostics.",
        ),
        inspection_panel(
            "Epic Diagnostics",
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
        ),
    ]
    return render_page("Epics", "".join(body), active="/epics")


def render_reviews(
    data: Mapping[str, Any],
    *,
    query: Mapping[str, Sequence[str]] | None = None,
) -> str:
    review_commands = data.get("review_commands") or []
    selected_task = _query_value(query or {}, "task")
    review_groups = task_review_candidate_groups(data, selected_task)
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
        "<h2>Review Decision Queue</h2>",
        review_task_selector(data, selected_task),
        task_review_queue(review_groups, data, selected_task=selected_task),
        "</section>",
        '<details class="panel diagnostics-panel">',
        "<summary><strong>Review Command Diagnostics</strong><span>{} commands</span></summary>".format(
            escape(len(command_rows))
        ),
        table(("Command", "Availability", "Description"), command_rows, "No review commands registered."),
        "</details>",
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
        inspection_intro(
            "Commit Readiness",
            "Local-only commit diagnostics for changed files, validation gates, and suggested message text.",
            "This page does not expose push, merge, reset, restore, checkout, or remote operations.",
        ),
        '<section class="summary-grid">',
        metric("Readiness", str(data.get("status") or "UNKNOWN")),
        metric("Changed Files", str(len(changed_files))),
        metric("Validation", str(doctor.get("overall_status") or "UNKNOWN")),
        metric("Git", str(git.get("status") or "unknown")),
        "</section>",
        inspection_panel(
            "Readiness Status",
            (
                '<div class="status-row">'
                "{}<span>{}</span>{}"
                '<a class="button-link" href="/commit?refresh=1">Refresh readiness checks</a>'
                "</div>"
            ).format(
                status_badge(str(data.get("status") or "UNKNOWN")),
                escape(data.get("message") or ""),
                doctor_cache_detail(doctor),
            ),
        ),
        inspection_panel(
            "Changed Files",
            "{}{}".format(
                commit_changed_files_table(git),
                '<p class="muted">Read command: <code>{}</code></p>'.format(
                    escape(git.get("command") or "git status --short --untracked-files=all")
                ),
            ),
        ),
        inspection_panel(
            "Readiness Checks",
            commit_validation_table(_mapping(data.get("validation"))),
        ),
        inspection_panel(
            "Completed Tasks",
            commit_task_table(data.get("completed_tasks")),
        ),
        inspection_panel(
            "Accepted Changes",
            commit_change_table(data.get("accepted_changes")),
        ),
        inspection_panel(
            "Suggested Commit Message (not executed)",
            (
                '<textarea readonly rows="2">{}</textarea>'
                '<p class="muted">Suggestion only. This view does not run git commit, git push, staging, reset, restore, or checkout commands.</p>'
            ).format(escape(data.get("suggested_commit_message") or "")),
        ),
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
    sections = [
        inspection_intro(
            "Events",
            "Recent audit lines grouped by project-control domain for low-level troubleshooting.",
        )
    ]
    for audit in data.get("events") or []:
        lines = audit.get("lines") or []
        if lines:
            content = "".join("<li>{}</li>".format(escape(line)) for line in lines)
        else:
            content = "<li>{}</li>".format(escape(audit.get("error") or "No recent events."))
        sections.append(
            inspection_panel(
                str(audit.get("domain", "audit").title()),
                '<ul class="event-list">{}</ul>'.format(content),
            )
        )
    if len(sections) == 1:
        sections.append(
            inspection_panel(
                "Audit Events",
                '<p class="empty">No audit domains loaded.</p>',
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
        inspection_intro(
            "Generated Views",
            "Read-only inventory of derived Markdown outputs and their current freshness signals.",
        ),
        project_health_panel(data),
        inspection_panel(
            "Generated View Inventory",
            table(("File", "Source", "Exists", "Updated", "First Line"), rows, "No generated views."),
        ),
    ]
    return render_page("Generated", "".join(body), active="/generated")


def render_settings(model: ReadOnlyProjectModel) -> str:
    read_model = model.ui_settings()
    settings = _mapping(read_model.get("settings"))
    policy_catalog = _mapping(read_model.get("policy_catalog"))
    effective_policy = _mapping(policy_catalog.get("effective_policy"))
    policy_context = "".join(
        item
        for item in [
            effective_policy_summary_panel(
                effective_policy,
                title="Effective Policy Summary",
                compact=True,
            ),
            incomplete_run_warning_panel(effective_policy, compact=True),
        ]
        if item
    )
    source = str(read_model.get("source") or "")
    path = str(read_model.get("path") or "")
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
        '<div class="settings-card-grid">',
        settings_group(
            "Pipeline",
            [
                settings_text_row(
                    "command_line",
                    "Command Line",
                    settings,
                    helper="Shell-style local Codex command used by UI runs.",
                ),
                settings_policy_select_row(
                    "default_policy",
                    "Default Policy",
                    settings,
                    policy_catalog,
                    helper="Pipeline policy preset used when the UI starts a run.",
                    context=policy_context,
                ),
                settings_text_row(
                    BATCH_MAX_STEPS_SETTING,
                    "Max Steps Override",
                    settings,
                    helper=(
                        "Optional Web-run override for policy batch.max_steps. "
                        "Allowed {}-{}; leave blank to use the selected policy."
                    ).format(BATCH_MAX_STEPS_MIN, BATCH_MAX_STEPS_MAX),
                    input_type="number",
                ),
                settings_text_row(
                    BATCH_MAX_FAILURES_SETTING,
                    "Max Failures Override",
                    settings,
                    helper=(
                        "Optional Web-run override for policy batch.max_failures. "
                        "Allowed {}-{}; leave blank to use the selected policy."
                    ).format(BATCH_MAX_FAILURES_MIN, BATCH_MAX_FAILURES_MAX),
                    input_type="number",
                ),
            ],
            description="Run command, default policy, and Batch Run overrides used by Web runs.",
            badge="policy",
            primary=True,
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
            description="Required review behavior before task close.",
            badge="gates",
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
            description="Local execution and readiness-check limits.",
            badge="limits",
        ),
        settings_group(
            "Advanced Controls",
            [
                settings_checkbox_row(
                    ALLOW_RELAXED_GIT_DIFF_VERIFICATION_SETTING,
                    "Allow relaxed git diff verification for UI runs",
                    settings,
                    helper=(
                        "UI runs only. Strict git diff verification remains the "
                        "default and is available by turning this off."
                    ),
                ),
                settings_checkbox_row(
                    ALLOW_REPORT_WARNINGS_SETTING,
                    "Allow report-warning pass behavior for UI runs",
                    settings,
                    helper=(
                        "UI runs only. Report warnings may pass verification; "
                        "report errors and other gates still block."
                    ),
                ),
                settings_checkbox_row(
                    ALLOW_RELAXED_REPORT_WARNINGS_SETTING,
                    "Allow relaxed report warnings for fast UI runs",
                    settings,
                    helper=(
                        "Fast UI runs only. Report warnings become advisory; "
                        "report errors and other gates still block."
                    ),
                ),
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
            description="Guarded controls for exceptional UI verification and internal project-control flows.",
            badge="guarded",
            guarded=True,
        ),
        "</div>",
        '<footer class="settings-footer">',
        '<a class="button-link secondary" href="/settings">Reset</a>',
        '<span class="muted settings-reset-note">Discard unsaved changes.</span>',
        '<label class="checkline"><input type="checkbox" name="confirm" value="yes" required>Confirm</label>',
        '<button type="submit">Apply Settings</button>',
        "</footer>",
        "</form>",
        "</section>",
    ]
    return render_page("Settings", "".join(body), active="/settings")


def render_doctor(data: Mapping[str, Any]) -> str:
    doctor = _mapping(data.get("doctor"))
    findings = doctor_findings(doctor)
    counts = doctor_summary_counts(doctor, findings)
    body = [
        '<section class="panel doctor-health-center">',
        '<div class="health-summary-header doctor-summary-header">',
        "<h2>Project Doctor</h2>",
        health_summary_counts_line(counts),
        "</div>",
        '<div class="doctor-status-strip">',
        '<div class="doctor-overall-status"><span>Overall</span>{}</div>'.format(
            status_badge(str(doctor.get("overall_status") or "UNKNOWN"))
        ),
        '<p class="doctor-summary-note">{}</p>'.format(
            escape(doctor_summary_message(counts))
        ),
        doctor_cache_detail(doctor),
        '<div class="doctor-action-strip">',
        '<a class="button-link" href="/doctor?refresh=1">Refresh Doctor</a>',
        action_form("project.doctor", [], button_label="Run Doctor"),
        "</div>",
        "</div>",
        "</section>",
        doctor_findings_panel(data, findings, counts),
        project_health_panel(data, compact=True, details_open=True),
    ]
    return render_page("Doctor", "".join(body), active="/doctor")


def doctor_findings(doctor: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    return [
        finding
        for finding in doctor.get("findings") or []
        if isinstance(finding, Mapping)
    ]


def doctor_summary_counts(
    doctor: Mapping[str, Any],
    findings: Sequence[Mapping[str, Any]],
) -> dict[str, int]:
    counts = {status: 0 for status in ("PASS", "WARN", "FAIL", "UNKNOWN")}
    for finding in findings:
        counts[doctor_finding_status(finding)] += 1

    summary = _mapping(doctor.get("summary"))
    for status in ("PASS", "WARN", "FAIL", "UNKNOWN"):
        if status in summary:
            counts[status] = doctor_count_value(summary.get(status), counts[status])
    return counts


def doctor_count_value(value: Any, default: int = 0) -> int:
    if isinstance(value, int):
        return max(0, value)
    text = str(value or "").strip()
    if text.isdigit():
        return int(text)
    return default


def doctor_finding_status(finding: Mapping[str, Any]) -> str:
    status = str(finding.get("status") or "").strip().upper()
    if status in {"PASS", "WARN", "FAIL"}:
        return status
    return "UNKNOWN"


def doctor_summary_message(counts: Mapping[str, int]) -> str:
    issue_count = counts.get("FAIL", 0) + counts.get("WARN", 0)
    unknown_count = counts.get("UNKNOWN", 0)
    if issue_count or unknown_count:
        return "{} FAIL, {} WARN, {} UNKNOWN need attention before PASS findings.".format(
            counts.get("FAIL", 0),
            counts.get("WARN", 0),
            unknown_count,
        )
    return "No failing, warning, or unknown findings reported."


def doctor_findings_panel(
    data: Mapping[str, Any],
    findings: Sequence[Mapping[str, Any]],
    counts: Mapping[str, int],
) -> str:
    if not findings:
        return (
            '<section class="panel doctor-findings">'
            "<h2>Doctor Findings</h2>"
            '<p class="empty">No doctor findings.</p>'
            "</section>"
        )

    by_status = {status: [] for status in ("FAIL", "WARN", "UNKNOWN", "PASS")}
    for finding in findings:
        by_status[doctor_finding_status(finding)].append(finding)

    has_attention_items = any(counts.get(status, 0) for status in ("FAIL", "WARN", "UNKNOWN"))
    groups = []
    for status in ("FAIL", "WARN", "UNKNOWN", "PASS"):
        status_findings = by_status[status]
        if not status_findings:
            continue
        open_by_default = status != "PASS" or not has_attention_items
        groups.append(
            doctor_finding_group(
                data,
                status,
                status_findings,
                open_by_default=open_by_default,
            )
        )

    return (
        '<section class="panel doctor-findings">'
        '<div class="doctor-section-header">'
        "<h2>Doctor Findings</h2>"
        '<span class="pill">{} total</span>'
        "</div>"
        "{}"
        "</section>"
    ).format(len(findings), "".join(groups))


def doctor_finding_group(
    data: Mapping[str, Any],
    status: str,
    findings: Sequence[Mapping[str, Any]],
    *,
    open_by_default: bool,
) -> str:
    open_attr = " open" if open_by_default else ""
    cards = "".join(doctor_finding_card(data, finding) for finding in findings)
    return (
        '<details class="doctor-finding-group doctor-group-{}"{}>'
        '<summary><span>{}</span><span class="pill">{} finding{}</span></summary>'
        '<div class="doctor-finding-list">{}</div>'
        "</details>"
    ).format(
        escape(status.lower()),
        open_attr,
        status_badge(status),
        len(findings),
        "" if len(findings) == 1 else "s",
        cards,
    )


def doctor_finding_card(data: Mapping[str, Any], finding: Mapping[str, Any]) -> str:
    status = doctor_finding_status(finding)
    command = str(finding.get("command") or "")
    command_html = (
        '<code>{}</code>'.format(escape(command))
        if command
        else '<p class="empty">No command reported.</p>'
    )
    return (
        '<article class="doctor-finding-card doctor-card-{}">'
        '<div class="doctor-finding-head">'
        "<h3>{}</h3>"
        "{}"
        "</div>"
        '<p class="doctor-finding-message">{}</p>'
        '<div class="doctor-finding-body">'
        '<div class="doctor-finding-command"><strong>Command</strong>{}</div>'
        '<div class="doctor-finding-actions"><strong>Repair / Check</strong>{}</div>'
        "</div>"
        "{}"
        "</article>"
    ).format(
        escape(status.lower()),
        escape(finding.get("check") or "check"),
        status_badge(status),
        escape(finding.get("message") or ""),
        command_html,
        doctor_finding_action_control(data, finding),
        doctor_finding_details(finding),
    )


def doctor_finding_details(finding: Mapping[str, Any]) -> str:
    details = finding.get("details")
    if not isinstance(details, Mapping) or not details:
        return ""
    return (
        '<details class="doctor-finding-details">'
        "<summary>Details</summary>"
        "<pre>{}</pre>"
        "</details>"
    ).format(escape(json.dumps(details, indent=2, sort_keys=True, default=str)))


def doctor_finding_action_control(
    data: Mapping[str, Any],
    finding: Mapping[str, Any],
) -> str:
    action = doctor_finding_action(str(finding.get("check") or ""))
    if action is None:
        return '<p class="empty">Use command above.</p>'

    action_id, button_label = action
    fields: list[str] = []
    if action_id in {
        "task.refresh_execution_context",
        "codex.prompt.build",
    }:
        task_ref = doctor_current_task_ref(data)
        if not task_ref:
            return '<p class="empty">Needs current task.</p>'
        fields.append(hidden_field("task", task_ref))
        if action_id == "codex.prompt.build":
            fields.append(hidden_field("with_context", "yes"))
    return action_form(action_id, fields, button_label=button_label)


def doctor_finding_action(check: str) -> tuple[str, str] | None:
    normalized = check.strip().lower()
    actions = {
        "task generated output": ("project.render", "Render Project Views"),
        "docs validation": ("docs.render", "Render Docs"),
        "docs generated output": ("docs.render", "Render Docs"),
        "evolution validation": ("project.render", "Render Project Views"),
        "evolution generated output": ("project.render", "Render Project Views"),
        "context validation": (
            "task.refresh_execution_context",
            "Refresh Context/Codex",
        ),
        "context generated output": (
            "task.refresh_execution_context",
            "Refresh Context/Codex",
        ),
        "protected project files": (
            "project.protected_check",
            "Check Protected Files",
        ),
        "codex prompt/status": ("codex.prompt.build", "Refresh Codex Prompt"),
        "context pack status": (
            "task.refresh_execution_context",
            "Refresh Context/Codex",
        ),
    }
    return actions.get(normalized)


def doctor_current_task_ref(data: Mapping[str, Any]) -> str:
    current = _mapping(data.get("current_task"))
    return str(current.get("ref") or current.get("id") or "").strip()


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
        inspection_intro(
            "Commands",
            "Registered CLI command metadata for checking ownership, availability, and read/write effects.",
        ),
        inspection_panel(
            "Command Registry",
            table(("Command", "Domain", "Kind", "Availability", "Read/Write"), rows, "No commands registered."),
        ),
    ]
    return render_page("Commands", "".join(body), active="/commands")


def render_actions(data: Mapping[str, Any]) -> str:
    current = data.get("current_task") or {}
    default_task = current.get("ref") or current.get("id") or ""
    run_policy_summary = dashboard_effective_policy_summary(data)
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
        inspection_intro(
            "Actions",
            "Confirmed write forms for controlled project operations routed through POST /actions.",
            "Use this page for low-level execution and repair forms; server-side workflow gates still apply.",
        ),
        inspection_panel(
            "Write Actions",
            table(("Action", "Registered Command", "Effect"), action_rows, "No write actions."),
            class_name="action-panel",
        ),
        inspection_panel(
            "Create Task",
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
            class_name="action-panel",
        ),
        inspection_panel(
            "Bulk Task Import",
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
            class_name="action-panel",
        ),
        inspection_panel(
            "Health & Repair",
            "".join(
                [
                    action_form("project.doctor", [], button_label="Run Doctor"),
                    action_form("project.protected_check", [], button_label="Check Protected Files"),
                    action_form("docs.render", [], button_label="Render Docs"),
                    action_form("project.render", [], button_label="Render Project Views"),
                ]
            ),
            class_name="action-panel",
        ),
        inspection_panel(
            "Task Workflows",
            "".join(
                [
                    table(("Workflow", "Command", "Step Preview"), workflow_rows, "No workflows."),
                    action_form(
                        "ui.run_selected_task",
                        [
                            input_field("task", "Task", default_task),
                            textarea_field(
                                "auto_close_note",
                                "Auto-close Owner Note",
                                rows=2,
                                placeholder="Required only when the selected policy auto-closes tasks.",
                            ),
                        ],
                        button_label="Run Selected Task",
                        confirm_required_note_fields=(
                            ("auto_close_note",)
                            if policy_requires_auto_close_note(run_policy_summary)
                            else ()
                        ),
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
                ]
            ),
            class_name="action-panel",
        ),
        inspection_panel(
            "Task Transition",
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
            class_name="action-panel",
        ),
        inspection_panel(
            "Current Task",
            "".join(
                [
                    action_form("current.set", [input_field("task", "Task", default_task)]),
                    action_form("current.clear", []),
                ]
            ),
            class_name="action-panel",
        ),
        inspection_panel(
            "Generated Output",
            "".join(
                [
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
                ]
            ),
            class_name="action-panel",
        ),
    ]
    return render_page(
        "Actions",
        "".join(body),
        active="/actions",
        confirm_policy_summary=policy_confirmation_summary(run_policy_summary),
    )


def render_error(error: CommandError) -> str:
    body = (
        '<section class="panel"><h2>Read Error</h2>'
        "<p>{}</p><pre>{}</pre></section>"
    ).format(
        escape(error.message),
        escape(json.dumps(error.details, indent=2, sort_keys=True)),
    )
    return render_page("Read Error", body, active="")


def _json_response(
    status: HTTPStatus,
    payload: Mapping[str, Any],
) -> tuple[HTTPStatus, str, str]:
    return (
        status,
        "application/json; charset=utf-8",
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
    )


def _json_error_response(error: CommandError) -> tuple[HTTPStatus, str, str]:
    if error.code in {
        "WEB_PIPELINE_RUNTIME_LOG_MISSING",
        "WEB_PIPELINE_SESSION_NOT_FOUND",
    }:
        status = HTTPStatus.NOT_FOUND
    elif error.code == "WEB_PIPELINE_RUNTIME_LOG_PATH_REJECTED":
        status = HTTPStatus.FORBIDDEN
    elif error.code in {
        "WEB_INVALID_PIPELINE_SESSION_ID",
        "WEB_INVALID_PIPELINE_LOG_STREAM",
        "WEB_INVALID_PIPELINE_LOG_OFFSET",
    }:
        status = HTTPStatus.BAD_REQUEST
    else:
        status = HTTPStatus.INTERNAL_SERVER_ERROR
    payload = {
        "ok": False,
        "error": {
            "code": error.code,
            "message": error.message,
            "details": error.details,
        },
    }
    if error.path:
        payload["error"]["path"] = error.path
    return _json_response(status, payload)


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
    return [
        task
        for task in tasks
        if task_review_queue_category(task, data)
    ]


def task_review_candidate_groups(
    data: Mapping[str, Any],
    selected_task: str = "",
) -> dict[str, list[Mapping[str, Any]]]:
    groups: dict[str, list[Mapping[str, Any]]] = {
        key: []
        for key, _, _ in REVIEW_QUEUE_GROUPS
    }
    for task in task_review_candidates(data, selected_task):
        category = task_review_queue_category(task, data)
        if not category and selected_task:
            category = "history"
        if category in groups:
            groups[category].append(task)
    return groups


def task_review_queue_category(
    task: Mapping[str, Any],
    data: Mapping[str, Any],
) -> str:
    status = str(task.get("status") or "unknown")
    if status == "in_review":
        return "awaiting_owner_review"
    if status == "changes_requested":
        return "changes_requested"
    if task_is_current(task, data) or status == "in_progress":
        return "current"
    if status in REVIEW_QUEUE_HISTORY_STATUSES or _mapping(task.get("latest_report")):
        return "history"
    return ""


def review_task_selector(data: Mapping[str, Any], selected_task: str) -> str:
    options = [("", "All review candidates"), *task_select_options(data)]
    return (
        '<form class="task-controls" method="get" action="/reviews">'
        "{}"
        '<button type="submit">Open</button>'
        '<a class="button-link secondary" href="/reviews">Reset</a>'
        "</form>"
    ).format(
        filter_select("task", "Task", options, selected_task),
    )


def task_review_queue(
    groups: Mapping[str, Sequence[Mapping[str, Any]]],
    data: Mapping[str, Any],
    *,
    selected_task: str = "",
) -> str:
    total = sum(len(tasks) for tasks in groups.values())
    if not total:
        if selected_task:
            return '<p class="empty">No task matches {}.</p>'.format(
                escape(selected_task)
            )
        return '<p class="empty">No review candidates.</p>'

    sections = []
    for key, title, description in REVIEW_QUEUE_GROUPS:
        tasks = list(groups.get(key) or [])
        selected_inside = bool(
            selected_task and any(task_ref_matches(task, selected_task) for task in tasks)
        )
        open_attr = " open" if selected_inside or key != "history" else ""
        sections.append(
            '<details class="review-queue-group review-queue-group-{}"{}>'
            "<summary><strong>{}</strong><span>{} task{}</span></summary>"
            '<p class="muted">{}</p>'
            "{}"
            "</details>".format(
                escape(css_token(key)),
                open_attr,
                escape(title),
                escape(len(tasks)),
                "" if len(tasks) == 1 else "s",
                escape(description),
                task_review_queue_table(
                    tasks,
                    data,
                    selected_task=selected_task,
                    empty_text="No {} tasks.".format(title.lower().replace(" ", "-")),
                ),
            )
        )
    return "".join(sections)


def task_review_queue_table(
    tasks: Sequence[Mapping[str, Any]],
    data: Mapping[str, Any],
    *,
    selected_task: str = "",
    empty_text: str,
) -> str:
    rows = []
    for task in tasks:
        cells = [
            task_review_ref_cell(task),
            status_badge(str(task.get("status") or "unknown")),
            escape(task.get("title") or ""),
            task_review_signal(task, data),
            task_review_primary_action(task, data, selected_task=selected_task),
        ]
        rows.append(
            "<tr>{}</tr>".format(
                "".join("<td>{}</td>".format(cell) for cell in cells)
            )
        )
    return table(("Task", "Status", "Title", "Review Signal", "Primary Action"), rows, empty_text)


def task_review_ref_cell(task: Mapping[str, Any]) -> str:
    task_ref = str(task.get("ref") or task.get("id") or "")
    legacy = str(task.get("legacy_id") or task.get("id") or "")
    if legacy and legacy != task_ref:
        return '<strong>{}</strong><div class="muted"><code>{}</code></div>'.format(
            escape(task_ref or "Task"),
            escape(legacy),
        )
    return '<strong>{}</strong>'.format(escape(task_ref or legacy or "Task"))


def task_review_signal(task: Mapping[str, Any], data: Mapping[str, Any]) -> str:
    status = str(task.get("status") or "unknown")
    parts = []
    if status == "in_review":
        parts.append("Owner decision required")
    elif status == "changes_requested":
        parts.append("Rework requested")
    elif task_is_current(task, data) or status == "in_progress":
        parts.append("Current execution work")
    elif status in REVIEW_QUEUE_HISTORY_STATUSES:
        parts.append("Decision history")
    else:
        parts.append("Review package")

    report = _mapping(task.get("latest_report"))
    report_signal = task_review_report_signal(report)
    if report_signal:
        parts.append(report_signal)

    hints = _mapping(task.get("pipeline_hints"))
    context = _mapping(hints.get("context"))
    context_reason = str(context.get("reason") or "")
    if context_reason:
        parts.append("context: {}".format(context_reason))

    return '<span class="review-signal">{}</span>'.format(
        escape(" · ".join(parts))
    )


def task_review_report_signal(report: Mapping[str, Any]) -> str:
    if not report:
        return ""
    bits = []
    report_id = str(report.get("id") or "")
    if report_id:
        bits.append("report {}".format(report_id))
    blockers = len(_string_items(report.get("blockers")))
    warnings = len(_string_items(report.get("warnings")))
    checks = [
        check
        for check in report.get("checks") or []
        if isinstance(check, Mapping)
    ]
    failed_checks = [
        check
        for check in checks
        if str(check.get("result") or "").lower() not in {"pass", "passed", "ok", "success"}
    ]
    if blockers:
        bits.append("{} blocker{}".format(blockers, "" if blockers == 1 else "s"))
    elif failed_checks:
        bits.append(
            "{} check issue{}".format(
                len(failed_checks),
                "" if len(failed_checks) == 1 else "s",
            )
        )
    elif warnings:
        bits.append("{} warning{}".format(warnings, "" if warnings == 1 else "s"))
    elif checks:
        bits.append("{} checks reported".format(len(checks)))
    if report.get("owner_decision_required"):
        bits.append("owner decision flag")
    return ", ".join(bits)


def task_review_primary_action(
    task: Mapping[str, Any],
    data: Mapping[str, Any],
    *,
    selected_task: str = "",
) -> str:
    status = str(task.get("status") or "")
    selected = bool(selected_task and task_ref_matches(task, selected_task))
    if status != "in_review" and not selected:
        task_ref = str(task.get("ref") or task.get("id") or "")
        if not task_ref:
            return '<span class="pill">Inspect Package</span>'
        href = "/reviews?task={}".format(quote(task_ref, safe=""))
        return '<a class="button-link secondary" href="{}">Inspect Package</a>'.format(
            escape(href)
        )
    label = "Decide Review" if status == "in_review" else "Inspect Package"
    open_attr = " open" if selected else ""
    return (
        '<details class="review-row-details"{}>'
        '<summary>{}</summary>'
        '<div class="review-row-package" aria-label="Task Review Packages">{}</div>'
        "</details>"
    ).format(
        open_attr,
        escape(label),
        task_review_package(task, data),
    )


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


def settings_group(
    title: str,
    rows: Sequence[str],
    *,
    description: str = "",
    badge: str = "",
    primary: bool = False,
    guarded: bool = False,
) -> str:
    classes = ["settings-card", "card"]
    if primary:
        classes.append("settings-card-primary")
    if guarded:
        classes.append("settings-card-guarded")
    description_html = (
        '<p class="muted">{}</p>'.format(escape(description)) if description else ""
    )
    badge_html = '<span class="pill">{}</span>'.format(escape(badge)) if badge else ""
    return (
        '<section class="{}">'
        '<div class="settings-card-header">'
        "<div><h3>{}</h3>{}</div>{}"
        "</div>"
        '<div class="settings-rows">{}</div>'
        "</section>"
    ).format(
        " ".join(classes),
        escape(title),
        description_html,
        badge_html,
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


def settings_policy_select_row(
    key: str,
    label: str,
    settings: Mapping[str, Any],
    policy_catalog: Mapping[str, Any],
    *,
    helper: str,
    context: str = "",
) -> str:
    selected_value = settings_form_value(settings.get(key))
    options = []
    for raw_policy in policy_catalog.get("policies") or []:
        policy = _mapping(raw_policy)
        name = str(policy.get("name") or "")
        if not name:
            continue
        behavior = str(policy.get("behavior_label") or "")
        option_label = name if not behavior else "{} - {}".format(name, behavior)
        selected = bool(policy.get("selected")) or name == selected_value
        options.append(
            '<option value="{}"{}>{}</option>'.format(
                escape(name),
                " selected" if selected else "",
                escape(option_label),
            )
        )
    if not options:
        fallback_label = selected_value or "No policy presets available"
        options.append(
            '<option value="{}" selected>{}</option>'.format(
                escape(selected_value),
                escape(fallback_label),
            )
        )
    context_html = (
        '<div class="settings-policy-context">{}</div>'.format(context)
        if context
        else ""
    )
    return (
        '<label class="setting-row setting-row-select">'
        "{}"
        '<span class="setting-control"><select name="{}">{}</select>{}</span>'
        "</label>"
    ).format(
        settings_row_copy(label, key, helper),
        escape(key),
        "".join(options),
        context_html,
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
        '<input type="checkbox" checked disabled>Locked ON<span class="pill">locked</span>'
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


def render_page(
    title: str,
    body: str,
    *,
    active: str,
    confirm_policy_summary: str = "",
) -> str:
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
    .app-shell {{
      min-height: 100vh;
      display: grid;
      grid-template-columns: 264px minmax(0, 1fr);
    }}
    .sidebar {{
      position: sticky;
      top: 0;
      height: 100vh;
      overflow-y: auto;
      background: #17212f;
      color: #f8fbff;
      border-right: 1px solid #111827;
      padding: 18px 14px;
    }}
    .sidebar-header {{
      display: grid;
      gap: 4px;
      padding: 0 8px 18px;
      border-bottom: 1px solid rgba(255,255,255,.14);
      margin-bottom: 18px;
    }}
    .brand {{
      color: #f8fbff;
      text-decoration: none;
      font-size: 18px;
      font-weight: 800;
      line-height: 1.2;
    }}
    .brand-kicker {{
      color: #a9b8c9;
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: .08em;
    }}
    .page-shell {{
      min-width: 0;
      display: grid;
      grid-template-rows: auto 1fr;
    }}
    .top-area {{
      background: var(--panel);
      border-bottom: 1px solid var(--line);
      padding: 22px 28px 20px;
    }}
    .eyebrow {{
      margin: 0 0 4px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: .08em;
    }}
    h1 {{
      margin: 0;
      font-size: 24px;
      font-weight: 700;
      letter-spacing: 0;
    }}
    .sidebar nav {{
      display: grid;
      gap: 20px;
    }}
    .nav-group {{
      display: grid;
      gap: 8px;
    }}
    .nav-group-title {{
      margin: 0;
      padding: 0 8px;
      color: #a9b8c9;
      font-size: 11px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: .08em;
    }}
    .nav-group-links {{
      display: grid;
      gap: 4px;
    }}
    .sidebar nav a {{
      display: flex;
      align-items: center;
      min-height: 34px;
      color: #dce8f6;
      text-decoration: none;
      border: 1px solid transparent;
      border-radius: 6px;
      padding: 7px 9px;
    }}
    .sidebar nav a:hover {{
      background: rgba(255,255,255,.07);
      border-color: rgba(255,255,255,.14);
    }}
    .sidebar nav a.active {{
      background: #f8fbff;
      color: #17212f;
      border-color: #f8fbff;
    }}
    .main-content {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 20px 28px 32px;
      width: 100%;
    }}
    .summary-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
      margin-bottom: 16px;
    }}
    .metric, .panel, .card, .queue-card, .drawer, .modal {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
    }}
    .card, .queue-card, .drawer, .modal {{
      min-width: 0;
      padding: 16px;
    }}
    .card-grid, .queue-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 14px;
    }}
    .queue-layout {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(260px, 360px);
      gap: 16px;
      align-items: start;
    }}
    .task-page-layout {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(300px, 400px);
      gap: 16px;
      align-items: start;
    }}
    .task-page-main {{
      min-width: 0;
      display: grid;
      gap: 16px;
    }}
    .queue-list {{
      display: grid;
      gap: 10px;
      min-width: 0;
    }}
    .drawer {{
      width: min(100%, 520px);
      max-height: calc(100vh - 40px);
      overflow: auto;
    }}
    .task-detail-drawer {{
      position: sticky;
      top: 20px;
      width: 100%;
      display: grid;
      gap: 12px;
      align-content: start;
    }}
    .task-drawer-header {{
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      gap: 10px;
      align-items: flex-start;
      border-bottom: 1px solid var(--line);
      padding-bottom: 10px;
    }}
    .task-drawer-header h2 {{
      margin: 0 0 3px;
      font-size: 18px;
    }}
    .task-drawer-title {{
      display: grid;
      grid-template-columns: auto minmax(0, 1fr);
      gap: 4px 8px;
      align-items: center;
      min-width: 0;
    }}
    .task-drawer-title strong,
    .task-drawer-title span {{
      overflow-wrap: anywhere;
    }}
    .task-drawer-title code {{
      grid-column: 2;
      overflow-wrap: anywhere;
    }}
    .modal {{
      width: min(100%, 640px);
      max-height: calc(100vh - 40px);
      overflow: auto;
      box-shadow: 0 18px 50px rgba(15, 23, 42, .16);
    }}
    .confirm-modal-backdrop[hidden] {{
      display: none;
    }}
    .confirm-modal-backdrop {{
      position: fixed;
      inset: 0;
      z-index: 80;
      display: grid;
      place-items: center;
      padding: 20px;
      background: rgba(15, 23, 42, .48);
    }}
    .confirm-modal {{
      display: grid;
      gap: 14px;
    }}
    .confirm-modal-header {{
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      gap: 10px 16px;
      align-items: flex-start;
    }}
    .confirm-modal-header h2 {{
      margin: 0;
    }}
    .confirm-modal-body {{
      display: grid;
      gap: 12px;
    }}
    .confirm-modal-summary {{
      display: grid;
      gap: 10px;
      margin: 0;
    }}
    .confirm-modal-summary div {{
      min-width: 0;
    }}
    .confirm-modal-summary dt {{
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0;
    }}
    .confirm-modal-summary dd {{
      margin: 3px 0 0;
      overflow-wrap: anywhere;
      font-weight: 700;
    }}
    .confirm-modal-notes {{
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #f8fafc;
      padding: 10px 12px;
    }}
    .confirm-modal-notes h3 {{
      margin: 0 0 6px;
      font-size: 13px;
    }}
    .confirm-modal-actions {{
      display: flex;
      flex-wrap: wrap;
      justify-content: flex-end;
      gap: 10px;
      border-top: 1px solid var(--line);
      padding-top: 12px;
    }}
    .confirm-modal-cancel {{
      background: #fff;
      color: #0d5f59;
    }}
    .metric {{
      padding: 14px;
      min-height: 86px;
    }}
    .cockpit-summary {{
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    }}
    .cockpit-metric {{
      color: inherit;
      text-decoration: none;
      display: block;
      transition: border-color .12s ease, box-shadow .12s ease;
    }}
    .cockpit-metric:hover {{
      border-color: #aeb9c8;
      box-shadow: 0 8px 20px rgba(15, 23, 42, .07);
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
    .metric small {{
      display: block;
      margin-top: 7px;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.35;
      overflow-wrap: anywhere;
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
    .badge.pass, .badge.ready, .badge.in_progress, .badge.running, .badge.active, .badge.approved, .badge.accepted, .badge.implemented, .badge.read, .badge.validation {{
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
    .current-execution-bar {{
      position: sticky;
      top: 0;
      z-index: 20;
      display: grid;
      grid-template-columns: minmax(0, 1.35fr) minmax(280px, .9fr) auto;
      gap: 14px;
      align-items: center;
      margin-bottom: 16px;
      padding: 12px 14px;
      background: #ffffff;
      border: 1px solid #c6d0de;
      border-radius: 8px;
      box-shadow: 0 10px 24px rgba(15, 23, 42, .09);
    }}
    .current-execution-bar.no-current {{
      grid-template-columns: minmax(0, 1fr) auto;
    }}
    .current-execution-main {{
      display: grid;
      gap: 6px;
      min-width: 0;
    }}
    .current-execution-kicker {{
      color: var(--muted);
      font-size: 11px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0;
    }}
    .current-execution-title {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
      min-width: 0;
    }}
    .current-execution-title strong,
    .current-execution-next strong {{
      overflow-wrap: anywhere;
    }}
    .current-execution-next {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      color: var(--muted);
    }}
    .current-execution-next span {{
      color: var(--text);
      font-weight: 700;
    }}
    .current-execution-warning {{
      margin: 0;
      color: var(--warn);
      font-weight: 700;
      overflow-wrap: anywhere;
    }}
    .current-execution-signals {{
      display: grid;
      grid-template-columns: repeat(2, minmax(130px, 1fr));
      gap: 8px;
      min-width: 0;
    }}
    .current-execution-signal {{
      display: grid;
      gap: 5px;
      min-width: 0;
      padding: 8px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #f8fafc;
    }}
    .current-execution-signal > span {{
      color: var(--muted);
      font-size: 11px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0;
    }}
    .current-execution-signal code {{
      overflow-wrap: anywhere;
    }}
    .current-execution-actions {{
      display: flex;
      flex-wrap: wrap;
      justify-content: flex-end;
      gap: 8px;
      min-width: 190px;
    }}
    .current-execution-actions form {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
      margin: 0;
    }}
    .current-execution-actions .checkline {{
      min-height: 32px;
      color: var(--text);
      font-size: 12px;
    }}
    .current-execution-actions button,
    .current-execution-actions .button-link {{
      min-height: 32px;
      padding: 5px 10px;
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
    .cockpit-detail summary {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px 10px;
      align-items: center;
      cursor: pointer;
      font-weight: 700;
      margin-bottom: 8px;
    }}
    .cockpit-detail-panel .execution-status {{
      margin-top: 12px;
    }}
    .cockpit-detail-actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: center;
      margin-top: 12px;
    }}
    .cockpit-detail-actions form {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
      margin: 0;
    }}
    .detail-links {{
      margin: 12px 0 0;
    }}
    .owner-section-header {{
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      gap: 10px 16px;
      align-items: flex-start;
      margin-bottom: 12px;
    }}
    .owner-section-header h2 {{
      margin-bottom: 3px;
    }}
    .owner-section-header p {{
      margin: 0;
      color: var(--muted);
    }}
    .inspection-intro {{
      padding-top: 14px;
      padding-bottom: 14px;
    }}
    .inspection-intro .owner-section-header {{
      margin-bottom: 0;
    }}
    .inspection-intro-detail {{
      margin: 8px 0 0;
      max-width: 860px;
    }}
    .inspection-panel .owner-section-header {{
      margin-bottom: 10px;
    }}
    .inspection-panel .owner-section-header p {{
      max-width: 860px;
    }}
    .owner-queue-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 12px;
    }}
    .owner-action-card {{
      display: grid;
      gap: 10px;
      align-content: start;
    }}
    .owner-action-card-header {{
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      gap: 8px;
      align-items: center;
    }}
    .owner-action-card h3 {{
      margin: 0;
      font-size: 15px;
      line-height: 1.35;
      overflow-wrap: anywhere;
    }}
    .owner-action-card h3 code {{
      margin-right: 6px;
    }}
    .owner-next, .owner-detail {{
      margin: 0;
      overflow-wrap: anywhere;
    }}
    .owner-detail {{
      color: var(--muted);
    }}
    .owner-card-action {{
      display: flex;
      justify-content: flex-start;
      align-items: center;
      margin-top: 2px;
    }}
    .owner-card-action .button-link {{
      min-height: 32px;
      padding: 5px 10px;
    }}
    .owner-action-more {{
      border-style: dashed;
      background: #fbfcfe;
    }}
    .owner-signals .cockpit-detail {{
      display: grid;
      gap: 12px;
    }}
    .health-summary-header {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px 16px;
      align-items: center;
      justify-content: space-between;
    }}
    .health-summary-header h2 {{
      margin: 0;
    }}
    .health-summary-counts {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
    }}
    .health-count {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      min-height: 26px;
      border-radius: 999px;
      padding: 3px 10px;
      font-size: 12px;
      font-weight: 700;
      background: #eef2f7;
      color: #334155;
      white-space: nowrap;
    }}
    .health-count.pass {{
      background: var(--accent-soft);
      color: var(--accent);
    }}
    .health-count.warn, .health-count.unknown {{
      background: var(--warn-soft);
      color: var(--warn);
    }}
    .health-count.fail {{
      background: var(--fail-soft);
      color: var(--fail);
    }}
    .health-detail {{
      margin-top: 12px;
      padding-top: 10px;
      border-top: 1px solid var(--line);
    }}
    .health-detail summary {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
      cursor: pointer;
      font-weight: 700;
    }}
    .health-detail table {{
      margin-top: 10px;
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
    .doctor-health-center {{
      display: grid;
      gap: 12px;
    }}
    .doctor-summary-header {{
      align-items: flex-start;
    }}
    .doctor-status-strip {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px 14px;
      align-items: center;
      padding: 12px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fbfcfe;
    }}
    .doctor-overall-status {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
    }}
    .doctor-overall-status > span,
    .doctor-finding-command strong,
    .doctor-finding-actions strong {{
      color: var(--muted);
      font-size: 12px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0;
    }}
    .doctor-summary-note {{
      flex: 1 1 280px;
      margin: 0;
      color: var(--muted);
      overflow-wrap: anywhere;
    }}
    .doctor-action-strip {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: center;
    }}
    .doctor-action-strip form,
    .doctor-finding-actions form {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
      margin: 0;
    }}
    .doctor-action-strip .checkline,
    .doctor-finding-actions .checkline {{
      min-height: 32px;
      font-size: 12px;
    }}
    .doctor-action-strip button,
    .doctor-action-strip .button-link,
    .doctor-finding-actions button {{
      min-height: 32px;
      padding: 5px 10px;
    }}
    .doctor-section-header {{
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      gap: 10px 16px;
      align-items: center;
      margin-bottom: 12px;
    }}
    .doctor-section-header h2 {{
      margin: 0;
    }}
    .doctor-finding-group {{
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
      overflow: hidden;
    }}
    .doctor-finding-group + .doctor-finding-group {{
      margin-top: 10px;
    }}
    .doctor-finding-group summary {{
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      gap: 8px 12px;
      align-items: center;
      cursor: pointer;
      padding: 10px 12px;
      background: #f1f4f8;
      font-weight: 700;
    }}
    .doctor-group-fail summary {{
      background: var(--fail-soft);
    }}
    .doctor-group-warn summary,
    .doctor-group-unknown summary {{
      background: var(--warn-soft);
    }}
    .doctor-group-pass summary {{
      background: var(--accent-soft);
    }}
    .doctor-finding-list {{
      display: grid;
      gap: 10px;
      padding: 12px;
    }}
    .doctor-finding-card {{
      display: grid;
      gap: 10px;
      min-width: 0;
      border: 1px solid var(--line);
      border-left: 4px solid #94a3b8;
      border-radius: 6px;
      padding: 12px;
      background: #fff;
    }}
    .doctor-card-pass {{
      border-left-color: var(--accent);
    }}
    .doctor-card-warn,
    .doctor-card-unknown {{
      border-left-color: var(--warn);
    }}
    .doctor-card-fail {{
      border-left-color: var(--fail);
    }}
    .doctor-finding-head {{
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      gap: 8px 12px;
      align-items: center;
    }}
    .doctor-finding-head h3 {{
      margin: 0;
      font-size: 15px;
      line-height: 1.35;
      overflow-wrap: anywhere;
    }}
    .doctor-finding-message {{
      margin: 0;
      overflow-wrap: anywhere;
    }}
    .doctor-finding-body {{
      display: grid;
      grid-template-columns: minmax(0, 1.25fr) minmax(220px, .75fr);
      gap: 12px;
      align-items: start;
    }}
    .doctor-finding-command,
    .doctor-finding-actions {{
      display: grid;
      gap: 7px;
      min-width: 0;
    }}
    .doctor-finding-command code {{
      display: block;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 8px;
      background: #f8fafc;
      white-space: normal;
      overflow-wrap: anywhere;
    }}
    .doctor-finding-details {{
      border-top: 1px solid var(--line);
      padding-top: 8px;
    }}
    .doctor-finding-details summary {{
      cursor: pointer;
      color: var(--muted);
      font-weight: 700;
    }}
    .doctor-finding-details pre {{
      margin: 8px 0 0;
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
    .compact-next {{
      display: block;
      max-width: 260px;
      overflow-wrap: anywhere;
    }}
    .compact-next strong {{
      color: var(--text);
    }}
    .compact-blocker {{
      color: var(--warn);
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
      gap: 16px;
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
    .settings-card-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 14px;
      align-items: start;
    }}
    .settings-card {{
      display: grid;
      gap: 12px;
      align-content: start;
    }}
    .settings-card-primary {{
      grid-column: 1 / -1;
    }}
    .settings-card-guarded {{
      border-color: #f0c36d;
      background: #fffdf6;
    }}
    .settings-card-header {{
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      gap: 8px 12px;
      align-items: flex-start;
    }}
    .settings-card-header h3 {{
      margin: 0 0 4px;
      font-size: 15px;
    }}
    .settings-card-header p {{
      margin: 0;
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
      display: grid;
      gap: 8px;
    }}
    .setting-control .checkline {{
      justify-content: flex-start;
    }}
    .settings-policy-context {{
      display: grid;
      gap: 8px;
    }}
    .locked-control {{
      color: #0d5f59;
      font-weight: 700;
    }}
    .setting-row-locked {{
      background: #f8fafc;
      margin: 0 -8px;
      padding-left: 8px;
      padding-right: 8px;
      border-radius: 6px;
    }}
    .settings-card-guarded .setting-row-checkbox {{
      border-color: #f4d99a;
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
    .effective-policy-summary-header {{
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      gap: 8px;
      align-items: center;
      margin-bottom: 10px;
    }}
    .effective-policy-summary-header h2,
    .effective-policy-summary-header h4 {{
      margin: 0;
    }}
    .effective-policy-summary-header h4 {{
      font-size: 13px;
    }}
    .effective-policy-summary-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 10px;
      margin: 0;
    }}
    .effective-policy-summary-grid div {{
      min-width: 0;
    }}
    .effective-policy-summary-grid dt {{
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: .04em;
    }}
    .effective-policy-summary-grid dd {{
      margin: 4px 0 0;
      font-weight: 700;
      overflow-wrap: anywhere;
    }}
    .effective-policy-summary-compact {{
      display: grid;
      gap: 8px;
      border-top: 1px solid var(--line);
      margin-top: 8px;
      padding-top: 8px;
    }}
    .effective-policy-summary-compact .effective-policy-summary-grid {{
      grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
      gap: 8px;
    }}
    .incomplete-run-warning {{
      border: 1px solid #f0c36d;
      border-radius: 6px;
      background: var(--warn-soft);
      color: var(--warn);
      padding: 12px;
      margin: 0 0 16px;
      display: grid;
      gap: 6px;
    }}
    .incomplete-run-warning strong {{
      color: var(--warn);
    }}
    .incomplete-run-warning p {{
      margin: 0;
    }}
    .incomplete-run-warning .muted {{
      color: var(--warn);
      opacity: .86;
    }}
    .incomplete-run-warning-compact {{
      margin: 8px 0;
    }}
    .incomplete-run-confirm {{
      justify-content: flex-start;
      color: var(--warn);
      font-weight: 700;
    }}
    .pipeline-run-summary {{
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    }}
    .pipeline-run-monitor {{
      display: grid;
      gap: 16px;
    }}
    .pipeline-run-header,
    .pipeline-live-access-header {{
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      gap: 10px 16px;
      align-items: flex-start;
    }}
    .pipeline-run-header h2,
    .pipeline-run-header p,
    .pipeline-live-access-header h3 {{
      margin: 0;
    }}
    .pipeline-run-links {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      justify-content: flex-end;
    }}
    .pipeline-session-identity {{
      margin-top: 6px;
    }}
    .pipeline-run-layout {{
      display: grid;
      grid-template-columns: minmax(0, 1.25fr) minmax(280px, .75fr);
      gap: 16px;
      align-items: start;
    }}
    .pipeline-run-progress,
    .pipeline-run-next {{
      min-width: 0;
    }}
    .pipeline-run-progress h3,
    .pipeline-run-next h3,
    .pipeline-detail-stack h3 {{
      margin: 0 0 10px;
      font-size: 14px;
    }}
    .pipeline-run-next {{
      border-left: 1px solid var(--line);
      padding-left: 16px;
    }}
    .pipeline-live-access {{
      border-top: 1px solid var(--line);
      padding-top: 14px;
    }}
    .pipeline-live-access .pipeline-live-log {{
      margin-bottom: 0;
    }}
    .pipeline-queue-compact {{
      display: grid;
      gap: 12px;
    }}
    .pipeline-queue-strip {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 12px;
      align-items: center;
    }}
    .pipeline-queue-next,
    .pipeline-queue-counts {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
      min-width: 0;
    }}
    .pipeline-queue-next strong {{
      overflow-wrap: anywhere;
    }}
    .pipeline-queue-counts {{
      justify-content: flex-end;
    }}
    .pipeline-queue-compact table {{
      min-width: 620px;
    }}
    .pipeline-compact-section {{
      padding: 0;
      overflow: hidden;
    }}
    .pipeline-compact-section summary {{
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      gap: 8px 16px;
      padding: 14px 16px;
      cursor: pointer;
      background: #f8fafc;
      font-weight: 700;
    }}
    .pipeline-compact-section summary span:last-child {{
      color: var(--muted);
      font-weight: 600;
    }}
    .pipeline-compact-body {{
      border-top: 1px solid var(--line);
      padding: 16px;
      overflow-x: auto;
    }}
    .pipeline-detail-stack {{
      display: grid;
      gap: 16px;
    }}
    .pipeline-compact-subsection {{
      border-top: 1px solid var(--line);
      padding-top: 12px;
    }}
    .pipeline-compact-subsection summary {{
      cursor: pointer;
      color: #0d5f59;
      font-weight: 700;
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
    .pipeline-action-groups-safety {{
      margin-top: 8px;
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
    .pipeline-action-group form {{
      display: grid;
      gap: 8px;
      margin-top: 8px;
    }}
    .pipeline-action-group form:first-of-type {{
      margin-top: 0;
    }}
    .pipeline-action-group button {{
      width: 100%;
    }}
    .safe-actions {{
      border-color: #b8ded1;
      background: #f7fffb;
    }}
    .progress-actions {{
      border-color: #c3d4ec;
      background: #f7fbff;
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
    .pipeline-live-log {{
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fbfcfe;
      padding: 12px;
      margin: 8px 0 14px;
    }}
    .pipeline-live-log .review-grid {{
      margin-top: 10px;
    }}
    .pipeline-live-log-streams {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 10px;
      margin-top: 12px;
    }}
    .pipeline-live-log-stream {{
      display: grid;
      gap: 8px;
      min-width: 0;
    }}
    .pipeline-live-log-output {{
      min-height: 160px;
      max-height: 360px;
      overflow: auto;
      margin: 0;
      background: #111827;
      color: #f8fafc;
      border-color: #111827;
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
    .change-queue-highlight summary {{
      background: #fff4d6;
    }}
    .change-row-needs-approval td:first-child {{
      border-left: 4px solid #c47f00;
    }}
    .change-create-panel summary {{
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      gap: 8px;
      cursor: pointer;
    }}
    .change-create-panel form {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: center;
      padding-top: 12px;
    }}
    .change-detail-panel {{
      min-width: 240px;
    }}
    .change-detail-body .review-field {{
      overflow-wrap: anywhere;
    }}
    .change-primary-action .row-action {{
      min-width: 200px;
    }}
    .task-detail-panel {{
      min-width: 220px;
      max-width: min(760px, calc(100vw - 80px));
      overflow-wrap: anywhere;
    }}
    .task-selected-detail .task-detail-panel {{
      max-width: none;
    }}
    .task-detail-panel summary {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
      justify-content: space-between;
      cursor: pointer;
      color: #0d5f59;
      font-weight: 700;
    }}
    .task-detail-body {{
      display: grid;
      gap: 14px;
      padding-top: 12px;
      min-width: min(620px, calc(100vw - 96px));
    }}
    .task-detail-drawer .task-detail-body {{
      min-width: 0;
      padding-top: 0;
    }}
    .task-selected-detail .task-detail-body {{
      min-width: 0;
    }}
    .task-detail-section {{
      border-top: 1px solid var(--line);
      padding-top: 12px;
      min-width: 0;
    }}
    .task-detail-section:first-child {{
      border-top: 0;
      padding-top: 0;
    }}
    .task-detail-section h4 {{
      margin: 0 0 8px;
      font-size: 13px;
    }}
    .task-detail-section table {{
      margin-top: 6px;
    }}
    .task-detail-section .review-grid {{
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    }}
    .task-diagnostic-section {{
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 0;
      overflow: hidden;
    }}
    .task-diagnostic-section summary {{
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      gap: 8px 16px;
      padding: 10px 12px;
      cursor: pointer;
      background: #f1f4f8;
      font-weight: 700;
    }}
    .task-diagnostic-body {{
      padding: 10px 12px 12px;
    }}
    .task-diagnostic-body table {{
      margin-top: 0;
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
    .diagnostics-panel {{
      padding: 0;
      overflow: hidden;
    }}
    .diagnostics-panel summary,
    .review-queue-group summary {{
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      gap: 8px 16px;
      padding: 10px 12px;
      cursor: pointer;
      background: #f1f4f8;
    }}
    .diagnostics-panel summary span,
    .review-queue-group summary span {{
      color: var(--muted);
      font-weight: 600;
    }}
    .diagnostics-panel table {{
      border-top: 1px solid var(--line);
    }}
    .review-queue-group {{
      border: 1px solid var(--line);
      border-radius: 8px;
      margin-top: 10px;
      background: #fff;
      overflow: hidden;
    }}
    .review-queue-group > .muted {{
      margin: 0;
      padding: 10px 12px 0;
    }}
    .review-queue-group table {{
      border-top: 1px solid var(--line);
      margin-top: 10px;
    }}
    .review-signal {{
      color: #374151;
      overflow-wrap: anywhere;
    }}
    .review-row-details {{
      min-width: 180px;
      max-width: min(760px, calc(100vw - 80px));
    }}
    .review-row-details summary {{
      color: #0d5f59;
      cursor: pointer;
      font-weight: 700;
    }}
    .review-row-package {{
      min-width: min(620px, calc(100vw - 96px));
      padding-top: 10px;
    }}
    .review-row-package .review-package {{
      border: 1px solid var(--line);
      border-radius: 8px;
      margin-top: 0;
      padding: 12px;
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
    @media (max-width: 900px) {{
      .app-shell {{ grid-template-columns: 1fr; }}
      .sidebar {{
        position: static;
        height: auto;
        border-right: 0;
        border-bottom: 1px solid #111827;
      }}
      .sidebar-header {{
        padding-left: 0;
        padding-right: 0;
      }}
      .sidebar nav {{
        gap: 14px;
      }}
      .nav-group-links {{
        grid-template-columns: repeat(auto-fit, minmax(128px, 1fr));
      }}
      .queue-layout {{
        grid-template-columns: 1fr;
      }}
      .task-page-layout {{
        grid-template-columns: 1fr;
      }}
      .task-detail-drawer {{
        position: static;
        max-height: none;
      }}
      .current-execution-bar,
      .current-execution-bar.no-current {{
        grid-template-columns: 1fr;
      }}
      .current-execution-actions {{
        justify-content: flex-start;
      }}
      .pipeline-run-layout,
      .pipeline-queue-strip {{
        grid-template-columns: 1fr;
      }}
      .pipeline-run-next {{
        border-left: 0;
        border-top: 1px solid var(--line);
        padding-left: 0;
        padding-top: 14px;
      }}
      .pipeline-run-links,
      .pipeline-queue-counts {{
        justify-content: flex-start;
      }}
      .doctor-finding-body {{
        grid-template-columns: 1fr;
      }}
    }}
    @media (max-width: 640px) {{
      .top-area, .main-content {{ padding-left: 14px; padding-right: 14px; }}
      h1 {{ font-size: 21px; }}
      .nav-group-links {{ grid-template-columns: 1fr 1fr; }}
      .sidebar nav a {{ justify-content: center; text-align: center; }}
      .metric strong {{ font-size: 18px; }}
      .card-grid, .queue-grid {{ grid-template-columns: 1fr; }}
      .current-execution-signals {{ grid-template-columns: 1fr; }}
      .drawer, .modal {{ width: 100%; max-height: none; }}
      .confirm-modal-backdrop {{ align-items: stretch; padding: 12px; }}
      .confirm-modal-actions {{ justify-content: stretch; }}
      .confirm-modal-actions button {{ flex: 1 1 150px; }}
      .result-step {{ grid-template-columns: 1fr; }}
      .setting-row {{ grid-template-columns: 1fr; }}
      .settings-footer {{ justify-content: stretch; }}
      .settings-footer .button-link, .settings-footer button {{ flex: 1 1 160px; }}
    }}
  </style>
</head>
<body>
  <div class="app-shell">
    <aside class="sidebar" aria-label="Web Control Center navigation">
      <div class="sidebar-header">
        <a class="brand" href="/">AI Control Center</a>
        <span class="brand-kicker">Project Control</span>
      </div>
      {nav}
    </aside>
    <div class="page-shell">
      <header class="top-area">
        <p class="eyebrow">Web Control Center</p>
        <h1>{title}</h1>
      </header>
      <main class="main-content">{body}</main>
    </div>
  </div>
  {confirm_modal}
  {confirm_script}
</body>
</html>
""".format(
        title=escape(title),
        nav=render_nav(active),
        body=body,
        confirm_modal=confirm_modal_markup(
            effective_policy_summary=confirm_policy_summary,
        ),
        confirm_script=confirm_modal_script(),
    )


def confirm_modal_markup(*, effective_policy_summary: str = "") -> str:
    policy_attr = ""
    if effective_policy_summary:
        policy_attr = ' data-confirm-effective-policy-summary="{}"'.format(
            escape(effective_policy_summary)
        )
    return """
  <div class="confirm-modal-backdrop" data-confirm-modal-backdrop{} hidden>
    <section class="modal confirm-modal" role="dialog" aria-modal="true" aria-labelledby="confirm-modal-title" data-confirm-modal-panel>
      <div class="confirm-modal-header">
        <div>
          <h2 id="confirm-modal-title">Confirm Owner Action</h2>
          <p class="muted">Review the action before the confirmed POST is sent.</p>
        </div>
        <span class="pill">POST /actions</span>
      </div>
      <div class="confirm-modal-body">
        <dl class="confirm-modal-summary">
          <div>
            <dt>Action</dt>
            <dd data-confirm-modal-action>Action</dd>
          </div>
          <div data-confirm-modal-row="target">
            <dt>Target</dt>
            <dd data-confirm-modal-target>Target</dd>
          </div>
          <div data-confirm-modal-row="policy">
            <dt>Policy</dt>
            <dd data-confirm-modal-policy>Policy</dd>
          </div>
        </dl>
        <div class="confirm-modal-notes" data-confirm-modal-notes></div>
        <p class="muted">Server-side confirmation and workflow requirements remain enforced after this dialog.</p>
      </div>
      <div class="confirm-modal-actions">
        <button type="button" class="confirm-modal-cancel" data-confirm-modal-cancel>Cancel</button>
        <button type="button" data-confirm-modal-submit>Confirm Action</button>
      </div>
    </section>
  </div>
""".format(policy_attr)


def confirm_modal_script() -> str:
    return """<script>
(function() {
  function startActionConfirmModal() {
    var backdrop = document.querySelector("[data-confirm-modal-backdrop]");
    if (!backdrop) {
      return;
    }

    var title = document.getElementById("confirm-modal-title");
    var actionTarget = backdrop.querySelector("[data-confirm-modal-action]");
    var targetTarget = backdrop.querySelector("[data-confirm-modal-target]");
    var policyTarget = backdrop.querySelector("[data-confirm-modal-policy]");
    var targetRow = backdrop.querySelector("[data-confirm-modal-row='target']");
    var policyRow = backdrop.querySelector("[data-confirm-modal-row='policy']");
    var notesTarget = backdrop.querySelector("[data-confirm-modal-notes]");
    var confirmButton = backdrop.querySelector("[data-confirm-modal-submit]");
    var cancelButton = backdrop.querySelector("[data-confirm-modal-cancel]");
    var state = {form: null, submitter: null, previousFocus: null};

    function namedControl(form, name) {
      var control = form.elements[name];
      if (!control) {
        return null;
      }
      if (typeof control.length === "number" && !control.tagName) {
        return control[0] || null;
      }
      return control;
    }

    function controlValue(control) {
      if (!control) {
        return "";
      }
      if (typeof control.length === "number" && !control.tagName) {
        return control.value || "";
      }
      if (control.tagName === "SELECT") {
        var selected = control.selectedOptions && control.selectedOptions[0];
        return selected ? (selected.textContent || selected.value || "") : (control.value || "");
      }
      if (control.type === "checkbox" || control.type === "radio") {
        return control.checked ? (control.value || "yes") : "";
      }
      return control.value || "";
    }

    function fieldValue(form, name) {
      return controlValue(namedControl(form, name)).trim();
    }

    function isChecked(form, name) {
      var control = namedControl(form, name);
      return !!(control && control.checked);
    }

    function actionId(form) {
      return fieldValue(form, "action") || form.dataset.confirmActionId || "action";
    }

    function actionLabel(form, submitter) {
      return (
        form.dataset.confirmActionLabel ||
        (submitter && (submitter.value || submitter.textContent || "").trim()) ||
        actionId(form)
      );
    }

    function targetSummary(form) {
      if (form.dataset.confirmTarget) {
        return form.dataset.confirmTarget;
      }
      var candidates = [
        ["task", "Task"],
        ["change", "Change"],
        ["session_id", "Pipeline session"],
        ["epic", "Epic"],
        ["current_task_ref", "Task"],
        ["current_task_id", "Task"]
      ];
      for (var index = 0; index < candidates.length; index += 1) {
        var value = fieldValue(form, candidates[index][0]);
        if (value) {
          return candidates[index][1] + ": " + value;
        }
      }
      var targets = {
        "project.doctor": "Project doctor",
        "project.protected_check": "Protected project files",
        "project.render": "Project generated views",
        "docs.render": "Documentation generated views",
        "pipeline.render": "Pipeline status",
        "current.clear": "Current task selection"
      };
      return targets[actionId(form)] || "Registered action " + actionId(form);
    }

    function policySummary(form) {
      if (form.dataset.confirmPolicySummary) {
        return form.dataset.confirmPolicySummary;
      }
      var modalPolicySummaryActions = {
        "task.prepare_for_codex": true,
        "ui.run_selected_task": true
      };
      if (modalPolicySummaryActions[actionId(form)] && backdrop.dataset.confirmEffectivePolicySummary) {
        return backdrop.dataset.confirmEffectivePolicySummary;
      }
      var parts = [];
      var policy = fieldValue(form, "policy");
      if (policy) {
        parts.push("Policy: " + policy);
      }
      var maxTasks = fieldValue(form, "max_tasks");
      if (maxTasks) {
        parts.push("Max tasks: " + maxTasks);
      }
      var orderBy = fieldValue(form, "order_by");
      if (orderBy) {
        parts.push("Order: " + orderBy);
      }
      if (isChecked(form, "auto_create_missing_changes")) {
        parts.push("Auto-create missing Changes: enabled");
      }
      if (isChecked(form, "owner_approve_required_changes")) {
        parts.push("Owner approval for required Changes: enabled");
      }
      return parts.join("; ");
    }

    function readableFieldName(name) {
      var labels = {
        "notes": "Owner Notes",
        "approval_note": "Approval Note",
        "auto_close_note": "Auto-close Owner Note"
      };
      if (labels[name]) {
        return labels[name];
      }
      return name.replace(/_/g, " ").replace(/\\b\\w/g, function(match) {
        return match.toUpperCase();
      });
    }

    function fieldLabel(control) {
      if (!control) {
        return "Owner note";
      }
      var label = control.closest ? control.closest("label") : null;
      if (label) {
        var text = (label.textContent || "").trim().replace(/\\s+/g, " ");
        if (text) {
          return text;
        }
      }
      return readableFieldName(control.name || "note");
    }

    function requiredNoteNames(form) {
      var names = [];
      var configured = (form.dataset.confirmRequiredNoteFields || "").split(",");
      configured.forEach(function(name) {
        name = name.trim();
        if (name && names.indexOf(name) === -1) {
          names.push(name);
        }
      });
      if (isChecked(form, "owner_approve_required_changes") && names.indexOf("approval_note") === -1) {
        names.push("approval_note");
      }
      return names;
    }

    function isNoteControl(control) {
      var name = control.name || "";
      return name.indexOf("note") !== -1 || name.indexOf("notes") !== -1;
    }

    function clearCustomValidity(form) {
      Array.prototype.forEach.call(form.elements, function(control) {
        if (control && control.setCustomValidity) {
          control.setCustomValidity("");
        }
      });
    }

    function validateForm(form) {
      clearCustomValidity(form);
      var controls = Array.prototype.slice.call(form.elements);
      for (var index = 0; index < controls.length; index += 1) {
        var control = controls[index];
        if (!control || control.disabled || control.name === "confirm") {
          continue;
        }
        if (control.required && control.checkValidity && !control.checkValidity()) {
          control.reportValidity();
          return false;
        }
      }
      var requiredNotes = requiredNoteNames(form);
      for (var noteIndex = 0; noteIndex < requiredNotes.length; noteIndex += 1) {
        var noteControl = namedControl(form, requiredNotes[noteIndex]);
        if (!noteControl || fieldValue(form, requiredNotes[noteIndex])) {
          continue;
        }
        if (noteControl.setCustomValidity) {
          noteControl.setCustomValidity("This owner note is required before confirming.");
          noteControl.addEventListener("input", function(event) {
            event.currentTarget.setCustomValidity("");
          }, {once: true});
          noteControl.reportValidity();
        }
        return false;
      }
      return true;
    }

    function requiredNoteSummaries(form) {
      var items = [];
      var seen = {};
      Array.prototype.forEach.call(form.elements, function(control) {
        if (!control || control.disabled || control.name === "confirm") {
          return;
        }
        if (control.required && isNoteControl(control)) {
          seen[control.name] = true;
          items.push({
            label: fieldLabel(control),
            status: controlValue(control).trim() ? "provided" : "missing"
          });
        }
      });
      requiredNoteNames(form).forEach(function(name) {
        if (seen[name]) {
          return;
        }
        var control = namedControl(form, name);
        items.push({
          label: control ? fieldLabel(control) : readableFieldName(name),
          status: fieldValue(form, name) ? "provided" : "missing"
        });
      });
      return items;
    }

    function renderRequiredNotes(form) {
      var notes = requiredNoteSummaries(form);
      if (!notes.length) {
        notesTarget.innerHTML = "<h3>Owner Notes</h3><p class=\\"empty\\">No required owner note field is registered for this action.</p>";
        return;
      }
      var list = document.createElement("ul");
      list.className = "compact-list";
      notes.forEach(function(note) {
        var item = document.createElement("li");
        var strong = document.createElement("strong");
        strong.textContent = note.label + ": ";
        item.appendChild(strong);
        item.appendChild(document.createTextNode(note.status));
        list.appendChild(item);
      });
      notesTarget.innerHTML = "<h3>Required Owner Notes</h3>";
      notesTarget.appendChild(list);
    }

    function setOptionalRow(row, target, value) {
      if (!row || !target) {
        return;
      }
      if (!value) {
        row.hidden = true;
        target.textContent = "";
        return;
      }
      row.hidden = false;
      target.textContent = value;
    }

    function openModal(form, submitter) {
      state.form = form;
      state.submitter = submitter;
      state.previousFocus = document.activeElement;
      var label = actionLabel(form, submitter);
      title.textContent = "Confirm " + label;
      actionTarget.textContent = label + " (" + actionId(form) + ")";
      setOptionalRow(targetRow, targetTarget, targetSummary(form));
      setOptionalRow(policyRow, policyTarget, policySummary(form));
      renderRequiredNotes(form);
      backdrop.hidden = false;
      confirmButton.focus();
    }

    function closeModal(restoreFocus) {
      backdrop.hidden = true;
      if (restoreFocus && state.previousFocus && state.previousFocus.focus) {
        state.previousFocus.focus();
      }
      state.form = null;
      state.submitter = null;
      state.previousFocus = null;
    }

    function submitConfirmed() {
      var form = state.form;
      var submitter = state.submitter;
      if (!form || !validateForm(form)) {
        return;
      }
      var confirmControl = namedControl(form, "confirm");
      if (confirmControl) {
        confirmControl.checked = true;
      }
      form.dataset.confirmModalApproved = "1";
      closeModal(false);
      if (form.requestSubmit) {
        if (submitter && submitter.form === form) {
          form.requestSubmit(submitter);
        } else {
          form.requestSubmit();
        }
      } else {
        form.submit();
      }
    }

    Array.prototype.forEach.call(
      document.querySelectorAll('form[data-confirm-modal="action"]'),
      function(form) {
        form.noValidate = true;
        form.addEventListener("click", function(event) {
          var target = event.target;
          if (!target || !target.closest) {
            return;
          }
          var submitter = target.closest('button[type="submit"], input[type="submit"]');
          if (submitter && submitter.form === form) {
            form._confirmSubmitter = submitter;
          }
        });
        form.addEventListener("submit", function(event) {
          if (form.dataset.confirmModalApproved === "1") {
            delete form.dataset.confirmModalApproved;
            return;
          }
          event.preventDefault();
          var submitter = event.submitter || form._confirmSubmitter || null;
          if (!validateForm(form)) {
            return;
          }
          openModal(form, submitter);
        });
      }
    );

    confirmButton.addEventListener("click", submitConfirmed);
    cancelButton.addEventListener("click", function() {
      closeModal(true);
    });
    backdrop.addEventListener("click", function(event) {
      if (event.target === backdrop) {
        closeModal(true);
      }
    });
    document.addEventListener("keydown", function(event) {
      if (event.key === "Escape" && !backdrop.hidden) {
        closeModal(true);
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", startActionConfirmModal);
  } else {
    startActionConfirmModal();
  }
})();
</script>"""


def render_nav(active: str) -> str:
    groups = []
    for group_label, items in NAV_GROUPS:
        links = []
        for href, label in items:
            class_name = ' class="active"' if href == active else ""
            links.append('<a href="{}"{}>{}</a>'.format(href, class_name, escape(label)))
        group_id = "nav-{}".format(css_token(group_label))
        groups.append(
            (
                '<section class="nav-group" aria-labelledby="{group_id}">'
                '<h2 class="nav-group-title" id="{group_id}">{label}</h2>'
                '<div class="nav-group-links">{links}</div>'
                "</section>"
            ).format(
                group_id=escape(group_id),
                label=escape(group_label),
                links="".join(links),
            )
        )
    return "<nav>{}</nav>".format("".join(groups))


def metric(label: str, value: str, *, data_field: str = "") -> str:
    data_attr = (
        ' data-pipeline-status-field="{}"'.format(escape(data_field))
        if data_field
        else ""
    )
    return '<div class="metric"{}><span>{}</span><strong>{}</strong></div>'.format(
        data_attr,
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
    compact: bool = False,
    details_open: bool = False,
) -> str:
    items = project_health_items(data)
    rows = project_health_rows(items, selected_task=selected_task)
    if compact:
        return compact_project_health_panel(items, rows, details_open=details_open)
    return (
        '<section class="panel health-panel">'
        "<h2>Project Health</h2>"
        "{}"
        "</section>"
    ).format(
        table(("Area", "Status", "Signal", "Repair / Check"), rows, "No health signals.")
    )


def project_health_items(data: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    health = _mapping(data.get("health"))
    doctor = _mapping(health.get("doctor"))
    artifacts = [
        artifact
        for artifact in health.get("artifacts") or []
        if isinstance(artifact, Mapping)
    ]
    return ([doctor] if doctor else []) + artifacts


def project_health_rows(
    items: Sequence[Mapping[str, Any]],
    *,
    selected_task: Mapping[str, Any] | None = None,
) -> list[str]:
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
                status_badge(health_summary_status(item.get("status"))),
                escape(detail),
                health_action_control(item, selected_task=selected_task),
            )
        )
    return rows


def compact_project_health_panel(
    items: Sequence[Mapping[str, Any]],
    rows: Sequence[str],
    *,
    details_open: bool = False,
) -> str:
    open_attr = " open" if details_open else ""
    return (
        '<section class="panel health-panel health-panel-compact" id="owner-health">'
        '<div class="health-summary-header">'
        "<h2>Project Health</h2>"
        "{}"
        "</div>"
        '<details class="health-detail"{}>'
        '<summary><span>Health details</span><span class="pill">{} signals</span></summary>'
        "{}"
        "</details>"
        "</section>"
    ).format(
        health_summary_counts_line(health_summary_counts(items)),
        open_attr,
        len(items),
        table(("Area", "Status", "Signal", "Repair / Check"), rows, "No health signals."),
    )


def health_summary_counts(items: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    counts = {status: 0 for status in ("PASS", "WARN", "FAIL", "UNKNOWN")}
    for item in items:
        counts[health_summary_status(item.get("status"))] += 1
    return counts


def health_summary_status(value: Any) -> str:
    status = str(value or "").strip().upper()
    if status in {"PASS", "WARN", "FAIL"}:
        return status
    return "UNKNOWN"


def health_summary_counts_line(counts: Mapping[str, int]) -> str:
    parts = []
    for status in ("PASS", "WARN", "FAIL", "UNKNOWN"):
        title = (
            ' title="Unknown means not reported yet, not a failure."'
            if status == "UNKNOWN"
            else ""
        )
        parts.append(
            '<span class="health-count {}"{}><strong>{}</strong> {}</span>'.format(
                status.lower(),
                title,
                escape(str(counts.get(status, 0))),
                status,
            )
        )
    return '<div class="health-summary-counts">{}</div>'.format("".join(parts))


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

    button_label = str(item.get("action_label") or action)
    if action == "codex.prompt.build":
        button_label = "Refresh Prompt"
    return action_form(action, fields, button_label=button_label)


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
    status = _query_value(query, "status")
    view = _query_value(query, "view")
    if view == "full":
        view = "inventory"
    if view not in TASK_VIEW_OPTIONS:
        wants_inventory = (
            bool(_query_value(query, "group"))
            or _query_enabled(query, "show_done")
            or status == "done"
        )
        view = "inventory" if wants_inventory else "queue"
    group = _query_value(query, "group") or "epic"
    if group not in TASK_GROUP_OPTIONS:
        group = "epic"
    return {
        "view": view,
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
    view_options = (
        ("queue", "Action Queue"),
        ("inventory", "Full Inventory"),
    )
    group_options = (
        ("epic", "Epic"),
        ("status", "Status"),
        ("none", "None"),
    )
    checked = " checked" if filters.get("show_done") else ""
    return (
        '<form class="task-controls" method="get" action="/tasks">'
        "{}{}{}{}{}{}"
        '<label class="checkline"><input type="checkbox" name="show_done" value="1"{}>Show done</label>'
        '<button type="submit">Apply</button>'
        '<a class="button-link secondary" href="/tasks">Reset</a>'
        "</form>"
    ).format(
        filter_select("view", "View", view_options, str(filters.get("view") or "queue")),
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
    pills.append(
        "view {}".format(
            "full inventory" if filters.get("view") == "inventory" else "action queue"
        )
    )
    if filters.get("initiative"):
        pills.append("initiative {}".format(filters.get("initiative")))
    if filters.get("epic"):
        pills.append("epic {}".format(filters.get("epic")))
    if filters.get("status"):
        pills.append("status {}".format(filters.get("status")))
    if filters.get("q"):
        pills.append('search "{}"'.format(filters.get("q")))
    if filters.get("view") == "inventory":
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
        if status == "deferred" and selected_status != "deferred":
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


def create_change_for_task_panel(
    task_options: Sequence[tuple[str, str]],
    default_task: str,
    *,
    compact: bool,
) -> str:
    open_attr = "" if compact else " open"
    summary = (
        "Available for eligible tasks"
        if compact
        else "Choose a task that needs controlled system evolution"
    )
    return (
        '<details class="panel action-panel change-create-panel"{}>'
        "<summary><strong>Create Change For Task</strong><span>{}</span></summary>"
        "{}"
        "</details>"
    ).format(
        open_attr,
        escape(summary),
        action_form(
            "evolution.create_for_task",
            [
                select_field_values("task", "Task", task_options)
                if task_options
                else input_field("task", "Task", default_task),
            ],
            button_label="Create Evolution Change",
        ),
    )


def change_decision_groups(
    changes: Sequence[Mapping[str, Any]],
) -> dict[str, list[Mapping[str, Any]]]:
    groups: dict[str, list[Mapping[str, Any]]] = {
        key: [] for key, _, _ in CHANGE_QUEUE_GROUPS
    }
    for change in changes:
        groups.setdefault(change_decision_group_key(change), []).append(change)
    return groups


def change_decision_group_key(change: Mapping[str, Any]) -> str:
    status = str(change.get("status") or "unknown")
    if status == "ready":
        return "needs_approval"
    if status in CHANGE_QUEUE_APPROVED_STATUSES:
        return "approved"
    if status == "in_review":
        return "in_review"
    if status == "accepted":
        return "accepted"
    return "blocked_or_other"


def change_decision_queue(
    groups: Mapping[str, Sequence[Mapping[str, Any]]],
    data: Mapping[str, Any],
) -> str:
    total = sum(len(groups.get(key, [])) for key, _, _ in CHANGE_QUEUE_GROUPS)
    return (
        '<section class="panel change-decision-queue">'
        '<div class="owner-section-header"><div><h2>Change Proposal Decision Queue</h2>'
        "<p>Owner decisions and blockers are grouped by current lifecycle state.</p></div>"
        '<div class="status-row">{}</div></div>'
        "{}"
        "</section>"
    ).format(
        change_queue_count_pills(groups),
        "".join(
            change_decision_group(key, title, description, groups.get(key, []), data)
            for key, title, description in CHANGE_QUEUE_GROUPS
        )
        if total
        else '<p class="empty">No Change Proposals match the filters.</p>',
    )


def change_queue_count_pills(
    groups: Mapping[str, Sequence[Mapping[str, Any]]],
) -> str:
    return "".join(
        '<span class="pill">{}: {}</span>'.format(
            escape(title),
            escape(len(groups.get(key, []))),
        )
        for key, title, _ in CHANGE_QUEUE_GROUPS
    )


def change_decision_group(
    key: str,
    title: str,
    description: str,
    changes: Sequence[Mapping[str, Any]],
    data: Mapping[str, Any],
) -> str:
    open_groups = {"needs_approval", "approved", "in_review"}
    open_attr = " open" if key in open_groups and changes else ""
    highlight_class = " change-queue-highlight" if key == "needs_approval" and changes else ""
    return (
        '<details class="task-group change-queue-group change-queue-group-{}{}"{}>'
        "<summary><strong>{}</strong><span>{} change{}</span></summary>"
        '<p class="muted task-action-group-note">{}</p>'
        "{}"
        "</details>"
    ).format(
        escape(css_token(key)),
        highlight_class,
        open_attr,
        escape(title),
        escape(len(changes)),
        "" if len(changes) == 1 else "s",
        escape(description),
        change_decision_table(
            changes,
            data,
            group_key=key,
            empty_text="No {} Change Proposals match the filters.".format(
                title.lower().replace(" / ", "-").replace(" ", "-")
            ),
        ),
    )


def change_decision_table(
    changes: Sequence[Mapping[str, Any]],
    data: Mapping[str, Any],
    *,
    group_key: str,
    empty_text: str,
) -> str:
    rows = [
        change_compact_row(change, data, group_key=group_key)
        for change in changes
    ]
    return table(
        (
            "Change",
            "Status",
            "Title",
            "Linked Task",
            "Next Action",
            "Details",
            "Primary Action",
        ),
        rows,
        empty_text,
    )


def change_compact_row(
    change: Mapping[str, Any],
    data: Mapping[str, Any],
    *,
    group_key: str,
) -> str:
    cells = [
        change_identity_cell(change),
        status_badge(str(change.get("status") or "unknown")),
        escape(change.get("title", "")),
        change_list_cell(change.get("linked_tasks"), limit=2),
        change_next_action_cell(change),
        change_detail_panel(change),
        change_primary_action_control(change, data),
    ]
    row_classes = [
        "change-row",
        "change-row-{}".format(css_token(group_key)),
        "change-status-{}".format(css_token(str(change.get("status") or "unknown"))),
    ]
    return '<tr class="{}">{}</tr>'.format(
        escape(" ".join(row_classes)),
        "".join("<td>{}</td>".format(cell) for cell in cells),
    )


def change_next_action_cell(change: Mapping[str, Any]) -> str:
    spec = change_primary_action_spec(change)
    if spec:
        return '<span class="compact-next"><strong>Next:</strong> {}</span>'.format(
            escape(spec.get("label") or spec.get("action") or "")
        )
    reason = change_blocker_reason(change)
    if reason:
        return (
            '<span class="compact-next compact-blocker">'
            "<strong>Blocked:</strong> {}</span>"
        ).format(escape(reason))
    status = str(change.get("status") or "unknown")
    if status == "accepted":
        return '<span class="muted">Accepted; inspect details.</span>'
    if status in {"rejected", "archived", "superseded"}:
        return '<span class="muted">Closed; inspect details.</span>'
    return '<span class="muted">No primary owner action.</span>'


def change_primary_action_control(
    change: Mapping[str, Any],
    data: Mapping[str, Any],
) -> str:
    spec = change_primary_action_spec(change)
    if spec:
        return '<div class="row-actions change-primary-action">{}</div>'.format(
            change_row_action(change, data, spec)
        )
    status = str(change.get("status") or "unknown")
    if status == "accepted":
        return '<span class="pill">Accepted</span>'
    if change_blocker_reason(change):
        return '<span class="pill">Inspect Blocker</span>'
    return '<span class="pill">Inspect Details</span>'


def change_primary_action_spec(change: Mapping[str, Any]) -> Mapping[str, Any]:
    specs = change_row_action_specs(change)
    return specs[0] if specs else {}


def change_blocker_reason(change: Mapping[str, Any]) -> str:
    hints = _mapping(change.get("pipeline_hints"))
    status = str(change.get("status") or "unknown")
    linked_task_blocker = task_queue_first_text(hints.get("linked_task_blockers"))
    if linked_task_blocker:
        return linked_task_blocker
    target_label = change_expected_action_label(status)
    for action in hints.get("actions") or []:
        if not isinstance(action, Mapping):
            continue
        if target_label and str(action.get("label") or "") != target_label:
            continue
        if action.get("available"):
            continue
        reason = str(action.get("reason") or "").strip()
        if reason:
            return change_compact_blocker_reason(reason, str(action.get("label") or ""))
    blocked = task_queue_first_text(hints.get("blocked_reasons"))
    if blocked:
        return change_compact_blocker_reason(blocked, "")
    return ""


def change_expected_action_label(status: str) -> str:
    if status == "ready":
        return "Approve Change"
    if status == "in_review":
        return "Accept Change"
    if status in CHANGE_QUEUE_APPROVED_STATUSES:
        return "Move to Review"
    return ""


def change_compact_blocker_reason(reason: str, label: str) -> str:
    text = " ".join(str(reason or "").split())
    prefix = "{} unavailable: ".format(label) if label else ""
    if prefix and text.startswith(prefix):
        text = text[len(prefix) :]
    if not prefix and " unavailable: " in text:
        text = text.split(" unavailable: ", 1)[1]
    return text[:177] + "..." if len(text) > 180 else text


def change_detail_panel(change: Mapping[str, Any]) -> str:
    change_id = str(change.get("id") or "Change")
    return (
        '<details class="task-detail-panel change-detail-panel">'
        '<summary><span>Details</span><span class="pill">{}</span></summary>'
        '<div class="task-detail-body change-detail-body">{}{}{}</div>'
        "</details>"
    ).format(
        escape(change_id),
        change_detail_context(change),
        change_detail_impact(change),
        change_detail_status(change),
    )


def change_detail_context(change: Mapping[str, Any]) -> str:
    rows = [
        review_field("Type", escape(change.get("change_type") or change.get("type") or "unknown")),
        review_field("Problem", escape(change.get("problem") or "No problem recorded.")),
        review_field("Rationale", escape(change.get("rationale") or "No rationale recorded.")),
        review_field("Proposal", escape(change.get("proposal") or "No proposal recorded.")),
        review_field(
            "Compatibility",
            escape(change.get("backward_compatibility") or "not recorded"),
        ),
        review_field("Migration", escape(change_migration_summary(change))),
    ]
    return (
        '<section class="task-detail-section">'
        "<h4>Change Proposal</h4>"
        '<div class="review-grid">{}</div>'
        "</section>"
    ).format("".join(rows))


def change_detail_impact(change: Mapping[str, Any]) -> str:
    rows = [
        review_field(
            "Affected Areas",
            text_list(change.get("affected_areas"), empty_text="No affected areas recorded."),
        ),
        review_field(
            "Affected Files",
            text_list(
                change.get("affected_files"),
                empty_text="No affected files recorded.",
                code=True,
            ),
        ),
        review_field("Impact", text_list(change.get("impact"), empty_text="No impact recorded.")),
        review_field("Risks", text_list(change.get("risks"), empty_text="No risks recorded.")),
    ]
    return (
        '<section class="task-detail-section">'
        "<h4>Impact</h4>"
        '<div class="review-grid">{}</div>'
        "</section>"
    ).format("".join(rows))


def change_detail_status(change: Mapping[str, Any]) -> str:
    rows = [
        review_field("Linked Tasks", change_list_cell(change.get("linked_tasks"), limit=8)),
        review_field("Approval", change_approval_cell(change)),
        review_field("Acceptance", change_acceptance_cell(change)),
        review_field("Updated", escape(change.get("updated_at") or "not recorded")),
        review_field("Action Gates", change_action_diagnostics(change)),
    ]
    superseded_by = str(change.get("superseded_by") or "")
    if superseded_by:
        rows.append(review_field("Superseded By", escape(superseded_by)))
    return (
        '<section class="task-detail-section">'
        "<h4>Status</h4>"
        '<div class="review-grid">{}</div>'
        "</section>"
    ).format("".join(rows))


def change_migration_summary(change: Mapping[str, Any]) -> str:
    if change.get("migration_required") is True:
        return "required"
    if change.get("migration_required") is False:
        return "not required"
    return "not recorded"


def change_action_diagnostics(change: Mapping[str, Any]) -> str:
    hints = _mapping(change.get("pipeline_hints"))
    rows = []
    for action in hints.get("actions") or []:
        if not isinstance(action, Mapping):
            continue
        label = str(action.get("label") or action.get("action") or "")
        available = bool(action.get("available"))
        reason = str(action.get("reason") or "")
        detail = "Available now."
        if reason:
            detail = (
                reason
                if available
                else "{} unavailable: {}".format(label, reason)
            )
        rows.append(
            "<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                escape(label),
                status_badge("available" if available else "blocked"),
                escape(detail),
            )
        )
    return table(
        ("Action", "Status", "Reason"),
        rows,
        "No action gate diagnostics recorded.",
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


def task_inventory_href(filters: Mapping[str, Any]) -> str:
    params = [("view", "inventory")]
    for name in ("initiative", "epic", "status", "q", "group"):
        value = str(filters.get(name) or "")
        if value:
            params.append((name, value))
    if filters.get("show_done"):
        params.append(("show_done", "1"))
    return "/tasks?{}".format(
        "&".join(
            "{}={}".format(quote(name, safe=""), quote(value, safe=""))
            for name, value in params
        )
    )


def task_detail_href(task: Mapping[str, Any], filters: Mapping[str, Any]) -> str:
    task_ref = str(task.get("ref") or task.get("id") or "")
    params: list[tuple[str, str]] = []
    for name in ("view", "initiative", "epic", "status", "q", "group"):
        value = str(filters.get(name) or "")
        if value:
            params.append((name, value))
    if filters.get("show_done"):
        params.append(("show_done", "1"))
    if task_ref:
        params.append(("task", task_ref))
    query = "&".join(
        "{}={}".format(quote(name, safe=""), quote(value, safe=""))
        for name, value in params
    )
    return "/tasks{}#task-details-drawer".format("?{}".format(query) if query else "")


def task_detail_link(
    task: Mapping[str, Any],
    filters: Mapping[str, Any] | None = None,
    *,
    label: str = "Details",
) -> str:
    task_ref = str(task.get("ref") or task.get("id") or "")
    if not task_ref:
        return '<span class="pill">Details unavailable</span>'
    href = task_detail_href(task, filters or {})
    return '<a class="button-link secondary task-detail-link" href="{}">{}</a>'.format(
        escape(href),
        escape(label),
    )


def task_detail_drawer(
    task: Mapping[str, Any],
    data: Mapping[str, Any],
    filters: Mapping[str, Any],
) -> str:
    if not task:
        return (
            '<aside class="drawer task-detail-drawer" id="task-details-drawer" '
            'aria-label="Task details drawer">'
            '<div class="task-drawer-header">'
            "<div><h2>Task Details</h2>"
            '<p class="muted">Select Details on a task row to inspect it here.</p></div>'
            '<span class="pill">No task selected</span>'
            "</div>"
            '<p class="empty">No task is selected.</p>'
            '<a class="button-link secondary" href="{}">Open Full Inventory</a>'
            "</aside>"
        ).format(escape(task_inventory_href(filters)))
    task_ref = str(task.get("ref") or task.get("id") or "Task")
    legacy = str(task.get("legacy_id") or task.get("id") or "")
    legacy_html = (
        '<code>{}</code>'.format(escape(legacy))
        if legacy and legacy != task_ref
        else ""
    )
    return (
        '<aside class="drawer task-detail-drawer" id="task-details-drawer" '
        'aria-label="Task details drawer">'
        '<div class="task-drawer-header">'
        "<div><h2>Task Details</h2>"
        '<p class="muted">Selected task inspection stays outside the table rows.</p></div>'
        "{}"
        "</div>"
        '<div class="task-drawer-title">'
        "{}<strong>{}</strong>{}<span>{}</span>"
        "</div>"
        '<div class="task-detail-body task-drawer-body">{}</div>'
        "</aside>"
    ).format(
        status_badge(str(task.get("status") or "unknown")),
        status_badge(str(task.get("status") or "unknown")),
        escape(task_ref),
        legacy_html,
        escape(task.get("title") or ""),
        task_detail_body(task, data),
    )


def task_action_queue(
    tasks: Sequence[Mapping[str, Any]],
    data: Mapping[str, Any],
    filters: Mapping[str, Any],
) -> str:
    groups = task_action_queue_groups(tasks, data)
    return "".join(
        task_action_queue_group(
            key,
            title,
            description,
            groups.get(key, []),
            data,
            filters,
        )
        for key, title, description in TASK_QUEUE_GROUPS
    )


def task_action_queue_groups(
    tasks: Sequence[Mapping[str, Any]],
    data: Mapping[str, Any],
) -> dict[str, list[Mapping[str, Any]]]:
    groups: dict[str, list[Mapping[str, Any]]] = {
        key: [] for key, _, _ in TASK_QUEUE_GROUPS
    }
    for task in tasks:
        category = task_action_queue_category(task, data)
        groups.setdefault(category, []).append(task)
    return groups


def task_action_queue_group(
    key: str,
    title: str,
    description: str,
    tasks: Sequence[Mapping[str, Any]],
    data: Mapping[str, Any],
    filters: Mapping[str, Any],
) -> str:
    return (
        '<details class="task-group task-action-group task-action-group-{}" open>'
        "<summary><strong>{}</strong><span>{} task{}</span></summary>"
        '<p class="muted task-action-group-note">{}</p>'
        "{}"
        "</details>"
    ).format(
        escape(css_token(key)),
        escape(title),
        escape(len(tasks)),
        "" if len(tasks) == 1 else "s",
        escape(description),
        task_action_queue_table(
            tasks,
            data,
            filters,
            category=key,
            empty_text="No {} tasks match the filters.".format(
                title.lower().replace(" ", "-")
            ),
        ),
    )


def task_action_queue_table(
    tasks: Sequence[Mapping[str, Any]],
    data: Mapping[str, Any],
    filters: Mapping[str, Any],
    *,
    category: str,
    empty_text: str,
) -> str:
    rows = []
    for task in tasks:
        cells = [
            task_identity_cell(task),
            status_badge(str(task.get("status") or "unknown")),
            escape(task.get("title", "")),
            escape(task_action_queue_next_text(task, category)),
            task_action_queue_primary_control(task, data, category, filters),
            task_detail_link(task, filters),
        ]
        rows.append(
            "<tr>{}</tr>".format(
                "".join("<td>{}</td>".format(cell) for cell in cells)
            )
        )
    return table(("Task", "Status", "Title", "Next", "Primary Action", "Details"), rows, empty_text)


def task_action_queue_category(
    task: Mapping[str, Any],
    data: Mapping[str, Any],
) -> str:
    status = str(task.get("status") or "unknown")
    action = task_primary_available_action(task)
    if task_has_structural_blocker(task):
        return "blocked"
    if task_is_current(task, data) or status == "in_progress":
        return "current"
    if task_action_is_decision(action):
        return "needs_decision"
    if task_action_is_run(action):
        return "ready_to_run"
    return "other_active"


def task_is_current(task: Mapping[str, Any], data: Mapping[str, Any]) -> bool:
    current = _mapping(data.get("current_task"))
    if not current:
        return False
    task_refs = set(task_ref_values(task))
    current_refs = set(task_ref_values(current))
    return bool(task_refs and current_refs and task_refs.intersection(current_refs))


def task_primary_available_action(task: Mapping[str, Any]) -> Mapping[str, Any]:
    hints = _mapping(task.get("pipeline_hints"))
    actions = [
        dict(action)
        for action in hints.get("actions") or []
        if isinstance(action, Mapping) and bool(action.get("available"))
    ]
    next_actions = _string_items(hints.get("next_actions"))
    for label in next_actions:
        for action in actions:
            if str(action.get("label") or "") == label:
                return action
    return actions[0] if actions else {}


def task_action_is_decision(action: Mapping[str, Any]) -> bool:
    return task_action_matches(
        action,
        labels=TASK_QUEUE_DECISION_ACTIONS,
        action_ids=TASK_QUEUE_DECISION_ACTION_IDS,
    )


def task_action_is_run(action: Mapping[str, Any]) -> bool:
    return task_action_matches(
        action,
        labels=TASK_QUEUE_RUN_ACTIONS,
        action_ids=TASK_QUEUE_RUN_ACTION_IDS,
        action_prefixes=TASK_QUEUE_RUN_ACTION_PREFIXES,
    )


def task_action_matches(
    action: Mapping[str, Any],
    *,
    labels: set[str],
    action_ids: set[str],
    action_prefixes: Sequence[str] = (),
) -> bool:
    label = str(action.get("label") or "")
    action_id = str(action.get("action") or "")
    return (
        label in labels
        or action_id in action_ids
        or any(action_id.startswith(prefix) for prefix in action_prefixes)
    )


def task_has_structural_blocker(task: Mapping[str, Any]) -> bool:
    hints = _mapping(task.get("pipeline_hints"))
    dependencies = _mapping(hints.get("dependencies"))
    latest_report = _mapping(task.get("latest_report"))
    if str(task.get("status") or "") == "blocked":
        return True
    if task_queue_first_text(
        task.get("blocked_reason"),
        task.get("blocker_reason"),
        task.get("reason"),
        task.get("blockers"),
        task.get("blocked_reasons"),
        latest_report.get("blockers"),
        dependencies.get("blocking"),
    ):
        return True
    return bool(dependencies.get("blocked"))


def task_structural_blocker_reason(task: Mapping[str, Any]) -> str:
    hints = _mapping(task.get("pipeline_hints"))
    dependencies = _mapping(hints.get("dependencies"))
    latest_report = _mapping(task.get("latest_report"))
    reason = task_queue_first_text(
        task.get("blocked_reason"),
        task.get("blocker_reason"),
        task.get("reason"),
        task.get("blockers"),
        task.get("blocked_reasons"),
        latest_report.get("blockers"),
        dependencies.get("blocking"),
    )
    if reason:
        return reason
    if str(task.get("status") or "") == "blocked":
        return "task status is blocked"
    return ""


def task_action_queue_next_text(task: Mapping[str, Any], category: str) -> str:
    status = str(task.get("status") or "unknown")
    action = task_primary_available_action(task)
    action_label = str(action.get("label") or "")
    if category == "blocked":
        return "Blocked; inspect details."
    if category == "ready_to_run":
        return action_label or "Ready to run"
    if category == "needs_decision":
        return action_label or "Review decision needed"
    if category == "current":
        return task_queue_first_next_action(task) or "Current task is {}".format(status)
    if status == "planned":
        return "Planned; not runnable yet."
    if status == "deferred":
        return "Deferred; no action by default."
    if status in TASK_QUEUE_DONE_STATUSES:
        return "{}; no action required.".format(status.replace("_", " ").title())
    return task_queue_first_next_action(task) or action_label or "No direct owner action."


def task_queue_first_next_action(task: Mapping[str, Any]) -> str:
    hints = _mapping(task.get("pipeline_hints"))
    return task_queue_first_text(hints.get("next_actions"))


def task_action_queue_primary_control(
    task: Mapping[str, Any],
    data: Mapping[str, Any],
    category: str,
    filters: Mapping[str, Any] | None = None,
) -> str:
    control = task_primary_action_control(
        task,
        data,
        category=category,
        filters=filters or {},
    )
    if not control:
        return '<span class="pill">No primary action</span>'
    return '<div class="row-actions row-primary-actions">{}</div>'.format(control)


def task_primary_action_control(
    task: Mapping[str, Any],
    data: Mapping[str, Any],
    *,
    category: str,
    filters: Mapping[str, Any] | None = None,
) -> str:
    task_ref = str(task.get("ref") or task.get("id") or "")
    if not task_ref:
        return '<span class="pill">Open Details</span>'
    filters = filters or {}
    session_control = task_primary_session_control(task, data, category=category)
    if session_control:
        return session_control
    action = task_primary_available_action(task)
    action_id = str(action.get("action") or "")
    if not action_id:
        return task_detail_link(task, filters, label="Open Details")
    if action_id == "ui.run_selected_task":
        return task_row_start_control(task, data)
    if action_id in TASK_PRIMARY_TASK_ACTION_LABELS:
        return task_primary_task_action_form(task, data, action_id)
    if action_id in TASK_PRIMARY_CHANGE_ACTION_LABELS:
        return task_primary_change_action_control(task, data, action_id, filters)
    if action_id.startswith("pipeline."):
        return task_primary_pipeline_action_control(task, data, action_id, filters)
    if action_id.startswith("evolution."):
        return task_primary_change_link(task, data, filters)
    return task_detail_link(task, filters, label="Open Details")


def task_primary_session_control(
    task: Mapping[str, Any],
    data: Mapping[str, Any],
    *,
    category: str,
) -> str:
    if category != "current":
        return ""
    session = task_row_pipeline_session(task, data)
    session_id = str(session.get("id") or "")
    status = str(session.get("status") or "")
    if not session_id:
        return ""
    if status in PIPELINE_RESUMABLE_STATUSES:
        return task_row_session_control(
            task,
            session_id,
            label="Resume",
            guidance=pipeline_session_action_guidance(session),
        )
    if status in PIPELINE_RUNNABLE_STATUSES:
        return task_row_session_control(
            task,
            session_id,
            label="Continue",
            guidance=pipeline_session_action_guidance(session),
        )
    return ""


def task_primary_task_action_form(
    task: Mapping[str, Any],
    data: Mapping[str, Any],
    action_id: str,
) -> str:
    if action_id in {"task.close_reviewed", "task.request_changes"}:
        spec = {
            "action": action_id,
            "label": TASK_PRIMARY_TASK_ACTION_LABELS[action_id],
            **TASK_PRIMARY_NOTE_SPECS[action_id],
        }
        return task_row_action(task, data, spec)
    task_ref = str(task.get("ref") or task.get("id") or "")
    if not task_ref:
        return ""
    return action_form(
        action_id,
        [hidden_field("task", task_ref)],
        button_label=TASK_PRIMARY_TASK_ACTION_LABELS.get(action_id, action_id),
    )


def task_primary_change_action_control(
    task: Mapping[str, Any],
    data: Mapping[str, Any],
    action_id: str,
    filters: Mapping[str, Any],
) -> str:
    change = task_primary_change_for_action(task, data, action_id)
    if not change:
        return task_primary_change_link(task, data, filters)
    spec = {
        "action": action_id,
        "label": TASK_PRIMARY_CHANGE_ACTION_LABELS[action_id],
        **TASK_PRIMARY_NOTE_SPECS[action_id],
    }
    return change_row_action(change, data, spec)


def task_primary_change_for_action(
    task: Mapping[str, Any],
    data: Mapping[str, Any],
    action_id: str,
) -> Mapping[str, Any]:
    for change in linked_changes_for_task(task, data):
        if entity_action_available(change, action_id) is True:
            return change
    target_statuses = {
        "evolution.approve_change": {"ready"},
        "evolution.accept_change": {"approved", "in_review"},
    }.get(action_id, set())
    if not target_statuses:
        return {}
    for change in task_linked_change_summaries(task):
        if str(change.get("status") or "") in target_statuses:
            return change
    return {}


def task_linked_change_summaries(task: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    hints = _mapping(task.get("pipeline_hints"))
    return [
        change
        for change in hints.get("linked_changes") or []
        if isinstance(change, Mapping)
    ]


def task_primary_change_link(
    task: Mapping[str, Any],
    data: Mapping[str, Any],
    filters: Mapping[str, Any],
) -> str:
    linked = linked_changes_for_task(task, data) or task_linked_change_summaries(task)
    target = str(
        (linked[0].get("id") if linked and isinstance(linked[0], Mapping) else "")
        or task.get("ref")
        or task.get("id")
        or ""
    )
    if not target:
        return task_detail_link(task, filters, label="Open Details")
    return '<a class="button-link" href="/evolution?q={}">Open Change</a>'.format(
        escape(quote(target, safe="")),
    )


def task_primary_pipeline_action_control(
    task: Mapping[str, Any],
    data: Mapping[str, Any],
    action_id: str,
    filters: Mapping[str, Any],
) -> str:
    if action_id == "pipeline.run_next":
        session = task_row_pipeline_session(task, data)
        session_id = str(session.get("id") or "")
        if session_id:
            return task_row_session_control(
                task,
                session_id,
                label="Resume",
                guidance=pipeline_session_action_guidance(session),
            )
    return task_detail_link(task, filters, label="Open Details")


def task_queue_first_text(*values: Any) -> str:
    for value in values:
        if isinstance(value, str):
            text = value.strip()
            if text:
                return text
            continue
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            for item in value:
                text = str(item or "").strip()
                if text:
                    return text
            continue
        text = str(value or "").strip()
        if text:
            return text
    return ""


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
            filters=filters,
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
                    filters=filters,
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


def owner_cockpit_summary(data: Mapping[str, Any]) -> str:
    queue = _mapping(data.get("owner_action_queue"))
    counts = _mapping(queue.get("counts"))
    current = _mapping(data.get("current_task"))
    current_ref = str(
        current.get("ref")
        or current.get("id")
        or ""
    )
    return (
        '<section class="summary-grid cockpit-summary" aria-label="Owner cockpit summary">'
        "{}{}{}{}{}"
        "</section>"
    ).format(
        cockpit_metric(
            "Needs Decision",
            str(counts.get("needs_decision", 0)),
            "#owner-queue-needs-decision",
            "Review decisions waiting",
        ),
        cockpit_metric(
            "Current",
            str(counts.get("current", 0)),
            "#owner-queue-current",
            current_ref or "No selected task",
        ),
        cockpit_metric(
            "Ready To Run",
            str(counts.get("ready_to_run", 0)),
            "#owner-queue-ready-to-run",
            "Runnable queue",
        ),
        cockpit_metric(
            "Blocked",
            str(counts.get("blocked", 0)),
            "#owner-queue-blocked",
            "Needs unblock",
        ),
        cockpit_metric(
            "Health",
            owner_health_metric_value(data),
            "#owner-health",
            "Compact checks",
        ),
    )


def cockpit_metric(label: str, value: str, href: str, detail: str) -> str:
    return (
        '<a class="metric cockpit-metric" href="{}">'
        "<span>{}</span><strong>{}</strong><small>{}</small>"
        "</a>"
    ).format(
        escape(href),
        escape(label),
        escape(value),
        escape(detail),
    )


def owner_health_metric_value(data: Mapping[str, Any]) -> str:
    counts = health_summary_counts(project_health_items(data))
    if counts.get("FAIL"):
        return "{} fail".format(counts.get("FAIL"))
    if counts.get("WARN"):
        return "{} warn".format(counts.get("WARN"))
    if counts.get("UNKNOWN"):
        return "{} unknown".format(counts.get("UNKNOWN"))
    return "OK"


def current_execution_details_panel(data: Mapping[str, Any]) -> str:
    return (
        '<section class="panel execution-panel cockpit-detail-panel">'
        '<details class="cockpit-detail">'
        '<summary><span>Current Execution Details</span><span class="pill">Prompt, context, copy text</span></summary>'
        "{}"
        "{}"
        '<p class="muted detail-links"><a href="/generated">Open generated files</a> · '
        '<a href="/tasks">Open Tasks</a> · <a href="/pipeline">Open Pipeline</a></p>'
        "</details>"
        "</section>"
    ).format(
        execution_status_panel(data, show_actions=False),
        current_execution_detail_actions(data),
    )


def current_execution_detail_actions(data: Mapping[str, Any]) -> str:
    context = _mapping(data.get("execution_context"))
    current = _mapping(context.get("current_task") or data.get("current_task"))
    if not current:
        return ""
    return '<div class="cockpit-detail-actions">{}</div>'.format(
        action_form("current.clear", [], button_label="Clear Current")
    )


def owner_queue_section(
    data: Mapping[str, Any],
    key: str,
    title: str,
    description: str,
    empty_text: str,
    *,
    limit: int,
) -> str:
    items = owner_queue_items(data, key)
    section_id = "owner-queue-{}".format(css_token(key))
    count = len(items)
    return (
        '<section class="panel owner-queue-section owner-queue-{}" id="{}">'
        '<div class="owner-section-header">'
        "<div><h2>{}</h2><p>{}</p></div>"
        '<span class="pill">{} item{}</span>'
        "</div>"
        "{}"
        "</section>"
    ).format(
        escape(css_token(key)),
        escape(section_id),
        escape(title),
        escape(description),
        escape(count),
        "" if count == 1 else "s",
        owner_queue_cards(
            items,
            empty_text=empty_text,
            limit=limit,
            more_href=owner_queue_more_href(key),
        ),
    )


def owner_queue_items(data: Mapping[str, Any], key: str) -> list[Mapping[str, Any]]:
    queue = _mapping(data.get("owner_action_queue"))
    return [
        item
        for item in queue.get(key) or []
        if isinstance(item, Mapping)
    ]


def owner_queue_cards(
    items: Sequence[Mapping[str, Any]],
    *,
    empty_text: str,
    limit: int,
    more_href: str,
) -> str:
    if not items:
        return '<p class="empty">{}</p>'.format(escape(empty_text))
    visible = list(items[:limit])
    cards = "".join(owner_queue_card(item) for item in visible)
    remainder = len(items) - len(visible)
    if remainder > 0:
        cards += (
            '<div class="queue-card owner-action-card owner-action-more">'
            "<h3>+{} more</h3>"
            '<p class="muted">Open the detailed page to inspect the remaining queue items.</p>'
            '<div class="owner-card-action"><a class="button-link secondary" href="{}">Open details</a></div>'
            "</div>"
        ).format(escape(remainder), escape(more_href))
    return '<div class="owner-queue-grid">{}</div>'.format(cards)


def owner_queue_card(item: Mapping[str, Any]) -> str:
    next_action = str(item.get("primary_next_action") or item.get("next_action") or "")
    detail = owner_queue_item_detail(item)
    return (
        '<article class="queue-card owner-action-card owner-action-{}">'
        '<div class="owner-action-card-header">'
        '<span class="pill">{}</span>{}'
        "</div>"
        "<h3><code>{}</code>{}</h3>"
        "{}{}"
        '<div class="owner-card-action">{}</div>'
        "</article>"
    ).format(
        escape(css_token(str(item.get("category") or item.get("kind") or "item"))),
        escape(owner_kind_label(item)),
        status_badge(str(item.get("status") or "unknown")),
        escape(item.get("ref") or item.get("id") or ""),
        " {}".format(escape(item.get("title") or "")) if item.get("title") else "",
        (
            '<p class="owner-next">Next: <strong>{}</strong></p>'.format(
                escape(next_action)
            )
            if next_action
            else '<p class="owner-next muted">No direct action available.</p>'
        ),
        '<p class="owner-detail">{}</p>'.format(escape(detail)) if detail else "",
        owner_queue_primary_control(item),
    )


def owner_queue_item_detail(item: Mapping[str, Any]) -> str:
    blocker = str(item.get("blocker_reason") or "").strip()
    if blocker:
        return blocker
    linked = _string_items(item.get("linked_tasks"))
    if linked:
        return "Linked task(s): {}".format(", ".join(linked[:3]))
    updated = str(item.get("updated_at") or "").strip()
    if updated:
        return "Updated {}".format(updated)
    return ""


def owner_kind_label(item: Mapping[str, Any]) -> str:
    kind = str(item.get("kind") or "item").replace("_", " ").strip()
    return kind.title() if kind else "Item"


def owner_queue_primary_control(item: Mapping[str, Any]) -> str:
    href = owner_queue_item_href(item)
    label = owner_queue_control_label(item)
    return '<a class="button-link" href="{}">{}</a>'.format(
        escape(href),
        escape(label),
    )


def owner_queue_item_href(item: Mapping[str, Any]) -> str:
    kind = str(item.get("kind") or "")
    ref = str(item.get("ref") or item.get("id") or "")
    action = str(item.get("action") or "")
    category = str(item.get("category") or "")
    if kind == "pipeline_session":
        return (
            "/pipeline/sessions/{}".format(quote(ref, safe=""))
            if ref
            else "/pipeline"
        )
    if kind == "pipeline":
        return "/pipeline"
    if kind == "change" or action.startswith("evolution."):
        return "/evolution?q={}".format(quote(ref, safe="")) if ref else "/evolution"
    if action == "task.close_reviewed" or category == "needs_decision":
        return "/reviews?task={}".format(quote(ref, safe="")) if ref else "/reviews"
    if kind == "task":
        return "/tasks?q={}".format(quote(ref, safe="")) if ref else "/tasks"
    return "/actions"


def owner_queue_control_label(item: Mapping[str, Any]) -> str:
    kind = str(item.get("kind") or "")
    category = str(item.get("category") or "")
    action = str(item.get("action") or "")
    if kind == "pipeline_session":
        return "Open Session"
    if kind == "pipeline":
        return "Open Pipeline"
    if action == "task.close_reviewed":
        return "Open Review"
    if kind == "change" or action.startswith("evolution."):
        return "Open Change"
    if category == "blocked":
        return "Open Details"
    if category == "current":
        return "Open Current"
    return "Open Task"


def owner_queue_more_href(key: str) -> str:
    if key == "needs_decision":
        return "/evolution"
    if key == "blocked":
        return "/tasks?status=blocked"
    if key == "ready_to_run":
        return "/tasks?status=ready"
    if key == "current":
        return "/tasks"
    return "/tasks"


def owner_recent_signals_panel(data: Mapping[str, Any]) -> str:
    items = owner_queue_items(data, "watch_only")
    if not items:
        return (
            '<section class="panel owner-signals">'
            "<h2>Recent Signals</h2>"
            '<p class="empty">No watch-only signals need attention.</p>'
            "</section>"
        )
    return (
        '<section class="panel owner-signals">'
        '<details class="cockpit-detail">'
        '<summary><span>Recent Signals</span><span class="pill">{} watch-only</span></summary>'
        "{}"
        "</details>"
        "</section>"
    ).format(
        escape(len(items)),
        owner_queue_cards(
            items,
            empty_text="No watch-only signals.",
            limit=6,
            more_href="/tasks",
        ),
    )


def current_execution_bar(
    data: Mapping[str, Any],
    *,
    selected_task: Mapping[str, Any] | None = None,
) -> str:
    context = _mapping(data.get("execution_context"))
    current = _mapping(context.get("current_task") or data.get("current_task"))
    prompt = _mapping(context.get("prompt"))
    pack = _mapping(context.get("context_pack"))
    selected_warning = _selected_task_warning(current, selected_task or {})

    if not current:
        return (
            '<section class="current-execution-bar no-current" aria-label="Current execution">'
            '<div class="current-execution-main">'
            '<span class="current-execution-kicker">Current Execution</span>'
            '<div class="current-execution-title">'
            "<strong>No current task</strong>"
            "{}"
            "</div>"
            '<div class="current-execution-next">Next owner action: '
            "<span>Select a task to prepare or execute.</span></div>"
            "{}"
            "</div>"
            '<div class="current-execution-actions">'
            '<a class="button-link secondary" href="/tasks">Open Tasks</a>'
            "</div>"
            "</section>"
        ).format(status_badge("none"), current_execution_warning(selected_warning))

    return (
        '<section class="current-execution-bar" aria-label="Current execution">'
        "{}{}{}"
        "</section>"
    ).format(
        current_execution_bar_summary(current, selected_warning=selected_warning),
        current_execution_readiness(prompt, pack),
        current_execution_quick_actions(current),
    )


def current_execution_bar_summary(
    current: Mapping[str, Any],
    *,
    selected_warning: str = "",
) -> str:
    task_ref = str(current.get("ref") or current.get("id") or "")
    internal_id = str(current.get("id") or current.get("legacy_id") or "")
    title = str(current.get("title") or "")
    next_action = current_execution_next_action(current)
    id_detail = ""
    if internal_id and internal_id != task_ref:
        id_detail = "<code>{}</code>".format(escape(internal_id))
    return (
        '<div class="current-execution-main">'
        '<span class="current-execution-kicker">Current Execution</span>'
        '<div class="current-execution-title">{}<strong>{}</strong>{}<span>{}</span></div>'
        '<div class="current-execution-next">Next owner action: <span>{}</span></div>'
        "{}"
        "</div>"
    ).format(
        status_badge(str(current.get("status") or "unknown")),
        escape(task_label(current)),
        id_detail,
        escape(title),
        escape(next_action),
        current_execution_warning(selected_warning),
    )


def current_execution_warning(message: str) -> str:
    if not message:
        return ""
    return '<p class="current-execution-warning">{}</p>'.format(escape(message))


def current_execution_next_action(current: Mapping[str, Any]) -> str:
    hints = _mapping(current.get("pipeline_hints"))
    next_actions = _string_items(hints.get("next_actions"))
    if next_actions:
        return ", ".join(next_actions)
    blockers = _string_items(hints.get("blocked_reasons"))
    if blockers:
        return "Blocked: {}".format(blockers[0])
    return "No owner action available."


def current_execution_readiness(
    prompt: Mapping[str, Any],
    pack: Mapping[str, Any],
) -> str:
    return '<div class="current-execution-signals">{}{}</div>'.format(
        current_execution_signal(
            "Codex Prompt",
            str(prompt.get("status") or "unknown"),
            str(prompt.get("code") or prompt.get("raw_status") or prompt.get("path") or ""),
        ),
        current_execution_signal(
            "Context Pack",
            str(pack.get("status") or "unknown"),
            _revision_detail(pack),
        ),
    )


def current_execution_signal(label: str, status: str, detail: str) -> str:
    return (
        '<div class="current-execution-signal">'
        "<span>{}</span>{}<code>{}</code>"
        "</div>"
    ).format(
        escape(label),
        status_badge(status),
        escape(detail or "not reported"),
    )


def current_execution_quick_actions(current: Mapping[str, Any]) -> str:
    task_ref = str(current.get("ref") or current.get("id") or "")
    if not task_ref:
        return (
            '<div class="current-execution-actions">'
            '<a class="button-link secondary" href="/tasks">Open Tasks</a>'
            "</div>"
        )
    href, label = current_execution_primary_target(current, task_ref)
    return (
        '<div class="current-execution-actions">'
        '<a class="button-link" href="{}">{}</a>'
        "</div>"
    ).format(
        escape(href),
        escape(label),
    )


def current_execution_primary_target(
    current: Mapping[str, Any],
    task_ref: str,
) -> tuple[str, str]:
    next_action = current_execution_next_action(current).lower()
    quoted = quote(task_ref, safe="")
    if "approve" in next_action or "review" in next_action:
        return "/reviews?task={}".format(quoted), "Open Review"
    if "change" in next_action:
        return "/evolution?q={}".format(quoted), "Open Change"
    return "/tasks?q={}".format(quoted), "Open Task"


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
    filters: Mapping[str, Any] | None = None,
) -> str:
    rows = []
    for task in tasks:
        cells = [
            task_identity_cell(task),
            status_badge(str(task.get("status") or "unknown")),
            escape(task.get("epic_key") or task.get("epic_id") or ""),
            escape(task.get("title", "")),
            task_compact_next_cell(task),
            task_detail_link(task, filters or {}),
        ]
        if include_actions:
            cells.append(task_row_actions(task, data or {}, filters=filters or {}))
        rows.append(
            "<tr>{}</tr>".format(
                "".join("<td>{}</td>".format(cell) for cell in cells)
            )
        )
    headers = ["Task", "Status", "Epic", "Title", "Next / Blocker", "Details"]
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


def task_compact_next_cell(task: Mapping[str, Any]) -> str:
    next_action = task_queue_first_next_action(task)
    if next_action:
        return '<span class="compact-next"><strong>Next:</strong> {}</span>'.format(
            escape(next_action)
        )
    blocker = task_first_blocker_reason(task)
    if blocker:
        return '<span class="compact-next compact-blocker"><strong>Blocked:</strong> {}</span>'.format(
            escape(blocker)
        )
    return '<span class="muted">No direct owner action.</span>'


def task_detail_panel(
    task: Mapping[str, Any],
    data: Mapping[str, Any],
    *,
    open_panel: bool = False,
    summary_label: str = "Details",
) -> str:
    open_attr = " open" if open_panel else ""
    task_ref = str(task.get("ref") or task.get("id") or "Task")
    return (
        '<details class="task-detail-panel"{}>'
        '<summary><span>{}</span><span class="pill">{}</span></summary>'
        '<div class="task-detail-body">'
        "{}"
        "</div>"
        "</details>"
    ).format(
        open_attr,
        escape(summary_label),
        escape(task_ref),
        task_detail_body(task, data),
    )


def task_detail_body(task: Mapping[str, Any], data: Mapping[str, Any]) -> str:
    return "{}{}{}{}{}{}{}{}".format(
        task_detail_context(task),
        task_detail_blockers(task),
        task_detail_linked_change(task, data),
        task_detail_action_table(task),
        task_detail_policy(data),
        task_detail_generated_files(task, data),
        task_detail_health(data, task),
        task_detail_recent_events(task, data),
    )


def task_detail_context(task: Mapping[str, Any]) -> str:
    rows = [
        review_field("Summary", escape(task.get("summary") or task.get("description") or "")),
        review_field("Stage", escape(task.get("active_stage") or "not recorded")),
        review_field("Description", escape(task.get("description") or "No description recorded.")),
        review_field("Scope", text_list(task.get("scope"), empty_text="No scope recorded.")),
        review_field(
            "Acceptance",
            text_list(task.get("acceptance_criteria"), empty_text="No acceptance criteria recorded."),
        ),
    ]
    return (
        '<section class="task-detail-section">'
        "<h4>Task</h4>"
        '<div class="review-grid">{}</div>'
        "</section>"
    ).format("".join(rows))


def task_detail_blockers(task: Mapping[str, Any]) -> str:
    blockers = task_blocker_reasons(task)
    return (
        '<section class="task-detail-section">'
        "<h4>Blockers</h4>"
        "{}"
        "</section>"
    ).format(
        text_list(blockers, empty_text="No blockers recorded.")
    )


def task_detail_linked_change(task: Mapping[str, Any], data: Mapping[str, Any]) -> str:
    hints = _mapping(task.get("pipeline_hints"))
    rows: list[str] = []
    summary_bits: list[str] = []
    seen: set[str] = set()
    for change in [
        *[
            change
            for change in hints.get("linked_changes") or []
            if isinstance(change, Mapping)
        ],
        *linked_changes_for_task(task, data),
    ]:
        change_id = str(change.get("id") or "")
        key = change_id or str(change)
        if key in seen:
            continue
        seen.add(key)
        summary_bits.append(
            "{} {}".format(
                change_id or "unknown",
                str(change.get("status") or "unknown"),
            ).strip()
        )
        rows.append(
            "<tr><td><code>{}</code></td><td>{}</td><td>{}</td></tr>".format(
                escape(change_id or "unknown"),
                status_badge(str(change.get("status") or "unknown")),
                escape(change.get("title") or ""),
            )
        )
    if not rows and hints.get("requires_evolution_change"):
        rows.append(
            '<tr><td colspan="3">Requires an approved linked Evolution Change.</td></tr>'
        )
    return (
        '<section class="task-detail-section">'
        "<h4>Linked Change</h4>"
        "{}"
        "{}"
        "</section>"
    ).format(
        (
            '<p class="hint-change"><strong>Linked Change:</strong> {}</p>'.format(
                escape(", ".join(summary_bits))
            )
            if summary_bits
            else ""
        ),
        table(("Change", "Status", "Title"), rows, "No linked Evolution Change."),
    )


def task_detail_policy(data: Mapping[str, Any]) -> str:
    summary = dashboard_effective_policy_summary(data)
    return (
        '<section class="task-detail-section">'
        "{}"
        "</section>"
    ).format(
        effective_policy_summary_panel(
            summary,
            title="Effective Run Policy",
            compact=True,
        ) or '<p class="empty">No effective policy summary available.</p>'
    )


def task_detail_generated_files(task: Mapping[str, Any], data: Mapping[str, Any]) -> str:
    rows = []
    file_count = 0
    for item in data.get("generated") or []:
        if not isinstance(item, Mapping):
            continue
        file_count += 1
        rows.append(
            "<tr><td><code>{}</code></td><td>{}</td><td>{}</td></tr>".format(
                escape(item.get("label") or item.get("name") or ""),
                "yes" if item.get("exists") else "no",
                escape(item.get("mtime") or ""),
            )
        )
    report_generated = _string_items(_mapping(task.get("latest_report")).get("generated_files"))
    if report_generated:
        file_count += len(report_generated)
        rows.append(
            '<tr><td colspan="3"><strong>Latest report:</strong> {}</td></tr>'.format(
                ", ".join("<code>{}</code>".format(escape(path)) for path in report_generated)
            )
        )
    return task_detail_diagnostic_section(
        "Generated Files",
        table(("File", "Exists", "Updated"), rows, "No generated file data available."),
        css_key="generated-files",
        summary_detail="{} file{}".format(file_count, "" if file_count == 1 else "s"),
    )


def task_detail_health(data: Mapping[str, Any], task: Mapping[str, Any]) -> str:
    rows = []
    items = project_health_items(data)
    for item in items:
        detail = str(item.get("message") or item.get("reason") or "")
        path = str(item.get("path") or "")
        if path:
            detail = "{}{}".format("{} ".format(detail) if detail else "", path).strip()
        rows.append(
            "<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                escape(item.get("label") or item.get("key") or ""),
                status_badge(health_summary_status(item.get("status"))),
                escape(detail),
            )
        )
    return task_detail_diagnostic_section(
        "Health",
        table(("Area", "Status", "Signal"), rows, "No health data available."),
        css_key="health",
        summary_detail="{} signal{}".format(len(items), "" if len(items) == 1 else "s"),
    )


def task_detail_recent_events(task: Mapping[str, Any], data: Mapping[str, Any]) -> str:
    events = task_recent_event_lines(task, data)
    return task_detail_diagnostic_section(
        "Recent Events",
        text_list(events, empty_text="No recent task events found in loaded audit data."),
        css_key="recent-events",
        summary_detail="{} event{}".format(len(events), "" if len(events) == 1 else "s"),
    )


def task_detail_diagnostic_section(
    title: str,
    content: str,
    *,
    css_key: str,
    summary_detail: str,
) -> str:
    return (
        '<details class="task-detail-section task-diagnostic-section task-diagnostic-{}">'
        '<summary><span>{}</span><span class="pill">{}</span></summary>'
        '<div class="task-diagnostic-body">{}</div>'
        "</details>"
    ).format(
        escape(css_token(css_key)),
        escape(title),
        escape(summary_detail),
        content,
    )


def task_blocker_reasons(task: Mapping[str, Any]) -> list[str]:
    hints = _mapping(task.get("pipeline_hints"))
    dependencies = _mapping(hints.get("dependencies"))
    latest_report = _mapping(task.get("latest_report"))
    values = [
        dependencies.get("blocking"),
        task.get("blockers"),
        task.get("blocked_reasons"),
        task.get("blocked_reason"),
        task.get("blocker_reason"),
        task.get("reason"),
        latest_report.get("blockers"),
    ]
    reasons: list[str] = []
    seen: set[str] = set()
    for value in values:
        if isinstance(value, str):
            candidates = [value]
        elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            candidates = [str(item or "") for item in value]
        else:
            candidates = []
        for candidate in candidates:
            text = candidate.strip()
            if text and text not in seen:
                reasons.append(text)
                seen.add(text)
    if not reasons and str(task.get("status") or "") == "blocked":
        reasons.append("task status is blocked")
    return reasons


def task_first_blocker_reason(task: Mapping[str, Any]) -> str:
    blockers = task_blocker_reasons(task)
    return blockers[0] if blockers else ""


def task_recent_event_lines(task: Mapping[str, Any], data: Mapping[str, Any]) -> list[str]:
    refs = set(task_ref_values(task))
    matches: list[str] = []
    fallback: list[str] = []
    for audit in data.get("events") or []:
        if not isinstance(audit, Mapping):
            continue
        domain = str(audit.get("domain") or "audit")
        for line in _string_items(audit.get("lines")):
            text = "{}: {}".format(domain, line)
            fallback.append(text)
            if refs and any(ref in line for ref in refs):
                matches.append(text)
    return matches[:8] or fallback[:5]


def task_detail_action_table(task: Mapping[str, Any]) -> str:
    hints = _mapping(task.get("pipeline_hints"))
    rows = []
    for action in hints.get("actions") or []:
        if not isinstance(action, Mapping):
            continue
        available = bool(action.get("available"))
        reason = str(action.get("reason") or "")
        rows.append(
            "<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                escape(action.get("label") or action.get("action") or ""),
                status_badge("available" if available else "unavailable"),
                escape(reason or ("Available now." if available else "No explanation recorded.")),
            )
        )
    return (
        '<section class="task-detail-section">'
        "<h4>Available Actions</h4>"
        "{}"
        "</section>"
    ).format(
        table(("Action", "Status", "Explanation"), rows, "No action hints recorded."),
    )


def task_row_actions(
    task: Mapping[str, Any],
    data: Mapping[str, Any],
    *,
    filters: Mapping[str, Any] | None = None,
) -> str:
    status = str(task.get("status") or "")
    if status in TASK_ROW_INACTIVE_STATUSES:
        return '<span class="pill">No row workflows</span>'
    category = task_action_queue_category(task, data)
    control = task_primary_action_control(
        task,
        data,
        category=category,
        filters=filters or {},
    )
    if not control:
        return '<span class="pill">No row workflows</span>'
    return '<div class="row-actions row-primary-actions">{}</div>'.format(control)


def task_row_run_control(task: Mapping[str, Any], data: Mapping[str, Any]) -> str:
    status = str(task.get("status") or "")
    if status in TASK_ROW_INACTIVE_STATUSES:
        return ""
    if status in TASK_ROW_RUN_STATUSES:
        return task_row_start_control(task, data)
    if status == "in_progress":
        return task_row_continue_control(task, data)
    return ""


def task_row_start_control(task: Mapping[str, Any], data: Mapping[str, Any]) -> str:
    task_ref = str(task.get("ref") or task.get("id") or "")
    if not task_ref:
        return ""
    policy_summary = dashboard_effective_policy_summary(data)
    return (
        '<details class="row-action row-action-run">'
        "<summary>Run</summary>"
        "{}{}"
        "</details>"
    ).format(
        task_row_change_guidance(task),
        action_form(
            "ui.run_selected_task",
            [
                hidden_field("task", task_ref),
                incomplete_run_warning_panel(
                    policy_summary,
                    compact=True,
                    include_confirmation=True,
                ),
                textarea_field(
                    "auto_close_note",
                    "Auto-close Owner Note",
                    rows=2,
                    placeholder="Required only when the selected policy auto-closes tasks.",
                ),
            ],
            button_label="Run",
            confirm_required_note_fields=(
                ("auto_close_note",)
                if policy_requires_auto_close_note(policy_summary)
                else ()
            ),
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


def _pipeline_log_tail_parts(path: str) -> tuple[str, str, str] | None:
    prefix = "/pipeline/sessions/"
    if not path.startswith(prefix):
        return None
    tail = path.removeprefix(prefix).strip("/")
    parts = tail.split("/")
    if len(parts) != 4 or parts[1] != "logs":
        return None
    stream = parts[3]
    if stream.endswith(".json"):
        stream = stream.removesuffix(".json")
    return unquote(parts[0]), unquote(parts[2]), unquote(stream)


def _pipeline_session_status_id(path: str) -> str | None:
    prefix = "/pipeline/sessions/"
    suffix = "/status.json"
    if not path.startswith(prefix) or not path.endswith(suffix):
        return None
    session_id = path[len(prefix) : -len(suffix)]
    return unquote(session_id.strip("/"))


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
    confirm_target: str = "",
    confirm_policy_summary: str = "",
    confirm_required_note_fields: Sequence[str] = (),
) -> str:
    confirm_required_attr = " required" if confirm_required else ""
    enctype_attr = ' enctype="multipart/form-data"' if multipart else ""
    modal_attrs = (
        action_form_confirm_attrs(
            action_id,
            button_label=button_label,
            target=confirm_target,
            policy_summary=confirm_policy_summary,
            required_note_fields=confirm_required_note_fields,
        )
        if confirm_required
        else ""
    )
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
    return '<form method="post" action="/actions"{}{}>{}</form>'.format(
        enctype_attr,
        modal_attrs,
        "".join(controls),
    )


def action_form_confirm_attrs(
    action_id: str,
    *,
    button_label: str | None = None,
    target: str = "",
    policy_summary: str = "",
    required_note_fields: Sequence[str] = (),
) -> str:
    attrs = [
        ' data-confirm-modal="action"',
        ' data-confirm-action-id="{}"'.format(escape(action_id)),
        ' data-confirm-action-label="{}"'.format(escape(button_label or action_id)),
    ]
    if target:
        attrs.append(' data-confirm-target="{}"'.format(escape(target)))
    if policy_summary:
        attrs.append(
            ' data-confirm-policy-summary="{}"'.format(escape(policy_summary))
        )
    if required_note_fields:
        attrs.append(
            ' data-confirm-required-note-fields="{}"'.format(
                escape(",".join(required_note_fields))
            )
        )
    return "".join(attrs)


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
