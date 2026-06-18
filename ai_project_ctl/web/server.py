"""Standard-library read-only HTTP server for the Web Control Center."""

from __future__ import annotations

import html
import ipaddress
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence
from urllib.parse import urlparse

from ai_project_ctl.core.result import CommandError
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
    """Run the local read-only Web Control Center until interrupted."""

    _require_loopback_host(host)
    model = ReadOnlyProjectModel(root, actor=actor)
    server = ThreadingHTTPServer((host, port), make_handler(model))
    url = "http://{}:{}".format(host, server.server_address[1])
    print("Read-only Web Control Center: {}".format(url))
    print("Root: {}".format(model.root))
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("")
    finally:
        server.server_close()


def make_handler(model: ReadOnlyProjectModel) -> type[BaseHTTPRequestHandler]:
    """Create a request handler bound to one read-only project model."""

    class ControlCenterHandler(BaseHTTPRequestHandler):
        server_version = "AIProjectControlCenter/0.1"

        def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
            self._handle_read(head_only=False)

        def do_HEAD(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
            self._handle_read(head_only=True)

        def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
            self._method_not_allowed()

        def do_PUT(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
            self._method_not_allowed()

        def do_PATCH(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
            self._method_not_allowed()

        def do_DELETE(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
            self._method_not_allowed()

        def log_message(self, format: str, *args: Any) -> None:
            return

        def _handle_read(self, *, head_only: bool) -> None:
            path = urlparse(self.path).path
            try:
                status, content_type, body = route(path, model)
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

        def _method_not_allowed(self) -> None:
            payload = (
                "Write actions are disabled in CTL-10. "
                "This local control center accepts GET and HEAD only.\n"
            ).encode("utf-8")
            self.send_response(HTTPStatus.METHOD_NOT_ALLOWED)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Allow", "GET, HEAD")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(payload)

    return ControlCenterHandler


def route(
    path: str,
    model: ReadOnlyProjectModel,
) -> tuple[HTTPStatus, str, str]:
    """Route one read-only request."""

    if path == "/healthz":
        return HTTPStatus.OK, "application/json; charset=utf-8", json.dumps(
            {"ok": True, "mode": "read-only"},
            indent=2,
            sort_keys=True,
        )
    if path == "/data.json":
        return HTTPStatus.OK, "application/json; charset=utf-8", json.dumps(
            model.dashboard(),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )

    pages: dict[str, Callable[[], str]] = {
        "/": lambda: render_dashboard(model.dashboard()),
        "/tasks": lambda: render_tasks(model.dashboard()),
        "/epics": lambda: render_epics(model.dashboard()),
        "/reviews": lambda: render_reviews(model.dashboard()),
        "/events": lambda: render_events(model.dashboard()),
        "/generated": lambda: render_generated(model.dashboard()),
        "/doctor": lambda: render_doctor(model.dashboard()),
        "/commands": lambda: render_commands(model),
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


def render_error(error: CommandError) -> str:
    body = (
        '<section class="panel"><h2>Read Error</h2>'
        "<p>{}</p><pre>{}</pre></section>"
    ).format(
        escape(error.message),
        escape(json.dumps(error.details, indent=2, sort_keys=True)),
    )
    return render_page("Read Error", body, active="")


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
