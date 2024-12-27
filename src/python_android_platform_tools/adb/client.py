from python_android_platform_tools.adb.common import State, Transport, execute_command
from python_android_platform_tools.exception import (
    ADBCommandInvocationException,
    ADBCommandTimeoutException,
)
from python_android_platform_tools.lib import search_by_pattern


def get_attached_devices(show_details: bool = False) -> list[dict[str, str | None]]:
    """
    Retrieve a list of attached Android devices with optional detailed information.

    :param show_details: If True, include detailed information about each device.
                         If False, only include basic information (default: False).
    :type show_details: bool
    :return: A list of dictionaries, each containing information about an attached device.
             The dictionary keys include:
             - "udid": The unique device identifier.
             - "state": The state of the device (e.g., device, offline).
             - "connected_usb" (optional): The USB port to which the device is connected.
             - "product" (optional): The product name of the device.
             - "model" (optional): The model name of the device.
             - "device_architecture" (optional): The architecture of the device.
             - "transport_id" (optional): The transport ID of the device.
    :rtype: list[dict[str, str | None]]
    """

    cmd = "devices -l" if show_details else "devices"
    stdout, *_ = execute_command(cmd, is_adb_shell=False)
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


def wait_for(transport: Transport, state: State, udid: str = "", timeout: int | float = 3) -> None:
    cmd = f"wait-for-{transport.value}-{state.value}"
    execute_command(cmd, udid=udid, is_adb_shell=False, timeout=timeout)


def grant_root_permission(udid: str = "") -> None:
    cmd = "root"
    stdout, *rest = execute_command(cmd, is_adb_shell=False, udid=udid, timeout=3)
    if stdout.strip() == "adbd cannot run as root in production builds":
        raise ADBCommandInvocationException(
            "Failed to grant the root permission to device since the target device is running with the production build."
        )


def get_all_properties(udid: str = "") -> dict[str, str | bool | None]:
    cmd = "getprop"
    stdout, *rest = execute_command(cmd, udid=udid, timeout=3)
    ret = {}
    for prop_info in stdout.splitlines():
        prop_key = _get_property_key(prop_info.strip())
        if prop_key is None:
            continue
        prop_value = _get_property_value(prop_info.strip())
        ret[prop_key] = prop_value
    return ret


def _get_property_key(prop_info: str) -> str | None:
    return search_by_pattern(prop_info, r"\[(.*)\]\:\s\[(.*)\]", 1)


def _get_property_value(prop_info: str) -> str | bool | None:
    prop_value = search_by_pattern(prop_info, r"\[(.*)\]\:\s\[(.*)\]", 2)
    if prop_value is None or not len(prop_value):
        return None
    elif prop_value == "true":
        return True
    elif prop_value == "false":
        return False
    else:
        return prop_value


def connect_device_wirelessly(host: str, port: int = 5555) -> None:
    cmd = f"connect {host}:{port}"
    stdout, stderr, returncode = execute_command(cmd)
    if "Operation timed out" in stdout:
        raise ADBCommandTimeoutException(
            "Unable to connect the device wirelessly since it timed out."
        )
