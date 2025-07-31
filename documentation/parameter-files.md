The Parameter files refer to the ones in the target device's workspace, not specific to the GUI itself, and they are expected to be `.yaml` files.

## Default and Current Files

It is expected to be two sets of files:
- default files (with default parameters)
- current files (with current parameter)

the path for the current parameters is expected to be specified in the [target device configuration file](target-device-config.md), and the default parameters are assumed to be in a `default` folder inside it.

If the `default` folder does not exist there, it is created and a copy of all current parameter files is generated inside.

If any file is present among the current and not in the defaults, it is copied to the defaults, and the analogous if a file is present among the defaults and not the current.

## Possible values

### Numeric value

It is possible to directly have numeric values like
```yaml
single_int: 1535
```
though if they are modified via the GUI they would be rewritten as
```yaml
single_int: '1535'
```

### Strings

Strings can be written plainly like
```yaml
single_string: Hello World!
```

### Parent parameter

The value of a parameter could be other parameters, like
```yaml
recursive:
  single_int: 235
  single_string: Goodbye
```

### List

Each element of the list can be any of the types mentioned above, like
```yaml
array_int:
- 10
- 20
- 30
array_string:
- fist
- second
- third
```
Or it could directly have subparameters, like
```yaml
array_struct:
- string: ten
  number: 10
- string: twenty
  number: 20
- string: thirty
  number: 30
```

### Example

The following is an example of the types and combinations that could exist in a parameters file
```yaml
single_string: Hello World!
single_int: 1535
array_string:
- fist
- second
- third
recursive:
  single_int: 235
  single_string: Goodbye
  double_recursive:
    some_list:
    - alpha
    - beta
    some_value_again: 4929
array_struct:
- string: ten
  number: 10
- string: twenty
  number: 20
- string: thirty
  number: 30
```

## No Comments

It is important to know, that even though the files can contain comments, if the file is ever modified in BirdWatch, these comments will be lost (all the comments in that file).