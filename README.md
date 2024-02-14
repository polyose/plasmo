Desmata is under construction, come back later.

<img src='banner.png' width='800'>

# Make your Repo Multicellular

| word | definition |
| :---- | :---------- |
| Plasmo**desmata** | (singular: plasmodesma) are microscopic channels which traverse the cell walls of adjacent plant cells, enabling transport and comunication between them. |
| `desmata` | is a python library (and cli command) for managing subsets of a git repository (and their dependencies) as if they were seperate cells. |
| `desmata.py` | conventionally defines a python module which inticates that its parent folder can be managed with `desmata`, these are typically found near a `flake.nix` and a `flake.lock`. |


## A Package Manager?

Desmata is at least **like** a package manager.
When you use desmata to add one or more "cells" to a project repo, you get something that is both more and less encapsulated than a typical package.

### More Encapsulated
Desmata cells rely on [nix](https://github.com/NixOS/nix) to handle their dependencies, so if you use it to add a cell to your repo, that cell's dependencies will be managed more completely than you might expect from something like `pip`.

### Less Encapsulated
Unlike `pip` or `poetry`, desmata cells are moved in and out of repo's not as a references, but as a bunch of code.
This makes it easier to edit their contents to suit your needs.

Users who have needs similar to you may prefer to gat the modified cell from your repo, rather than make similar edits themselves.
In this way, Desmata hopes to achieve a sort of evolution and specialization of the cells that it manages.

### What Kind of Packages?

It would be strange to use Desmata to add a purely python cell to your purely python project.
Python already has good ways to compose such things.

It is for providing pythonic access to nonpythonic things so that your still looks and feels like a python project.

### Must it be Python?

No, that's just what's familliar to me.
If it works well, we can implement the same pattern in whatever language.

## Usage

This section TODO

## P2P Aspirations

Desmata represents a re-imagning of software packging, it asks:

>  Instead of worrying about the security, stability, or trustworthyness of 
>  high-value targets like Github and PyPI, what if our systems had no high
>  value targets?

We know that this is possible in principle: biological cells achieve remarkable feats of coordination by depending on inputs from only their neighbors.
(Well ok, maybe trafficking software isn't quite the same trafficking solutes, but it still seems worth trying just the same.)

To put it differently:

Desmata aims to explore the consequences of chosing "partition tolerant" when confronted with the [CAP theorem](https://en.wikipedia.org/wiki/CAP_theorem).
It might be more difficult to build things this way, but if we can manage it then we will have more resilient technology.

Despite these aspirations, there is nothing stopping you from pulling a desmata cell from Github, or writing one that depends on PyPI.
But if Desmata's design seems kind of strange in places, this is why.
