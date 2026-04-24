from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence


@dataclass(frozen=True)
class CompletedJob:
    command: tuple[str, ...]
    exit_code: int
    stdout: str
    stderr: str
    runtime_seconds: float


class CommandRunner:
    """Thin wrapper around subprocess for future external tool integrations."""

    def run(
        self,
        command: Sequence[str],
        cwd: Path | None = None,
        env: Mapping[str, str] | None = None,
        timeout_seconds: int | None = None,
    ) -> CompletedJob:
        start = time.perf_counter()
        completed = subprocess.run(
            list(command),
            cwd=str(cwd) if cwd else None,
            env=dict(env) if env else None,
            capture_output=True,
            check=False,
            text=True,
            timeout=timeout_seconds,
        )
        runtime = time.perf_counter() - start
        return CompletedJob(
            command=tuple(command),
            exit_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            runtime_seconds=runtime,
        )

