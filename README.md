# Desmata


...is under construction, everything below is a lie (for now).

## Handling dependencies so that the caller doesn't have to

One of Desmata's goals is to make it possible to write Python like its Unison.
The thing I like about Unison is that it resolves function implementations by cryptographic hash.
Here's how that looks with Desmata:

```
from desmata.get import from_hash
from desmata.interface import Cell
from typing import Callable

class Adder(Cell):
    add: Callable[[int, int], int]

adder = from_hash("QmWB61kWC2nCpq4XPU3rhtXRVbVUqgiR5V9198WvdNPjNu", interface=Arithmetic)

assert adder.add(1, 1) == 2
```

The implementation of `add` might be elsewhere on the LAN, or further away.
It may have non-python dependencies which are not installed.
Desmata provides a way to package code so that those details don't contribute to problems for the user.

It make take some time the first time you call into a cell because maybe Desmata nees to fetch the cell from far away.
And maybe Desmata has to build those dependencies (it wraps Nix for this).
But calls to `add` should be reasonably fast the second time and there after.

## A different approach to code collaboration

Desmata does not aim to compete with `git`.
It aims to compete with emailing code to your peers, or handing them a thumb drive.
Because lets face it, if software isn't your job, git is a bit much.

No branches, no merges, no globally meaningful name.
We're just moving payloads around by cryptographic hash.
All human readable names are local, which prevents leftpad-style skulduggery.

**Alice**
```
$ mkdir awesome-adder && cd awesome-adder
$ dsm init
$ # hackity hack
$ dsm publish
  using folder name as cell name: awesome-adder
  published cell: awesome-adder QmWBaeu6y1zEcKbsEqCuhuDHPL3W8pZouCPdafMCRCSUWk
$ dsm pubkey
    k51qzi5uqu5dlvj2baxnqndepeb86cbk3ng7n3i46uzyxzyqj2xjonzllnv0v8
```

> Hey Bob, I wrote a desmata cell for you.  It's called 'awesome-adder'.
> My public key is
>    `k51qzi5uqu5dlvj2baxnqndepeb86cbk3ng7n3i46uzyxzyqj2xjonzllnv0v8`

**Bob**
```
$ dsm peers add --name alice --pubkey k51qzi5uqu5dlvj2baxnqndepeb86cbk3ng7n3i46uzyxzyqj2xjonzllnv0v8
  alice
    awesome-adder QmWBaeu6y1zEcKbsEqCuhuDHPL3W8pZouCPdafMCRCSUWk
$ dsm clone alice.awesome-adder
$ cd alice.awesome-adder
$ # hackity hack
$ dsm publish
$ dsm self pubkey
    w22qzi5uqu5dlvj2baxnqndepeb86cbk3ng7n3i46uzyxzyqj2xjonzllnv1fF
 ```

> Thanks Alice, I made some changes
> My public key is `w22qzi5uqu5dlvj2baxnqndepeb86cbk3ng7n3i46uzyxzyqj2xjonzllnv1fF`

**Alice**
```
$ dsm peers add --name bob --pubkey w22qzi5uqu5dlvj2baxnqndepeb86cbk3ng7n3i46uzyxzyqj2xjonzllnv1fF
  bob
    awesome-adder Qm55aF6y1zEcKbsaaRUkk5w2L3W8pZjpPPdafMCRCSKkz
$ dsm clone bob.awesome-adder
$ diff alice.awesome-adder/somefile.py bob.awesome-adder/somefile.py
$ dsm publish 
  derived cell name from folder name: awesome-adder
  you already have a cell published under that name, overwrite Y/N?
    Y
  published cell: awesome-adder QmbWqxBEKC3P8tqsKc98xmWNzrzDtRLMiMPL8wBuTGsMnR
```
> Thanks Bob, I like your changes.
> I've updated my cell with them so that my other peers can see them too

### But I need branches and merges

If so, use git instead.
Or use git on the parent folder and desmata on a subfolder for each cell.

But consider that if your project has become so complex that it needs those things, then maybe it should be two projects.
I aspire towards cells that are so simple that a users can audit them.
If you need branches and merges, has your project become to complex for your users to trust?

### But I need globally meaningful names

Desmata's raison d'etre is to explore the possibility that we can get by without globally meaningful names.

People have been trusting other people for millenia.
People have been trusting domain names like `github.com` or `pypi.org` and package names like `leftpad` for decades.
We're good at the former, but when we try to do the latter we end up with **insecure**, **unreliable**, and **expensive** software.

Insecure because when a name is heavily relied on it becomes a high value target for corruption.
Unreliable because when its time to turn those names into bits, you might end up with different bits at different times (because maybe a server is down or maybe a solar flare destroyed the intenet).
Expensive because *since* you can't rely on a name *consistently* mapping to the same bits, you have to re-compute things today that you computed yesterday to be sure that something hasn't changed since then.

## Membranes and Nuclei, a different approach to software libraries

The files that compose a Desmata cell either belong to the **nucleus** or the **membrane** (don't worry, the biology metaphor pretty much stops there).
Nucleus files are expected to change infrequently, while people who copy a cell are encouraged to republish the cell with changes to its membrane.

```
$ dsm ls
  nucleus:
    cell.py
    flake.nix
    flake.lock
    app/

  membrane:
    config.txt
```

### For Users and Membrane Devs

#### Less to review

Users sometimes trust software without reviewing every line of code.
Maybe if they knew that 95% of the code had been scrutinized heavily by people they trust, they would consider reviewing the other 5% themselves before using it for anything important.
Desmata itself is not for code review, but it aims to associate code with a social graph in a way that will hopefully help make code review more effective.

#### Start from a working state, not a blank slate

When you install a library you end up with a blank slate.
You don't know if the library worked, and you now have to read the docs to figure out how to even start using it.
If that code is packaged in a cell instead, you can do this:

1. find the hash of its nucleus
2. find all cells with that nucleus
3. find one that resembles your use case
4. clone it locally

Now you've got something that runs.
You can prove to yourself that it works, and you can change it gradually--all the while continually proving to yourself that it still works.
I think this is a friendlier way than having every user's first experience be a blank slate.

#### Find usage examples among your peers

If your developing a membrane and you need to call a function in a commonly-used nucleus, you can look to other membranes that use that nucleus for inspiration.

### For Nucleus Devs

#### See who is using your code, and how

When a program depends on a traditional library, it's a relationship that only shows up in one direction.
Anybody viewing the code for the program can see its dependencies, but there's no way for a library viewer to find the programs that depend on it.

Desmata encodes the relationship so that it's queryable in both directions.
So rather than assuming that a certain change will be a breaking one, you can go see whether it actually will be.







