"""Server-Sent Events (SSE) endpoint for streaming real-time job progress."""

from __future__ import annotations

import asyncio
import json
import logging

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from app.api.deps import get_task_queue
from app.workers.task_queue import AsyncTaskQueue

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/{job_id}")
async def stream_job_events(
    job_id: str,
    request: Request,
    queue: AsyncTaskQueue = Depends(get_task_queue),
) -> StreamingResponse:
    """Stream real-time progress updates for a job via Server-Sent Events."""

    async def event_generator():
        try:
            async for update in queue.subscribe(job_id):
                if await request.is_disconnected():
                    break
                payload = json.dumps(update)
                yield f"data: {payload}\n\n"
        except asyncio.CancelledError:
            pass

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
