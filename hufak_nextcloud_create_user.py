#!/usr/bin/env python3

# pip3 install questionary rich
import re
import sys
from shutil import which
from typing import Optional

import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from hufak_mailboxes import EMAIL_DOMAIN
from hufak_nextcloud_occ import run_occ
from hufak_nextcloud_snappymail import select_snappymail_main_account

console = Console()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def sanitize_username(full_name: str) -> str:
    name = full_name.strip().lower()
    name = re.sub(r"[^\w\s-]", "", name)
    name = re.sub(r"[\s_-]+", ".", name)
    return name


def build_email(username: str) -> str:
    return f"{username}@{EMAIL_DOMAIN}"


def ensure_occ_available():
    if not which("php"):
        console.print(
            Panel(
                "PHP executable not found in PATH.",
                title="Fatal error",
                style="red",
            )
        )
        sys.exit(1)

    run_occ(["--version"], description="occ availability check")


def create_user(username: str, full_name: str, email: str) -> Optional[str]:
    """
    Create a Nextcloud user and return the generated password if available.
    """
    result = run_occ(
        [
            "user:add",
            "--display-name",
            full_name,
            "--email",
            email,
            "--generate-password",
            username,
        ],
        capture_output=True,
        description="User creation",
    )

    password = None
    if result and result.stdout:
        for line in result.stdout.splitlines():
            if "password" in line.lower():
                password = line.split()[-1]

    if not password:
        console.print(
            Panel(
                "User was created, but no password was returned.\n"
                "Your Nextcloud version may not support --generate-password.",
                title="Warning",
                style="yellow",
            )
        )

    return password


def set_pronouns(username: str, pronouns: Optional[str]):
    if not pronouns:
        return

    #'occ user:profile "${username}" pronouns "he/him"'
    run_occ(
        [
            "user:setting",
            username,
            "profile",
            "pronouns",
            pronouns,
        ],
        fatal=False,
        description="Setting pronouns",
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    console.print("[bold green]Nextcloud User Creation Wizard[/bold green]\n")

    ensure_occ_available()

    full_name = questionary.text(
        "Full name:",
        validate=lambda t: len(t.strip()) > 0 or "Name cannot be empty",
    ).ask()

    if not full_name:
        console.print("[red]Aborted.[/red]")
        sys.exit(1)

    username = questionary.text(
        "Username:",
        default=sanitize_username(full_name),
        validate=lambda t: (
            True
            if re.fullmatch(r"[a-z0-9._-]+", t)
            else "Use lowercase letters, numbers, dots, dashes, underscores only"
        ),
    ).ask()

    email = questionary.text(
        "Email address:",
        default=build_email(username),
    ).ask()

    pronouns = questionary.select(
        "Pronouns:",
        choices=[
            "they/them",
            "she/her",
            "he/him",
            "custom",
            "prefer not to say",
        ],
    ).ask()

    if pronouns == "custom":
        pronouns = questionary.text("Enter pronouns:").ask()

    # -----------------------------------------------------------------------
    # Confirmation
    # -----------------------------------------------------------------------

    table = Table(title="Confirm User Details")
    table.add_column("Field", style="bold")
    table.add_column("Value")

    table.add_row("Full name", full_name)
    table.add_row("Username", username)
    table.add_row("Email", email)
    table.add_row("Pronouns", pronouns or "—")

    console.print()
    console.print(table)

    if not questionary.confirm("Create this user?", default=True).ask():
        console.print("[yellow]Aborted.[/yellow]")
        sys.exit(0)

    # -----------------------------------------------------------------------
    # Execution
    # -----------------------------------------------------------------------

    password = create_user(username, full_name, email)
    set_pronouns(username, pronouns)

    if password:
        console.print(
            Panel(
                f"[bold]Username:[/bold] {username}\n"
                f"[bold red]Password:[/bold red] {password}\n\n"
                "⚠️ Copy this password now.\n"
                "It will not be shown again.",
                title="Generated Credentials",
                style="green",
            )
        )
    else:
        console.print(
            Panel(
                f"User [bold]{username}[/bold] created successfully.",
                title="Success",
                style="green",
            )
        )

    # set app order
    run_occ(
        [
            "user:setting",
            username,
            "core",
            "apporder",
            '{"dashboard":{"order":0,"app":"dashboard"},"snappymail":{"order":1,"app":"snappymail"},"collectives":{"order":2,"app":"collectives"},"tables_application_1":{"order":3},"calendar":{"order":4,"app":"calendar"},"files":{"order":5,"app":"files"},"contacts":{"order":6,"app":"contacts"},"polls":{"order":7,"app":"polls"},"tables":{"order":8,"app":"tables"},"passwords":{"order":9,"app":"passwords"},"mail":{"order":10,"app":"mail"},"occweb":{"order":11,"app":"occweb"}}',
        ]
    )

    # set email account
    select_snappymail_main_account(username)


if __name__ == "__main__":
    main()
