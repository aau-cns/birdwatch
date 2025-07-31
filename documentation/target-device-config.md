# Target Device Configuration

Inside the config/target_devices folder, each possible target device, and the name of the file defines the name with which it will be displayed.

Each file has three sections

## SSH Connection

Defines the necessary data to stablish an SSH connection with the target device. This section is optional and if it is not present, everything will be run locally

```yaml
ssh_connection:
  username: user
  selected_network: 1
  networks:
  - name: IST
    ip: 143.205.120.159
  - name: Local
    ip: 10.42.0.126
```

- `username` is the name of the user to which to connect to
- `selected_network` is the index (starting from zero) of the network to which to stablish a connection
- `networks` is a list of possible network through which to connect to the device
    - `name` is simply a name under which to show the network in the GUI
    - `ip` address of the network

## Files

Defines the path of different files or directories needed. This section is mandatory.

```yaml
files:
  workspace_path: ~/workspace/
  source: install/setup.bash
  nodes: config/nodes.yaml
  topics: config/topics.yaml
  recordings: ~/Documents/recordings/
  missions: ~/Documents/missions/
  parameters: config/parameters/
```

`workspace_path` defines the root of a workspace in the target device it needs to be specified as an absolute path either as `~/path` or `/home/<username>/path` (`<username>` should be the one specified in [SSH Connection](#ssh-connection), or the local user if no SSH configuration is provided)

The rest of the paths can be specified as relative to the workspace path, or absolute if they are specified either as `~/path` or `/home/<username>`


Field         | Required | Type   | Comment
--------------|----------|--------|---------
 `source`     | No       | File   | File that needs to be source in each shell running scripts for the mission
 `nodes`      | Yes      | File   | Defines what to execute when launching the mission. They will be run in the target device. This is explained further in [Nodes File](nodes-file.md)
 `topics`     | Yes      | File   | Defines what topics to record. This is explained further in [Topics File](topics-file.md)
 `recording`  | Yes      | Folder | Where in the target device to store the recorded topics
 `missions`   | Yes      | Folder | Where in the target device to send the defined mission to
 `parameters` | Yes      | Folder | Contains the parameter files of the workspace with the values it is currently using. This is further explained in [Parameter Files](parameter-files.md)


## Color Theme

Defines the colors associated with the device, which will be the accent colors of the GUI when the device is selected. This section is optional and if it is not present, a default theme will be used

```yaml
color_theme:
  primary: '#98302a'
  dark_primary: '#67211d'
  darker_primary: '#481614'
```

All three colors are expected to be approximately in the same shade, simply getting darker. They are expressed in hexadecimal value

## App Icon

If the user wishes, the icon for the app in the OS taskbar depending on the selected device. The path for this icon is specified in the field `app_icon_path`, which by default is relative to the root of where BirdWatch is located, if `app_icon_path_global` is used instead, the absolute path can be specified.

If no path is specified or if BirdWatch cannot find the specified icon, it will use a default white icon:

![Default White Logo](../resources/logos/White.png)