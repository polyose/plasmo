from pathlib import Path
import logging
import inspect

from injector import Injector, Module, provider, singleton
from dataclasses import dataclass
from typing import TypeVar, Generic, Type, Dict

from desmata.tool import Tool
from desmata.nix import Nix

# The interface I'm working on



class Loggers:
    msg: logging.Logger
    proc: logging.Logger

    def __init__(self) -> None:
        self.msg = logging.getLogger("msg")
        self.proc = logging.getLogger("proc")

@dataclass
class Dependency:
    id: str

    def __init__(self, package_name: str, loggers: Loggers) -> None:
        loggers.msg.info(f"hi from {self.__class__.__name__}, a user-defined subclass of Dependency")
        loggers.proc.info(f"installing {package_name}")
        self.id = package_name + "id"

@dataclass
class Closure:
    cell_name: str
    dependencies: list[Dependency]

    def __init__(self, cell_name: str, loggers: Loggers):
        loggers.msg.info(f"hi from {self.__class__.__name__}, a user-defined subclass of Closure")
        self.cell_name = cell_name
        self.loggers = loggers

        # detect dependencies based on type hints and set them as attributes
        for name, Dep in self.__annotations__.items():
            if issubclass(Dep, Dependency):
                setattr(self, name, Dep(package_name=name, loggers=loggers))

SpecificClosure = TypeVar("SpecificClosure", bound=Closure)

class Cell(Generic[SpecificClosure]):
    ClosureClass: Type[SpecificClosure]
    closure: SpecificClosure

    def __init_subclass__(cls, closure_class: Type[SpecificClosure]):
        cls.ClosureClass = closure_class

    def __init__(self, loggers: Loggers):
        loggers.msg.info(f"hi from {self.__class__.__name__}, a user-defined subclass of Cell")
        cell_name = Path(inspect.getfile(self.__class__)).name
        self.closure = self.ClosureClass(cell_name=cell_name, loggers=loggers)
        self.initialize_dependencies()

    def initialize_dependencies(self):
        for name in self.closure.__annotations__:
            setattr(self, name, getattr(self.closure, name))

### Utility Functions

def create_provider(cls: Type, dependencies: list):
    @singleton
    @provider
    def provide(instance: Injector) -> cls:
        args = {dep.__name__.lower(): instance.get(dep) for dep in dependencies}
        return cls(**args)
    return provide

def register_classes(cell_cls: Type[Cell], closure_cls: Type[Closure], dependency_cls_dict: Dict[str, Type[Dependency]]):
    providers = []

    # Register dependencies
    for dep_name, dep_cls in dependency_cls_dict.items():
        dependencies = [Loggers]  # Assuming dependencies only need Loggers
        providers.append(create_provider(dep_cls, dependencies))

    # Register closure
    closure_dependencies = [Loggers]
    providers.append(create_provider(closure_cls, closure_dependencies))

    # Register cell
    cell_dependencies = [Loggers]
    providers.append(create_provider(cell_cls, cell_dependencies))

    return DynamicModule(providers)

class DynamicModule(Module):
    def __init__(self, providers):
        self.providers = providers

    def configure(self, binder):
        for _provider in self.providers:
            binder.bind(_provider.__annotations__['return'], to=_provider, scope=singleton)

def construct_cell(injector: Injector, cell_cls: Type[Cell]) -> Cell:
    return injector.get(cell_cls)

### User defined classes

class Git(Dependency, Tool):
    def __init__(self, package_name: str, loggers: Loggers):
        Dependency.__init__(self, package_name=package_name, loggers=loggers)
        Tool.__init__(self, name="git", path=Path("/home/matt/.nix-profile/bin/git"), env_filter=lambda _: {}, log=loggers.proc.getChild("git"))

class BuiltinsClosure(Closure):
    "handles which files are needed to run git"
    git: Git

class DesmataBuiltins(Cell, closure_class=BuiltinsClosure):
    "wraps functions which can be called to use git"
    git: Git

### Test Code

def test_get_builtins():
    # Define user classes
    cell_cls = DesmataBuiltins
    closure_cls = BuiltinsClosure
    dependency_cls_dict = {
        "git": Git,
    }

    # Register classes with Injector
    dynamic_module = register_classes(cell_cls, closure_cls, dependency_cls_dict)
    injector = Injector([dynamic_module])

    # Create a DesmataBuiltins cell
    builtins = construct_cell(injector, cell_cls)

    # Call `builtins.git("version")` and check the result
    result = builtins.git("version")
    print(result)
    assert "2" in result

if __name__ == "__main__":
    test_get_builtins()
