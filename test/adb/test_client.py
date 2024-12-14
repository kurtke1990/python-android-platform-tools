from itertools import product
from subprocess import TimeoutExpired

import pytest

from python_android_platform_tools.adb import client
from python_android_platform_tools.adb.common import State, Transport
from python_android_platform_tools.exception import (
    ADBCommandInvocationException,
    ADBCommandTimeoutException,
)

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

properties_output = """[DEVICE_PROVISIONED]: [1]
[ro.system.build.fingerprint]: [google/flame/flame:13/TP1A.221005.002.B2/9382335:user/release-keys]
[ro.system.build.date]: [Thu Dec  8 00:54:08 UTC 2022]
[ro.build.version.known_codenames]: [Base,Base11,Cupcake,Donut,Eclair,Eclair01,EclairMr1,Froyo,Gingerbread,GingerbreadMr1,Honeycomb,HoneycombMr1,HoneycombMr2,IceCreamSandwich,IceCreamSandwichMr1,JellyBean,JellyBeanMr1,JellyBeanMr2,Kitkat,KitkatWatch,Lollipop,LollipopMr1,M,N,NMr1,O,OMr1,P,Q,R,S,Sv2,Tiramisu]
[cache_key.telephony.get_active_data_sub_id]: [-4434845841350405319]
[hwservicemanager.ready]: [true]
[gsm.operator.isroaming]: [false]
[persist.sys.boot.reason]: []
(invalid_key_format): [this_shall_be_skipped]
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


@pytest.mark.parametrize(
    "adb_root_succeed_output", ["restarting adbd as root", "adbd is already running as root"]
)
def test_grant_root_permission_successfully(adb_root_succeed_output, subprocess_run_stub):
    subprocess_run_stub(adb_root_succeed_output, "", 0)
    client.grant_root_permission()


def test_grant_root_permission_but_device_runs_production_build(subprocess_run_stub):
    subprocess_run_stub("adbd cannot run as root in production builds", "", 0)
    with pytest.raises(
        ADBCommandInvocationException,
        match="Failed to grant the root permission to device since the target device is running with the production build.",
    ):
        client.grant_root_permission()


def test_get_all_properties(subprocess_run_stub):
    subprocess_run_stub(properties_output, "", 0)
    properties = client.get_all_properties()
    assert properties == {
        "DEVICE_PROVISIONED": "1",
        "ro.system.build.fingerprint": "google/flame/flame:13/TP1A.221005.002.B2/9382335:user/release-keys",
        "ro.system.build.date": "Thu Dec  8 00:54:08 UTC 2022",
        "ro.build.version.known_codenames": "Base,Base11,Cupcake,Donut,Eclair,Eclair01,EclairMr1,Froyo,Gingerbread,GingerbreadMr1,Honeycomb,HoneycombMr1,HoneycombMr2,IceCreamSandwich,IceCreamSandwichMr1,JellyBean,JellyBeanMr1,JellyBeanMr2,Kitkat,KitkatWatch,Lollipop,LollipopMr1,M,N,NMr1,O,OMr1,P,Q,R,S,Sv2,Tiramisu",
        "cache_key.telephony.get_active_data_sub_id": "-4434845841350405319",
        "hwservicemanager.ready": True,
        "gsm.operator.isroaming": False,
        "persist.sys.boot.reason": None,
    }
