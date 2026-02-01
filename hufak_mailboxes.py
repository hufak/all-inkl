import tomllib
from pathlib import Path

CONFIG_FILE = Path("hufak_mailboxes.toml")
EMAIL_DOMAIN = "hufak.net"
# SNAPPYMAIL_DATA = Path(
#     "$HOME/cloud.hufak.net/data/appdata_snappymail/_data_/_default_/storage/hufak.net/"
# )


def load_shared_mailboxes() -> list[dict[str, str]]:
    if not CONFIG_FILE.exists():
        return []

    data = tomllib.loads(CONFIG_FILE.read_text())

    return [
        {
            "prefix": prefix,
            "name": cfg.get("name", prefix),
            "email": f"{prefix}@{EMAIL_DOMAIN}",
        }
        for prefix, cfg in data.items()
        if isinstance(cfg, dict)
    ]
