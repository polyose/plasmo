This repo is under construction, come back later.

# Make your Repo Multicellular

| word | definition |
| :---- | :---------- |
| Plasmo**desmata** | (singular: plasmodesma) are microscopic channels which traverse the cell walls of adjacent plant cells, enabling transport and comunication between them. |
| `desmata` | is a python library (and cli command) for managing subsets of a git repository (and their dependencies) as if they were seperate cells. |
| `desmata.py` | conventionally defines a python module which inticates that its parent folder can be managed with `desmata`. |

## A Package Manager?

Desmata is not a package manager but it is **like** a package manager.
When you use desmata to add one or more "cells" to a project repo, you get something that is both more and less encapsulated than a typical package.


### More Encapsulated
Desmata cells rely on [nix](https://github.com/NixOS/nix) to handle their dependencies, so if you use it to add a cell to your repo, that cell's dependencies will be managed more completely than you might expect from something like `pip`.

### Less Encapsulated
Unlike `pip` or `poetry`, desmata cells are added directly to your repo so that you can easily make edits to them.

## Usage

This section TODO

## P2P Aspirations

Desmata represents a re-imagning of software packging, it asks:

>  Instead of worrying about the security, stability, or trustworthyness of 
>  high-value targets like Github and PyPI, what if we designed systems which 
>  have no high value targets?
>
>  What if all package consumers were one command away from being package
>  providers?

We know that this is possible in principle: biological cells manage it all of the time.
(Well ok, maybe trafficking software isn't quite the same trafficking solutes, but it still seems worth trying just the same.)

To put it differently:

Desmata aims to explore the consequences of chosing "partition tolerant" when confronted with the [CAP theorem](https://en.wikipedia.org/wiki/CAP_theorem).
It might be more difficult to build things like this, but if we can manage it we will end up with more reliable technology.

Despite these aspirations, there is nothing stopping you from pulling a desmata cell from Github, or writing one that depends on PyPI.
But if Desmata's design seems kind of strange, this is why.
