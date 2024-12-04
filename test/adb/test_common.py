from subprocess import TimeoutExpired

import pytest

from python_android_platform_tools.adb.common import execute_command
from python_android_platform_tools.exception import (
    ADBCommandInvocationException,
    ADBCommandTimeoutException,
)


def test_execute_command_but_timeout(subprocess_run_stub):
    cmd = "cmd"
    timeout = 3
    udid = "udid"
    subprocess_run_stub("", "", 0, TimeoutExpired(cmd, timeout))

    with pytest.raises(
        ADBCommandTimeoutException,
        match=f"Command 'adb -s {udid} {cmd}' timed out after {timeout} seconds.",
    ):
        execute_command(cmd=cmd, udid=udid, timeout=timeout, is_adb_shell=False)


def test_execute_command_but_a_non_returncode_returns(subprocess_run_stub):
    cmd = "cmd"
    timeout = 3
    udid = "udid"
    stderr = "something went wrong."
    returncode = 127
    subprocess_run_stub("", stderr, returncode)

    with pytest.raises(
        ADBCommandInvocationException,
        match=f"Failed to run command 'adb -s {udid} {cmd}' due to {stderr} with the non-zero return code {returncode}",
    ):
        execute_command(cmd=cmd, udid=udid, timeout=timeout, is_adb_shell=False)
