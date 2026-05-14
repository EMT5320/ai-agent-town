from __future__ import annotations

import json
import mimetypes
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from app.developer.developer_commands import apply_developer_command
from app.runtime.agent_runtime import AgentRuntime


class TownApplication:
    """应用外壳，隔离 HTTP 层和核心 Runtime。"""

    def __init__(self, provider_mode: str | None = None) -> None:
        self.runtime = AgentRuntime(provider_mode=provider_mode)

    def get_public_state(self) -> dict[str, Any]:
        return self.runtime.get_public_state()

    def get_game_state(self) -> dict[str, Any]:
        return self.runtime.get_game_state()

    def step_simulation(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.runtime.step(actor_id=(payload or {}).get("actorId", "developer"))

    def command(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        return apply_developer_command(self.runtime, payload or {})

    def player_action(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.runtime.handle_player_action(payload or {})


def create_town_app(provider_mode: str | None = None) -> TownApplication:
    """供测试和 HTTP 服务复用的应用工厂。"""
    return TownApplication(provider_mode=provider_mode)


def create_handler(app: TownApplication, project_root: Path):
    frontend_root = project_root / "frontend"

    class Handler(BaseHTTPRequestHandler):
        """轻量 HTTP 适配器，保持和前端一致的 REST/SSE API。"""

        def do_GET(self) -> None:  # noqa: N802 - http.server 约定方法名
            route = self.path.split("?", 1)[0]
            if route == "/api/state":
                return self.write_json(app.get_public_state())
            if route == "/api/world/state":
                return self.write_json(app.get_game_state())
            if route == "/api/model-config":
                return self.write_json(app.runtime.model_config.public_config())
            if route == "/api/events":
                return self.stream_events(app)
            return self.serve_static(frontend_root)

        def do_POST(self) -> None:  # noqa: N802 - http.server 约定方法名
            payload = self.read_json()
            route = self.path.split("?", 1)[0]
            if route == "/api/step":
                return self.write_json(app.step_simulation(payload))
            if route == "/api/player/action":
                try:
                    return self.write_json(app.player_action(payload))
                except ValueError as error:
                    return self.write_json({"ok": False, "error": str(error)}, HTTPStatus.BAD_REQUEST)
            if route == "/api/developer":
                return self.write_json(app.command(payload))
            return self.write_json({"error": "unknown endpoint"}, HTTPStatus.NOT_FOUND)

        def read_json(self) -> dict[str, Any]:
            length = int(self.headers.get("content-length", "0"))
            if length <= 0:
                return {}
            raw = self.rfile.read(length).decode("utf-8")
            return json.loads(raw) if raw else {}

        def write_json(self, data: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
            body = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("content-type", "application/json; charset=utf-8")
            self.send_header("content-length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def serve_static(self, root: Path) -> None:
            requested = "/index.html" if self.path == "/" else self.path.split("?", 1)[0]
            target = (root / requested.lstrip("/")).resolve()
            if not str(target).startswith(str(root.resolve())) or not target.exists():
                return self.write_json({"error": "file not found"}, HTTPStatus.NOT_FOUND)
            body = target.read_bytes()
            content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
            self.send_response(HTTPStatus.OK)
            self.send_header("content-type", f"{content_type}; charset=utf-8" if content_type.startswith("text/") or target.suffix == ".js" else content_type)
            self.send_header("content-length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def stream_events(self, app_ref: TownApplication) -> None:
            queue = app_ref.runtime.event_store.subscribe()
            self.send_response(HTTPStatus.OK)
            self.send_header("content-type", "text/event-stream; charset=utf-8")
            self.send_header("cache-control", "no-cache")
            self.end_headers()
            try:
                while True:
                    event = queue.get()
                    self.wfile.write(f"data: {json.dumps(event, ensure_ascii=False)}\n\n".encode("utf-8"))
                    self.wfile.flush()
            except Exception:
                app_ref.runtime.event_store.unsubscribe(queue)

        def log_message(self, format: str, *args: Any) -> None:
            # 开发期减少请求日志噪音，核心事件已进入 EventStore。
            if os.getenv("AGENT_TOWN_HTTP_LOG") == "1":
                super().log_message(format, *args)

    return Handler


def run_server(port: int = 8787) -> None:
    """启动本地开发服务器。"""
    project_root = Path(__file__).resolve().parents[2]
    app = create_town_app()
    server = ThreadingHTTPServer(("127.0.0.1", port), create_handler(app, project_root))
    print(f"AI Agent 小镇 Python 后端已启动：http://localhost:{port}")
    print(f"模型配置：provider={app.runtime.provider_mode}, config={app.runtime.model_config.config_path}, local={app.runtime.model_config.local_config_path.exists()}")
    server.serve_forever()


if __name__ == "__main__":
    run_server(int(os.getenv("PORT", "8787")))


