import asyncio
import os
import signal
from utils.logger import get_logger

log = get_logger(__name__, process_name = "shell")

class ShellService:
    @staticmethod
    async def execute_command(command: str, timeout: int = 30) -> dict:
        """
        Runs a shell command in Termux and returns stdout, stderr, and return code.
        Includes a timeout to prevent the agent from hanging.
        """
        log.info(f"Executing (Timeout {timeout}s): {command}")

        # Start the process in a new session so we can kill the entire process group if needed
        # preexec_fn=os.setsid is used to create a new process group.
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                preexec_fn=os.setsid
            )
        except Exception as e:
            log.error(f"Failed to start process: {str(e)}")
            return {"stdout": "", "stderr": str(e), "exit_code": -1}

        try:
            # Wait for the command to finish with a timeout
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
            exit_code = process.returncode
        except asyncio.TimeoutError:
            log.warning(f"Command timed out after {timeout} seconds. Killing process group.")
            # Kill the process group to ensure any child processes are also terminated
            try:
                os.killpg(os.getpgid(process.pid), signal.SIGKILL)
            except ProcessLookupError:
                pass # Process already died
            
            return {
                "stdout": "",
                "stderr": f"Command timed out after {timeout} seconds and was killed.",
                "exit_code": 124 # Standard exit code for timeout
            }

        # Decode output
        stdout_str = stdout.decode("utf-8", errors="replace")
        stderr_str = stderr.decode("utf-8", errors="replace")

        log.info(f"Exit code: {exit_code}")

        return {
            "stdout": stdout_str,
            "stderr": stderr_str,
            "exit_code": exit_code
        }
