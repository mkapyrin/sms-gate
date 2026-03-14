import asyncio
import shutil


class ADBManager:
    """Manages ADB connection and port forwarding to Android device via USB."""

    def __init__(self, local_port: int = 8080, remote_port: int = 8080) -> None:
        self.local_port = local_port
        self.remote_port = remote_port
        self._adb = shutil.which("adb")
        if not self._adb:
            raise RuntimeError("adb not found in PATH. Install Android SDK Platform Tools.")

    async def _run(self, *args: str) -> tuple[int, str, str]:
        proc = await asyncio.create_subprocess_exec(
            self._adb, *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        return proc.returncode, stdout.decode().strip(), stderr.decode().strip()

    async def is_device_connected(self) -> bool:
        code, out, _ = await self._run("devices")
        lines = [l for l in out.splitlines()[1:] if l.strip() and "device" in l]
        return len(lines) > 0

    async def get_device_info(self) -> dict | None:
        if not await self.is_device_connected():
            return None
        _, model, _ = await self._run("shell", "getprop", "ro.product.model")
        _, android_ver, _ = await self._run("shell", "getprop", "ro.build.version.release")
        _, serial, _ = await self._run("get-serialno")
        return {"model": model, "android": android_ver, "serial": serial}

    async def setup_port_forward(self) -> bool:
        code, out, err = await self._run(
            "forward", f"tcp:{self.local_port}", f"tcp:{self.remote_port}"
        )
        if code != 0:
            raise RuntimeError(f"adb forward failed: {err}")
        return True

    async def remove_port_forward(self) -> None:
        await self._run("forward", "--remove", f"tcp:{self.local_port}")

    async def list_forwards(self) -> str:
        _, out, _ = await self._run("forward", "--list")
        return out

    async def check_gateway_app(self) -> bool:
        """Check if SMS Gateway app is installed on the device."""
        code, out, _ = await self._run(
            "shell", "pm", "list", "packages", "com.capcom.smsgateway"
        )
        return "com.capcom.smsgateway" in out
