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

import subprocess
import sys
from pathlib import Path


def submit_shadow_job(
    runner: QueueRunner,
    *,
    name: str,
    pipeline: str,
    input_path: str,
    out_path: str,
    baseline: str | None = None,
    limit: int = 1000,
    priority: int = 10,
    python_exe: str | None = None,
) -> None:
    """
    Submit a shadow_runner job:
      - pipeline: capability-backed pipeline YAML
      - input_path: sanitized transcripts JSONL
      - baseline: optional baseline metrics JSON for Δ and CI
      - out_path: destination metrics JSON
    """
    pipeline = str(Path(pipeline))
    input_path = str(Path(input_path))
    out_path = str(Path(out_path))
    baseline = str(Path(baseline)) if baseline else None

    def _job():
        exe = python_exe or sys.executable
        cmd = [
            exe,
            "tools/shadow_runner.py",
            "--pipeline",
            pipeline,
            "--input",
            input_path,
            "--out",
            out_path,
            "--limit",
            str(limit),
        ]
        if baseline:
            cmd.extend(["--baseline", baseline])
        print(f"[queue] run: {' '.join(cmd)}")
        subprocess.check_call(cmd)

    runner.submit(name, _job, priority=priority)


def submit_dual_shadow_jobs(
    runner: QueueRunner,
    *,
    pipeline: str,
    gold_input: str,
    fresh_input: str,
    gold_out: str = "baseline.shadow.metrics.json",
    fresh_out: str = "shadow.metrics.json",
    baseline_for_fresh: str | None = None,
    gold_limit: int = 10000,
    fresh_limit: int = 1000,
    gold_priority: int = 12,
    fresh_priority: int = 10,
    python_exe: str | None = None,
) -> None:
    """Enqueue gold (baseline) then fresh replays in priority order.

    Gold runs first at higher priority to generate/update the baseline. Fresh
    then runs with the baseline (either provided or the gold output path).
    """
    submit_shadow_job(
        runner,
        name="eval:shadow@gold",
        pipeline=pipeline,
        input_path=gold_input,
        out_path=gold_out,
        baseline=None,
        limit=gold_limit,
        priority=gold_priority,
        python_exe=python_exe or sys.executable,
    )
    submit_shadow_job(
        runner,
        name="eval:shadow@fresh",
        pipeline=pipeline,
        input_path=fresh_input,
        out_path=fresh_out,
        baseline=baseline_for_fresh or gold_out,
        limit=fresh_limit,
        priority=fresh_priority,
        python_exe=python_exe or sys.executable,
    )
