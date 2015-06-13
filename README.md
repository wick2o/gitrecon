# gitrecon

gitrecon: Mass clone a GitHub user's repositories


### Dependencies

- Python 2.7+: gitpython, simplejson

- Python 2.6+: argparse, gitpython, simplejson

**Note:** This assumes you have git installed and that it be in your path.


### Usage arguments

```text
usage: gitrecon.py [-h] -u USERNAME [-t THREADS] [-d]

optional arguments:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        Github Username
  -t THREADS, --threads THREADS
                        Number of threads
  -d, --debug           Show debug messages
```


### Example usage

```bash
./gitrecon.py --username wick2o --threads 5
./gitrecon.py -u wick2o -t 5
```
