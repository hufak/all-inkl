#!/usr/bin/env python3
import questionary
from rich.console import Console
from rich.panel import Panel

from hufak_mailboxes import EMAIL_DOMAIN, load_shared_mailboxes
from hufak_nextcloud_occ import run_occ

console = Console()


def set_snappymail_main_account(nc_uid: str, email_prefix: str, password: str):
    email = f"{email_prefix}@{EMAIL_DOMAIN}"
    run_occ(
        ["snappymail:settings", nc_uid, email, password],
        description="Set a Nextcloud user's snappymail primary email account",
    )
    console.print(
        Panel(
            f"Shared mailbox [bold]{email}[/bold] added to SnappyMail.",
            title="SnappyMail",
            style="green",
        )
    )


def select_snappymail_main_account(nc_uid: str | None = None):
    shared_mailboxes = load_shared_mailboxes()

    nc_uid = (
        nc_uid
        or questionary.text(
            "Nextcloud username:",
            validate=lambda t: len(t.strip()) > 0 or "Cannot be empty",
        ).ask()
    )

    if shared_mailboxes:
        choice = questionary.select(
            "Assign a shared email account?",
            choices=["None"] + list(shared_mailboxes.keys()),
        ).ask()

        if choice != "None":
            set_snappymail_main_account(nc_uid, choice, password)


def add_snappymail_extra_account(nc_uid: str, email_prefix: str):
    # TODO add entry to the user's additionalaccounts file
    # TODO create subdirectory and identities file in it
    pass


def main():
    # TODO ask if to add main account
    # TODO ask if to add extra accounts (in loop)
    # TODO "SignatureInsertBefore":true, into identities
    pass


if __name__ == "__main__":
    main()
