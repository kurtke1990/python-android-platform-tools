from python_android_platform_tools.adb.common import execute_command


def start_server(port: str = "5037") -> None:
    cmd = f"-P {port} start-server"
    execute_command(cmd=cmd, is_adb_shell=False, timeout=10)


def stop_server() -> None:
    cmd = "kill-server"
    execute_command(cmd=cmd, is_adb_shell=False, timeout=10)
