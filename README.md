Desmata is under construction, come back later.

<img src='banner.png' width='800'>

# Make Your Repo Multicellular

| word | definition |
| :---- | :---------- |
| Plasmo**desmata** | (singular: plasmodesma) are microscopic channels which traverse the walls of adjacent plant cells, enabling transport and comunication between them. |
| `desmata` | is a python library (and cli command) for managing subsets of a git repository (and their dependencies) as if they were seperate cells. |

Desmata lets users create and share "cells", which are pythonic interfaces into [Nix](https://github.com/NixOS/nix)-managed environments.
Creating a cell requires some nix understanding, but using one only [requires that nix be installled](https://determinate.systems/posts/determinate-nix-installer).

## Usage

### Adding a cell

Use `desmata add` to refer to a cell in another repo, and tell it where to put the cell in your repo:
```
$ tree
  .
  ├── .git
  ├── ...
  └── test
      └── test_foo.py

$ pip install desmata
$ desmata add github.com/polyose/samples --remote-cell ./postgres --local-cell ./test/pg
$ tree
  .
  ├── .git
  ├── ...
  └── test
      ├── pg
      │   ├── desmata.py
      │   ├── flake.lock
      │   └── flake.nix
      └── test_foo.py
```

Your interface to the contents of the newly added cell will be in `desmata.py`.

```python3
# test_foo.py
from .pg.desmata import Postgres
def test_pg():
    c = Postgres.get_connection()
    ...
```

This example does not use your system's postgres, rather it uses the contents of `flake.nix` and `flake.lock` to build (or download) one for this project.
This gives you stronger guarantees that all users of your project get the same version of postgres, while still ensuring that users on different architectures get something that works.

Desmata intends to provide strong encapsulation where it counts (that's Nix's job), while also remaining quite permiable.
That's why you end up with new files in your repo: you may want to to edit these to specialize the cell to meet your needs.
Later, other users with similar needs may want to add a cell based on your changes (this is how cells evolve). 

### Writing a cell

This section is TODO, summary: implement the `Desma` abstract base class in `desmata.py`.

## P2P Aspirations

Desmata asks:

>  Instead of worrying about the security, stability, or trustworthyness of 
>  high-value targets like Github and PyPI, what if our systems had no high
>  value targets at all?

That is, Desmata aims to explore the consequences of chosing "partition tolerant" when confronted with the [CAP theorem](https://en.wikipedia.org/wiki/CAP_theorem).
It might be more difficult to build things this way, but if we can manage it, then we will have more resilient technology.

This is the logical space in which biological cells operate, and they achieve astounding feats of coordination (and with not even one widespread outage for billions of years).
Desmata wants to make the same possible for software.

Despite these aspirations, there is nothing stopping you from pulling a desmata cell from Github, or writing one that depends on PyPI.
Just know that if Desmata's design seems kind of strange in places, it is probably because compromises were made in support of this dream.
