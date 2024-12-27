from logging import Logger
import json
from pathlib import Path
from typing import cast, Iterator
from collections import deque

from desmata.tool import Cmd, MajorMinorPatch, Tool
from desmata.messages import NixPathInfo

from dataclasses import dataclass

@dataclass
class NixDependencyTree:
    size: int
    info: NixPathInfo
    immediate_dependencies: list['NixDependencyTree']

class Nix(Tool):
    _version: MajorMinorPatch | None = None
    _flakes_enabled: bool | None = None

    def __init__(self, cwd: Path, log: Logger):
        def flakes_and_cmd(cmd: Cmd) -> Cmd:
            return [
                *["--extra-experimental-features", "nix-command"],
                *["--extra-experimental-features", "flakes"],
                *cmd,
            ]

        super().__init__(name="nix", cmd_filter=flakes_and_cmd, cwd=cwd, log=log.getChild("nix"))

    def build(
        self, output_name: str
    ) -> tuple[Path, list[NixPathInfo]]:
        path_str = self(
                    "build",
                    f".#{output_name}",
                    "--print-out-paths",
                    "--no-link",
                ).strip()
        dependency_info: list[NixPathInfo] = []
        for info_str in json.loads(self("path-info", "--json", "-r", path_str)):
            info = NixPathInfo.model_validate(info_str)
            dependency_info.append(info)
        return Path(path_str), dependency_info
            


    def get_nar_sha256_hex(self, path: Path) -> str:
        raise NotImplementedError()

    @property
    def version(self) -> MajorMinorPatch:
        if not Nix._version:
            Nix._version = cast(
                MajorMinorPatch,
                tuple(map(int, self("--version").split(" ")[-1].split("."))),
            )
        return Nix._version

    def check(self) -> None:
        min_ver = (2, 0, 0)
        if not min_ver <= self.version:
            raise EnvironmentError(f"{self.name} is at {self.version} but {min_ver} is required")

    @staticmethod
    def get_id(path: Path) -> str:
        return path.replace("/nix/store", "")


    @staticmethod
    def dep_dags(info: list[NixPathInfo], root_path: str) -> Iterator[NixDependencyTree]:
        path_infos: dict[str, NixPathInfo] = {x.path : x for x in info}
        built_trees: dict[str, NixDependencyTree] = {}
        to_process = deque([(root_path, 0)])  # (path, depth)
        seen = set()

        while to_process:
            current_path, depth = to_process.popleft()

            if current_path in seen:
                continue

            seen.add(current_path)
            info = path_infos[current_path]

            # Queue up the next level of dependencies
            for ref in info.references:
                if ref in path_infos and ref not in seen:
                    to_process.append((ref, depth + 1))

            # Build current node with whatever dependencies we've built so far
            deps = [
                built_trees[ref] 
                for ref in info.references 
                if ref in path_infos and ref in built_trees
            ]

            # Calculate total size recursively - include current node (1) plus all dependencies
            total_size = 1 + sum(dep.size for dep in deps)

            tree = NixDependencyTree(
                size=total_size,
                info=info,
                immediate_dependencies=deps
            )
            built_trees[current_path] = tree

            # Yield the current state of the root tree
            yield built_trees[root_path]

