from __future__ import annotations

import heapq
import time
import traceback
from dataclasses import dataclass, field
from typing import Any, Callable, List


@dataclass(order=True)
class _Job:
    sort_key: int
    name: str = field(compare=False)
    fn: Callable[[], Any] = field(compare=False)
    priority: int = field(compare=False)
    submitted_at: float = field(compare=False, default_factory=time.perf_counter)


class QueueRunner:
    """
    Minimal priority queue:
      - Higher `priority` runs first (internally stored as negative).
      - `run(budget_s)` time-slices until budget is spent or queue is empty.
      - Each job runs to completion (coarse-grained time-slice).
    """

    def __init__(self) -> None:
        self._q: List[_Job] = []
        self.completed: List[str] = []
        self.failed: List[str] = []

    def submit(self, name: str, fn: Callable[[], Any], priority: int = 1) -> None:
        heapq.heappush(
            self._q, _Job(sort_key=-int(priority), name=name, fn=fn, priority=priority)
        )

    def run(self, budget_s: float = 30.0, sleep_between: float = 0.0) -> None:
        t0 = time.perf_counter()
        while self._q and (time.perf_counter() - t0) < budget_s:
            job = heapq.heappop(self._q)
            try:
                job.fn()
                print(f"[queue] ok: {job.name}")
                self.completed.append(job.name)
            except Exception:
                print(f"[queue] fail: {job.name}")
                traceback.print_exc()
                self.failed.append(job.name)
            if sleep_between > 0:
                time.sleep(sleep_between)


def demo_submit(runner: QueueRunner) -> None:
    """Example: schedule 'evaluation' jobs above 'exploration' jobs."""

    def eval_job():
        # put your evaluation call here, e.g. shadow replay or unit pipeline run
        pass

    def explore_job():
        # put your exploration/mutation call here
        pass

    runner.submit("eval:shadow@A", eval_job, priority=10)
    runner.submit("explore:mutate@1", explore_job, priority=1)

