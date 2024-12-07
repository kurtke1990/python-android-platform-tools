from itertools import product
from subprocess import TimeoutExpired

import pytest

from python_android_platform_tools.adb import client
from python_android_platform_tools.adb.common import State, Transport
from python_android_platform_tools.exception import ADBCommandTimeoutException

attached_devices_output = """List of devices attached
98201FFAZ001P4         device
192.168.1.200:5555     offline
0a388e93          unauthorized
"""

attached_devices_output_w_details = """List of devices attached
98201FFAZ001P4         device usb:0-1 product:flame model:Pixel_4 device:flame transport_id:3
192.168.1.200:5555     offline product:sdk_google_phone_x86 model:Android_SDK_built_for_x86 device:generic_x86
0a388e93               unauthorized usb:1-1
"""

no_devices_attached_output = """List of devices attached
"""


def test_get_attached_devices(subprocess_run_stub, assert_subprocess_run_called_with):
    run_stub = subprocess_run_stub(
        stdout=attached_devices_output_w_details, stderr="", returncode=0
    )
    cmd = "adb devices -l"
    assert client.get_attached_devices(show_details=True) == [
        {
            "udid": "98201FFAZ001P4",
            "state": "device",
            "connected_usb": "0-1",
            "product": "flame",
            "model": "Pixel_4",
            "device_architecture": "flame",
            "transport_id": "3",
        },
        {
            "udid": "192.168.1.200:5555",
            "state": "offline",
            "connected_usb": None,
            "product": "sdk_google_phone_x86",
            "model": "Android_SDK_built_for_x86",
            "device_architecture": "generic_x86",
            "transport_id": None,
        },
        {
            "udid": "0a388e93",
            "state": "unauthorized",
            "connected_usb": "1-1",
            "product": None,
            "model": None,
            "device_architecture": None,
            "transport_id": None,
        },
    ]
    assert_subprocess_run_called_with(run_stub, cmd)


def test_no_attached_devices(subprocess_run_stub):
    subprocess_run_stub(stdout=no_devices_attached_output, stderr="", returncode=0)
    assert client.get_attached_devices(show_details=True) == []


def test_get_attached_devices_without_details(
    subprocess_run_stub, assert_subprocess_run_called_with
):
    run_stub = subprocess_run_stub(stdout=attached_devices_output, stderr="", returncode=0)
    cmd = "adb devices"
    assert client.get_attached_devices(show_details=False) == [
        {
            "udid": "98201FFAZ001P4",
            "state": "device",
        },
        {
            "udid": "192.168.1.200:5555",
            "state": "offline",
        },
        {
            "udid": "0a388e93",
            "state": "unauthorized",
        },
    ]
    assert_subprocess_run_called_with(run_stub, cmd)


@pytest.mark.parametrize(
    "state, transport",
    list(product(list(Transport), list(State))),
    ids=lambda param: param.value,  # make test case name look better
)
def test_wait_for(state, transport, subprocess_run_stub, assert_subprocess_run_called_with):
    cmd = f"adb wait-for-{transport.value}-{state.value}"
    run_stub = subprocess_run_stub("", "", 0)
    client.wait_for(transport, state)
    assert_subprocess_run_called_with(run_stub, cmd, timeout=3)


@pytest.mark.parametrize(
    "state, transport",
    list(product(list(Transport), list(State))),
    ids=lambda param: param.value,  # make test case name look better
)
def test_wait_for_but_timedout(state, transport, subprocess_run_stub):
    cmd = f"adb wait-for-{transport.value}-{state.value}"
    timeout = 3
    subprocess_run_stub("", "", 1, TimeoutExpired(cmd, timeout))
    with pytest.raises(
        ADBCommandTimeoutException, match=f"Command {cmd!r} timed out after {timeout} seconds."
    ):
        client.wait_for(transport, state)
