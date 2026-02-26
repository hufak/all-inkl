#!/usr/bin/env python3
import json
from pathlib import Path
from string import Template

import questionary
from rich.console import Console
from rich.panel import Panel

from hufak_mailboxes import EMAIL_DOMAIN, load_shared_mailboxes
from hufak_nextcloud_occ import run_occ

console = Console()


def generate_signature(nc_uid, email_prefix):
    department = load_shared_mailboxes()[email_prefix]
    return (
        Template(open("hufak_signature_template.txt").read())
        .substitute(
            {
                "pronouns": run_occ(
                    ["user:profile", nc_uid, "pronouns"], capture_output=True
                ),
                "person_name": run_occ(
                    ["user:profile", nc_uid, "displayname"], capture_output=True
                ),
                "department_de": department["de"],
                "department_en": department["en"],
            }
        )
        .replace("\n", "<br>")
    )


def add_snappymail_identity(
    identities_path: Path, email: str, name: str, signature: str
):
    identities = (
        json.loads(identities_path.read_text())
        if identities_path.exists()
        else {"---": {"Id": "", "Name": name}}
    )
    identity = identities["---"]  # TODO check if identity with that name exists
    identity = {
        **identity,
        **{
            "Name": name,
            "Email": email,
            "Signature": signature,
            "SignatureInsertBefore": True,
        },
    }
    # TODO is this automatically stored in root identities?
    with open("filename", "w") as f:
        json.dump(identities, f)


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
            "Use a shared email account as main account?",
            choices=["Custom/User-specific"] + list(shared_mailboxes.keys()),
        ).ask()

        if choice == "Custom/User-specific":
            choice = questionary.text(
                "Enter full email address:",
                validate=lambda t: (
                    True if "@" in t else "Please enter a valid email address"
                ),
            ).ask()

        password = questionary.text(
            "Mailbox password:",
            validate=lambda t: len(t.strip()) > 0 or "Cannot be empty",
        ).ask()
        set_snappymail_main_account(nc_uid, choice, password)
    return nc_uid


def add_snappymail_extra_account(nc_uid: str, email_prefix: str):
    # TODO add entry to the user's additionalaccounts file
    # TODO create subdirectory and identities file in it
    # TODO "SignatureInsertBefore":true, into identities
    pass


def main():
    # TODO ask if to add main account
    nc_uid = select_snappymail_main_account()

    # TODO ask if to add extra accounts
    shared_mailboxes = load_shared_mailboxes()
    if shared_mailboxes:
        choices = questionary.checkbox(
            "Add shared email account(s)? (DON'T DO THIS when the primary account is a shared account!)",
            choices=shared_mailboxes.keys(),
        ).ask()

        if choices:
            for choice in choices:
                add_snappymail_extra_account(nc_uid, choice)


if __name__ == "__main__":
    main()
