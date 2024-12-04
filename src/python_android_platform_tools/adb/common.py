import subprocess

from python_android_platform_tools.exception import (
    ADBCommandInvocationException,
    ADBCommandTimeoutException,
)
from python_android_platform_tools.lib import remove_empty_strings


def execute_command(
    cmd: str, udid: str = "", is_adb_shell: bool = True, timeout: int | float = 1.0
) -> tuple[str, str, int]:
    cmd = " ".join(
        remove_empty_strings(
            [
                "adb",
                f"-s {udid}" if udid else "",
                "shell" if is_adb_shell else "",
                cmd,
            ]
        )
    )
    try:
        completed = subprocess.run(
            cmd,
            timeout=timeout,
            shell=True,
            check=False,
            encoding="utf-8",
            capture_output=True,
        )
    except subprocess.TimeoutExpired as e:
        raise ADBCommandTimeoutException(
            f"Command {cmd!r} timed out after {timeout} seconds."
        ) from e
    if completed.returncode != 0:
        raise ADBCommandInvocationException(
            f"Failed to run command {cmd!r} due to {completed.stderr} with the non-zero return code {completed.returncode}"
        )
    return completed.stdout, completed.stderr, completed.returncode
