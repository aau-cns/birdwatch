The Nodes file contains a description of what to execute when launching the mission.
When the mission is launched, a tmux session named "BirdWatch" will be created in the target device, windows will be created inside it, and then each node in that window will be executed in a different pane.

A node is specified in the Nodes file like follows
```yaml
NodeName:
  run: true/false
  order: '1'
  command: command to run
  delay_ms: '100'
  window: 'name of tmux window'
```

- `NodeName` is the name with which it will be shown in the GUI
- `run` indicates wether to run or not the node. If the field is not present, it will be considered `true`
- `order` is the order in the sequence of all nodes in which it will be executed. If two or more nodes have the same `order` they will be executed in the order they appear in the file
- `command` is the command to run in the tmux pane
- `delay_ms` is the time in milliseconds to wait after executing the command before continuing with next node. This parameter is optional, if `delay_ms` is not present, there will be no delay after executing the node
- `window` is the name of the tmux window in which the node will be executed

## Example
```yaml
Operator:
  run: true
  order: '1'
  command: ros2 run operator operator.py
  window: operator
Supervisor:
  run: true
  order: '2'
  command: ros2 run supervisor supervisor.py
  delay_ms: '100'
  window: estimation
Estimator:
  order: '3'
  command: ros2 run estimator estimator.py
  window: estimation
```

The tmux session created from this will have the following structure
```
Session "BirdWatch"
    ├── Window "operator"
    │   └── Node "Operator"
    └── Window "estimation"
        ├── Node "Supervisor"
        └── Node "Estimator"
```

And the order of things to happen will be:
1. Creates tmux session "BirdWatch" in target device
2. Renames the default window to "operator"
3. Executes `ros2 run operator operator.py` in that window
4. Creates a new window and calls it "estimation"
5. Executes `ros2 run supervisor supervisor.py` in that window
6. Waits 100 milliseconds
7. Creates a new pane in the window "estimation"
8. Executes `ros2 run estimator estimator.py` in the new pane

If a `source` was specified for the target device (see [Target Device Configuration](target-device-config.md)), it will be sourced before running each node.