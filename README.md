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

### Configuration
A configuration file called 'config.ini' is included in the repo. This configuration file governs the urls and database locations used by Pythur, when exploring the AUR. The configuration mechanism looks for the 'config.ini' file in both the current directory and in the user wide configuration folder of '~/USER/.config/pythur/', if this exists.

## Dependencies
The following depedencies where used in this explorer:
- [Requests](http://docs.python-requests.org/en/master/) : A library for working with HTTP request on a high abstraction level
- configparser : A library for parsing .ini configuration files
