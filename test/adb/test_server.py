from python_android_platform_tools.adb.server import start_server


def test_start_server(subprocess_run_stub):
    run_stub = subprocess_run_stub("", "", returncode=0)
    port = "5037"
    cmd = f"adb -P {port} start-server"
    start_server(port)
    run_stub.assert_called_once_with(
        cmd,
        timeout=10,
        shell=True,
        check=False,
        encoding="utf-8",
        capture_output=True,
    )
