from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from queue import Queue
from typing import Any
from uuid import uuid4


class EventStore:
    """内存事件流，后续可以平滑替换为 SQLite 落盘。"""

    def __init__(self, max_events: int = 500) -> None:
        self.max_events = max_events
        self.events: list[dict[str, Any]] = []
        self.snapshots: list[dict[str, Any]] = []
        self.listeners: list[Queue] = []

    def append(self, event_type: str, payload: dict[str, Any] | None = None, meta: dict[str, Any] | None = None) -> dict[str, Any]:
        event = {
            "id": f"evt_{uuid4().hex}",
            "type": event_type,
            "payload": payload or {},
            "meta": meta or {},
            "createdAt": datetime.now(timezone.utc).isoformat(),
        }
        self.events.append(event)
        if len(self.events) > self.max_events:
            self.events.pop(0)
        for listener in list(self.listeners):
            listener.put(deepcopy(event))
        return event

    def add_snapshot(self, world: dict[str, Any]) -> None:
        # 快照先保留摘要，后续接 SQLite 时再保存完整 diff。
        self.snapshots.append({"tick": world["clock"]["tick"], "day": world["clock"]["day"], "hour": world["clock"]["hour"], "agents": len(world["agents"]), "at": datetime.now(timezone.utc).isoformat()})
        if len(self.snapshots) > 80:
            self.snapshots.pop(0)

    def subscribe(self) -> Queue:
        queue: Queue = Queue()
        self.listeners.append(queue)
        return queue

    def unsubscribe(self, queue: Queue) -> None:
        if queue in self.listeners:
            self.listeners.remove(queue)

    def list(self) -> list[dict[str, Any]]:
        return deepcopy(self.events)
