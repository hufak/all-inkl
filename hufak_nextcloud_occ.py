import subprocess
import sys

from rich.console import Console
from rich.panel import Panel

console = Console()

OCC_CMD = ["php", "/www/htdocs/w00ccd84/cloud.hufak.net/occ"]


# ---------------------------------------------------------------------------
# Core command runner (single subprocess entry point)
# ---------------------------------------------------------------------------
def run_occ(
    args: list[str],
    *,
    capture_output: bool = False,
    fatal: bool = True,
    description: str = "Command",
) -> subprocess.CompletedProcess | None:
    """
    Run an occ command.

    - args: arguments after `occ`
    - capture_output: return stdout/stderr
    - fatal: exit on failure
    """
    cmd = OCC_CMD + args

    try:
        return subprocess.run(
            cmd,
            check=True,
            text=True,
            stdout=subprocess.PIPE if capture_output else None,
            stderr=subprocess.PIPE if capture_output else None,
        )
    except subprocess.CalledProcessError as e:
        console.print(
            Panel(
                e.stderr or f"{description} failed.",
                title="Error",
                style="red",
            )
        )
        if fatal:
            sys.exit(1)
        return None
    except FileNotFoundError:
        console.print(
            Panel(
                "Unable to execute `php occ`.\n"
                "Ensure PHP is installed and you are running this from\n"
                "the Nextcloud root directory.",
                title="Fatal error",
                style="red",
            )
        )
        sys.exit(1)
