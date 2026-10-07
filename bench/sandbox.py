"""Runs a submission and captures the value of run().

Two modes:

- execute(): a separate Python process. This isolates crashes, infinite loops and
  stray prints from the harness, but it is NOT a security boundary: generated code
  runs with your user's permissions.
- execute_docker(): a throwaway container with no network, a read-only file
  system, CPU, memory and process limits, no Linux capabilities and an
  unprivileged user. The submission is mounted read-only; nothing else from the
  host is visible. Use it for code you have not read.
"""

import json
import subprocess
import sys
import tempfile
import uuid
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


DOCKER_IMAGE = "python:3.12-slim"
CONTAINER_PATH = "/sub/submission.py"
STARTUP_GRACE_S = 20  # time for Docker to start the container, on top of the run timeout
TIMEOUT_EXIT = 124  # what coreutils `timeout` returns when it stops the program
KILLED_EXIT = 137  # SIGKILL, e.g. the kernel's out-of-memory killer


def docker_command(path: Path, timeout: float, name: str, image: str = DOCKER_IMAGE) -> list[str]:
    """The `docker run` invocation for one submission (kept separate so it can be checked)."""
    return [
        "docker", "run", "--rm", "--name", name,
        "--network", "none",  # no network at all
        "--read-only", "--tmpfs", "/tmp:size=16m",  # nothing writable except a small /tmp
        "--memory", "256m", "--memory-swap", "256m",  # no swap beyond the memory limit
        "--cpus", "1", "--pids-limit", "64",
        "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
        "--user", "65534:65534",  # nobody
        "-v", f"{Path(path).resolve()}:{CONTAINER_PATH}:ro",
        image,
        "timeout", f"{timeout:g}", "python", "-I", "-c", DRIVER, CONTAINER_PATH,
    ]  # fmt: skip


def docker_available() -> bool:
    try:
        return subprocess.run(["docker", "info"], capture_output=True, timeout=30).returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def execute_docker(path: Path, timeout: float = 10.0, image: str = DOCKER_IMAGE) -> Execution:
    name = f"bench-{uuid.uuid4().hex[:12]}"
    try:
        proc = subprocess.run(
            docker_command(path, timeout, name, image),
            capture_output=True,
            text=True,
            timeout=timeout + STARTUP_GRACE_S,
        )
    except subprocess.TimeoutExpired:
        subprocess.run(["docker", "kill", name], capture_output=True)
        return Execution("timeout", error=f"exceeded {timeout:g}s (container did not finish)")

    for line in reversed(proc.stdout.splitlines()):
        if line.startswith(MARKER):
            return Execution("ok", value=json.loads(line[len(MARKER):]))
    if proc.returncode == TIMEOUT_EXIT:
        return Execution("timeout", error=f"exceeded {timeout:g}s")
    if proc.returncode == KILLED_EXIT:
        return Execution("error", error="killed (memory limit of 256 MB?)")
    stderr = proc.stderr.strip().splitlines()
    return Execution("error", error=stderr[-1] if stderr else f"exit code {proc.returncode}")
