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
