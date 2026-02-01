## hufak @ all-inkl

Shell configs and Python scripts for managing the Nextcloud instance hosted at all-inkl. Work in progress!

## Dependencies

```sh
pip3 install questionary rich
```

## Nextcloud global configuration

Some persistent global settings that can only be set from the command line, not the administrator web interface:

```sh
occ config:app:set core shareapi_enable_link_password_by_default --value no
occ config:app:set core shareapi_allow_custom_tokens --value yes
```
