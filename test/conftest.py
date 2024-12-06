from unittest.mock import MagicMock

import pytest


@pytest.fixture
def subprocess_run_stub(monkeypatch):
    cp = MagicMock()
    run_stub = MagicMock()
    monkeypatch.setattr("python_android_platform_tools.adb.common.subprocess.run", run_stub)

    def prepare(stdout, stderr, returncode, exception=None):
        cp.stdout = stdout
        cp.stderr = stderr
        cp.returncode = returncode
        if exception is None:
            run_stub.return_value = cp
        else:
            run_stub.side_effect = exception
        return run_stub

    return prepare


@pytest.fixture
def assert_subprocess_run_called_with():
    def assert_called_with(run_stub, cmd, timeout: int | float = 1.0):
        run_stub.assert_called_once_with(
            cmd,
            timeout=timeout,
            shell=True,
            check=False,
            encoding="utf-8",
            capture_output=True,
        )

    return assert_called_with
