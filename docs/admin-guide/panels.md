# Maintaining gene panels

This page describes how admins load and maintain gene panels from the command line. For the panel file format, and for how users edit panels in the web interface, see [Gene panels](../user-guide/panels.md) in the user guide. PanelApp panels are described in [PanelApp gene panels](panelapp_panels.md).

## Loading a panel

Load a gene panel from a file with:

```bash
scout load panel <panel-file> --panel-id <panel-id> --institute <institute-id>
```

The panel ID, institute, version, date and display name can be given either as options or in the [optional header](../user-guide/panels.md#custom-panels-optional-header) of the panel file. Useful options:

- `--panel-id`: the panel identifier (panel name)
- `--institute`: the institute that owns the panel. The institute must exist in Scout
- `-v`, `--version`: the panel version. Defaults to 1.0
- `-d`, `--date`: date of the panel, on the format `2017-12-24`. Defaults to today
- `-n`, `--display-name`: a display name for the panel
- `-t`, `--panel-type`: `clinical` (default) or `research`

To load a new version of a panel that already exists, give a version number that is not already in the database. Loading a version that exists fails.

See `scout load panel --help` for all options, including loading the OMIM-AUTO panel (`--omim`) and PanelApp panels (`--panel-app`).

Panels loaded from the command line start out with an empty maintainer list, which means that only admins can change them in the web interface. This also applies to a new version of an existing panel loaded from a file. Use `scout update panel --add-maintainer` (below) to give users edit rights.

!!! note
    `scout load panel --maintainer <user-id>` checks that the user exists, but the maintainer is not stored on the loaded panel ([#6749](https://github.com/Clinical-Genomics/scout/issues/6749)). Add maintainers with `scout update panel` after loading.

## Updating a panel

Update an existing panel with `scout update panel`:

```bash
scout update panel --panel <panel-id> [OPTIONS]
```

| Option | Description |
|---|---|
| `-p`, `--panel` | The panel ID (panel name) to update. *Required* |
| `--version` | The version to update. Defaults to the latest version |
| `-a`, `--add-maintainer` | Add a user as maintainer of the panel |
| `-r`, `--revoke-maintainer` | Remove a user from the maintainers of the panel |
| `-d`, `--update-date` | Set the date of the panel, on the format `2017-12-24` |
| `--update-version` | Change the version number of the panel |

Changing the date or version number also updates the panel information stored on the cases that use the panel.

## Panel maintainers

Maintainers are the users allowed to change a panel in the web interface, in addition to admins. See [Panel maintainers and edit permissions](../user-guide/panels.md#panel-maintainers-and-edit-permissions) in the user guide for what maintainers can do.

Maintainers are given by their Scout user ID. Unless an ID was set when the user was created, this is the user's email address.

Add a maintainer:

```bash
scout update panel --panel <panel-id> --add-maintainer <user-id>
```

Remove a maintainer:

```bash
scout update panel --panel <panel-id> --revoke-maintainer <user-id>
```

For example, to make Clark Kent a maintainer of the latest version of `panel1`:

```bash
scout update panel --panel panel1 --add-maintainer clark@mail.com
```

Some things to keep in mind:

- Each command adds or removes one user. Run the command once per user.
- Adding a maintainer fails if the user does not exist in Scout, or is already a maintainer of the panel.
- Revoking a user that is not a maintainer logs a warning and leaves the maintainers unchanged.
- Maintainers are stored on each panel version. Without `--version` only the latest version is changed, which is the version new versions are made from in the web interface.
- Removing the last maintainer leaves the panel editable by admins only.
- Change maintainers in a separate command from `--update-version` and `--update-date`. Only one kind of change is saved per command: a new version number takes precedence over maintainer changes, and maintainer changes over a new date.
