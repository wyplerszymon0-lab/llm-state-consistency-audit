import subprocess

import pytest

import run_audit
from bench import sandbox
from bench.sandbox import Execution, docker_command, execute_docker
from bench.scoring import score_all

HAS_DOCKER = sandbox.docker_available()
needs_docker = pytest.mark.skipif(not HAS_DOCKER, reason="Docker daemon not available")


def write(tmp_path, body):
    path = tmp_path / "s.py"
    path.write_text(body, encoding="utf-8")
    return path


def test_container_is_locked_down(tmp_path):
    cmd = docker_command(tmp_path / "s.py", 10, "bench-test")
    pairs = {cmd[i]: cmd[i + 1] for i in range(len(cmd) - 1)}
    assert pairs["--network"] == "none"
    assert "--read-only" in cmd and pairs["--tmpfs"].startswith("/tmp:")
    assert pairs["--memory"] == pairs["--memory-swap"] == "256m"
    assert pairs["--cpus"] == "1" and pairs["--pids-limit"] == "64"
    assert pairs["--cap-drop"] == "ALL" and pairs["--security-opt"] == "no-new-privileges"
    assert pairs["--user"] == "65534:65534"
    assert pairs["-v"].endswith(":/sub/submission.py:ro")  # the only thing mounted, read-only
    assert cmd[cmd.index(sandbox.DOCKER_IMAGE) + 1 : cmd.index(sandbox.DOCKER_IMAGE) + 3] == ["timeout", "10"]


def test_audit_refuses_docker_mode_without_a_daemon(monkeypatch, capsys):
    monkeypatch.setattr(run_audit, "docker_available", lambda: False)
    assert run_audit.main(["--sandbox", "docker"]) == 2
    assert "Docker daemon" in capsys.readouterr().err


def test_score_all_uses_the_given_executor(tmp_path):
    (tmp_path / "ledger" / "m").mkdir(parents=True)
    (tmp_path / "ledger" / "m" / "run_1.py").write_text("def run():\n    return 0\n", encoding="utf-8")
    seen = []

    def fake(path):
        seen.append(path.name)
        return Execution("ok", value=6553.73)

    [summary] = score_all(tmp_path, executor=fake)
    assert seen == ["run_1.py"] and summary.passes("ledger") == 1


@pytest.fixture(scope="module")
def image():
    # Pull once up front, so the first test's timeout does not include the download.
    subprocess.run(["docker", "pull", "-q", sandbox.DOCKER_IMAGE], capture_output=True, timeout=600)
    return sandbox.DOCKER_IMAGE


@needs_docker
def test_returns_the_value_and_ignores_prints(tmp_path, image):
    result = execute_docker(write(tmp_path, "print(1)\ndef run():\n    print('noise')\n    return 4.5\n"))
    assert result == Execution("ok", value=4.5)


@needs_docker
def test_runs_as_nobody_and_sees_only_the_submission(tmp_path, image):
    body = "import os\ndef run():\n    assert os.listdir('/sub') == ['submission.py']\n    return float(os.getuid())\n"
    assert execute_docker(write(tmp_path, body)).value == 65534


@needs_docker
def test_has_no_network(tmp_path, image):
    body = (
        "import socket\n"
        "def run():\n"
        "    socket.create_connection(('1.1.1.1', 53), timeout=3)\n"
        "    return 1.0\n"
    )
    result = execute_docker(write(tmp_path, body))
    assert result.status == "error"
    assert "Network is unreachable" in result.error


@needs_docker
def test_cannot_write_outside_tmp(tmp_path, image):
    body = "def run():\n    open('/sub/evil.py', 'w').write('x')\n    return 1.0\n"
    result = execute_docker(write(tmp_path, body))
    assert result.status == "error" and "Read-only file system" in result.error
    assert not (tmp_path / "evil.py").exists()


@needs_docker
def test_memory_is_limited(tmp_path, image):
    body = "def run():\n    blocks = [bytearray(64 * 2**20) for _ in range(16)]  # 1 GB\n    return 1.0\n"
    result = execute_docker(write(tmp_path, body))
    assert result == Execution("error", error="killed (memory limit of 256 MB?)")


@needs_docker
def test_infinite_loop_times_out(tmp_path, image):
    result = execute_docker(write(tmp_path, "def run():\n    while True:\n        pass\n"), timeout=2)
    assert result.status == "timeout"
