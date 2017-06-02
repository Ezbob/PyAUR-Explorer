# Python AUR explorer

## What is this?
This a Arch User Repository explorer written in Python.
With this you can search for different packages located in the AUR.

### Python Version Compatibility
This explorer has recently been adjusted to target both Python 2.7 and Python 3.5 . 

## How-To

### Run it
To search for a package simply use the following command:
``` python pythur <package query>```

Where `<package query>` can be replace with the name of the package you're looking for.

### Get help
To get an overview over the options you can parse to the explorer:
```python pythur --help``` or
```python pythur -h ``` 
This will give you a short usage message.

## Dependencies
The following depedencies where used in this explorer:
- [Requests](http://docs.python-requests.org/en/master/) : A library for working with HTTP request on a high abstraction level
