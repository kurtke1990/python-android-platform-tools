from python_android_platform_tools.adb.server import start_server, stop_server


def test_start_server(subprocess_run_stub, assert_subprocess_run_called_with):
    run_stub = subprocess_run_stub("", "", returncode=0)
    port = "5037"
    cmd = f"adb -P {port} start-server"
    start_server(port)
    assert_subprocess_run_called_with(run_stub, cmd, timeout=10)


def test_stop_server(subprocess_run_stub, assert_subprocess_run_called_with):
    run_stub = subprocess_run_stub("", "", returncode=0)
    cmd = "adb kill-server"
    stop_server()
    assert_subprocess_run_called_with(run_stub, cmd, timeout=10)
