"""Async task queue and pub-sub manager for background jobs and SSE streaming."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, AsyncGenerator, Callable, Coroutine
from uuid import UUID

logger = logging.getLogger(__name__)


class AsyncTaskQueue:
    """In-memory async task manager supporting cancellation, progress tracking, and SSE pub/sub."""

    def __init__(self) -> None:
        self._tasks: dict[str, asyncio.Task[Any]] = {}
        self._progress: dict[str, dict[str, Any]] = {}
        self._subscribers: dict[str, list[asyncio.Queue[dict[str, Any]]]] = {}

    def submit(
        self,
        task_id: str | UUID,
        coro_fn: Callable[[], Coroutine[Any, Any, Any]],
    ) -> asyncio.Task[Any]:
        """Submit a background coroutine to run."""
        tid = str(task_id)
        if tid in self._tasks and not self._tasks[tid].done():
            logger.warning("Task %s is already running", tid)
            return self._tasks[tid]

        task = asyncio.create_task(coro_fn())
        self._tasks[tid] = task

        def on_done(t: asyncio.Task[Any]) -> None:
            if t.cancelled():
                logger.info("Task %s was cancelled", tid)
            elif t.exception():
                logger.error("Task %s failed with exception: %s", tid, t.exception())
            else:
                logger.info("Task %s completed successfully", tid)

        task.add_done_callback(on_done)
        return task

    async def update_progress(
        self,
        task_id: str | UUID,
        progress: float,
        speed: float = 0.0,
        status: str = "downloading",
        eta: str = "--:--",
        extra: dict[str, Any] | None = None,
    ) -> None:
        """Update job progress and publish event to all SSE subscribers."""
        tid = str(task_id)
        payload = {
            "task_id": tid,
            "progress": round(progress, 2),
            "speed": speed,
            "status": status,
            "eta": eta,
            **(extra or {}),
        }
        self._progress[tid] = payload

        # Broadcast to active SSE listeners
        if tid in self._subscribers:
            for q in list(self._subscribers[tid]):
                try:
                    q.put_nowait(payload)
                except asyncio.QueueFull:
                    pass

    def get_progress(self, task_id: str | UUID) -> dict[str, Any] | None:
        """Get latest cached progress state."""
        return self._progress.get(str(task_id))

    def cancel(self, task_id: str | UUID) -> bool:
        """Cancel an in-progress background task."""
        tid = str(task_id)
        task = self._tasks.get(tid)
        if task and not task.done():
            task.cancel()
            return True
        return False

    async def subscribe(self, task_id: str | UUID) -> AsyncGenerator[dict[str, Any], None]:
        """Subscribe to real-time events for a specific task as an async generator."""
        tid = str(task_id)
        q: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=100)

        if tid not in self._subscribers:
            self._subscribers[tid] = []
        self._subscribers[tid].append(q)

        # Send initial cached state if present
        if tid in self._progress:
            yield self._progress[tid]

        try:
            while True:
                data = await q.get()
                yield data
                if data.get("status") in ("completed", "failed", "cancelled"):
                    break
        finally:
            if tid in self._subscribers and q in self._subscribers[tid]:
                self._subscribers[tid].remove(q)
                if not self._subscribers[tid]:
                    del self._subscribers[tid]


# Global singleton instance
task_queue = AsyncTaskQueue()

