![version](https://img.shields.io/pypi/v/wordz) ![pyversions](https://img.shields.io/pypi/pyversions/wordz) ![license](https://img.shields.io/pypi/l/wordz) ![status](https://img.shields.io/pypi/status/wordz)

# wordz

> Wordlists builder

## Introduction

This tool evolved from the helper scripts used for the [brutas](https://github.com/tasooshi/brutas/) project. It is used for generating and managing wordlists for password cracking, content discovery, fuzzing etc.

## Requirements

* GNU/Linux, macOS
* `hashcat`
* `hashcat-utils`
* GNU tools: `cat`, `awk`, `comm`, `sort`, `uniq`

## Usage

### Sources

Let's say you have some `tests/data/keywords.txt` like the following:

```
acapulco
cerveja
```

Also, you know of a few common suffixes (`tests/data/bits.txt`) used in this particular case, namely:

```
!
123
```

We would use a modest set of Hashcat rules (`tests/data/hashcat.rule`): one that simply passes a keyword, and the other one that makes it upper case. Like these:

```
:
u
```

### Classes

Now it's time to design a class that will build the wordlist for us according to some requirements, e.g.:
* bits after each keyword
* bits before each keyword
* and on both sides of a keyword

```
from wordz import Combinator


class Passwords(Combinator):

    wordlists = (
        'data/keywords.txt',
    )
    rules = (
        'data/hashcat.rule',
    )

    def process(self):

        self.merge(
            self.output('passwords.txt'),
            (
                self.right(self.temp('hashcat-data-keywords.txt'), self.base('data/bits.txt')),
                self.left(self.temp('hashcat-data-keywords.txt'), self.base('data/bits.txt')),
                self.both(self.temp('hashcat-data-keywords.txt'), self.base('data/bits.txt')),
            )
        )
```

What happens in the background is that `wordz` takes all `wordlists` defined on the class level and parses them using `rules`. It is done with the `setup` method which is launched before `process`, and which you can override with your own logic (however, you will probably want to keep `self.wordlists_process()` in there).

This is how we know the name of the file in the temporary directory: it is composed of the name of the rule (`hashcat`), the name of the parent directory (`data`) and name of the keywords file without extension (`keywords`).

There are three "shortcuts" for directories available in each `Combinator` instance: `base()`, `temp()` and `output()`.

### Building

Now it's time to build our lists:

```
$ mkdir tmp
$ wordz -p data/classes.py::Passwords
```

The result should now be in `passwords.txt`.

### Advanced usage

If you want to see how it is used in more advanced cases, have a look into [tests](https://github.com/tasooshi/wordz/tree/main/tests) or the [brutas](https://github.com/tasooshi/brutas/) project.

## Command line

Once installed, you can call `wordz` from the command line. Here are the arguments you can use:

```
usage: wordz [-h] -p PATH [-b BASE_DIR] [-t TEMP_DIR] [-o OUTPUT_DIR] [-v] [--min-length MIN_LENGTH] [--cores CORES] [--memory MEMORY] [--bin-hashcat BIN_HASHCAT] [--bin-combinator BIN_COMBINATOR] [--bin-rli2 BIN_RLI2] [-d | -q]

options:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  Class path (e.g. classes/passwords.py::ExtraPasswords)
  -b BASE_DIR, --base-dir BASE_DIR
                        Base directory path (default: .)
  -t TEMP_DIR, --temp-dir TEMP_DIR
                        Temporary directory path (default: tmp)
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Output directory path (default: .)
  -v, --version         Print version
  --min-length MIN_LENGTH
                        Minimal length for a password when merging lists (default: 4)
  --cores CORES         Number of cores to be used for sorting (default: CPUs-based)
  --memory MEMORY       Percentage of memory to be used for sorting (default: 80%)
  --bin-hashcat BIN_HASHCAT
                        Hashcat binary (default: hashcat)
  --bin-combinator BIN_COMBINATOR
                        Hashcat utils `combinator` binary (default: combinator.bin)
  --bin-rli2 BIN_RLI2   Hashcat utils `rli2` binary (default: rli2.bin)
  -d, --debug           Debug mode
  -q, --quiet           Quiet mode
```