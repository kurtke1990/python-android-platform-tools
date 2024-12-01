import subprocess

from python_android_platform_tools.exception import (
    ADBCommandInvocationException,
    ADBCommandTimeoutException,
)
from python_android_platform_tools.lib import remove_empty_strings, search_by_pattern


def get_attached_devices(show_details: bool = False) -> dict:
    """
    Get all attached android devices.

    :param show_details: if True, the product, model, transport_id etc will be listed the return value. if False, these won't be shown in the return value.
    :type show_details: bool
    """
    cmd = "devices -l" if show_details else "devices"
    stdout, *_ = _execute_cmd(cmd, is_adb_shell=False)
    ret = []
    dev_details = [ln for ln in stdout.splitlines()[1:] if ln]

    for detail in dev_details:
        processed_detail = {}
        processed_detail["udid"] = _get_udid(detail)
        processed_detail["state"] = _get_device_mode(detail)
        if show_details:
            processed_detail["connected_usb"] = _get_host_connected_usb_port(detail)
            processed_detail["product"] = _get_product(detail)
            processed_detail["model"] = _get_model(detail)
            processed_detail["device_architecture"] = _get_device_arch(detail)
            processed_detail["transport_id"] = _get_transport_id(detail)
        ret.append(processed_detail)
    return ret


def _execute_cmd(
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
            f"Failed to run command due to {completed.stderr} with the non-zero return code {completed.returncode}"
        )
    return completed.stdout, completed.stderr, completed.returncode


def _get_udid(detail: str) -> str | None:
    return search_by_pattern(detail, r"^([\w\-_?!*+&!#@%$:\(\)~;\/.]{1,})\s{1,}", 1)


def _get_device_mode(detail: str) -> str | None:
    return search_by_pattern(detail, r"\s{1,}(device|unauthorized|offline)", 1)


def _get_host_connected_usb_port(detail: str) -> str | None:
    return search_by_pattern(detail, r"(usb:)([\d\-]+)", 2)


def _get_product(detail: str) -> str | None:
    return search_by_pattern(detail, r"(product:)([\w\-_?!*+&!#@%$:\(\)~;\/.]+)", 2)


def _get_model(detail: str) -> str | None:
    return search_by_pattern(detail, r"(model:)([\w\-_?!*+&!#@%$:\(\)~;\/.]+)", 2)


def _get_device_arch(detail: str) -> str | None:
    return search_by_pattern(detail, r"(device:)([\w\-_?!*+&!#@%$:\(\)~;\/.]+)", 2)


def _get_transport_id(detail: str) -> str | None:
    return search_by_pattern(detail, r"(transport_id:)(\d+)", group_num=2)
