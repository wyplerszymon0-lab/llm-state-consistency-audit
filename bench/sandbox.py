"""Runs a submission in a separate Python process and captures the value of run().

This isolates crashes, infinite loops and stray prints from the harness. It is NOT a
security boundary: generated code runs with your user's permissions. Run untrusted
submissions inside a container or VM.
"""

import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

MARKER = "__BENCH_RESULT__"

DRIVER = f"""
import importlib.util, json, sys
spec = importlib.util.spec_from_file_location("submission", sys.argv[1])
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
value = float(module.run())
print("{MARKER}" + json.dumps(value))
"""


@dataclass(frozen=True)
class Execution:
    status: str  # "ok", "error" or "timeout"
    value: float | None = None
    error: str | None = None


def execute(path: Path, timeout: float = 10.0) -> Execution:
    with tempfile.TemporaryDirectory() as workdir:
        try:
            proc = subprocess.run(
                [sys.executable, "-I", "-c", DRIVER, str(Path(path).resolve())],
                cwd=workdir,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return Execution("timeout", error=f"exceeded {timeout:g}s")

    for line in reversed(proc.stdout.splitlines()):
        if line.startswith(MARKER):
            return Execution("ok", value=json.loads(line[len(MARKER):]))

    stderr = proc.stderr.strip().splitlines()
    return Execution("error", error=stderr[-1] if stderr else f"exit code {proc.returncode}")
