from unittest.mock import MagicMock

import pytest


@pytest.fixture
def subprocess_run_stub(monkeypatch):
    cp = MagicMock()
    run_stub = MagicMock()
    monkeypatch.setattr("python_android_platform_tools.adb.client.subprocess.run", run_stub)

    def prepare(stdout, stderr, returncode):
        cp.stdout = stdout
        cp.stderr = stderr
        cp.returncode = returncode
        run_stub.return_value = cp
        return run_stub

    return prepare
