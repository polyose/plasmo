{
  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:nixos/nixpkgs?ref=23.11";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    pre-commit-hooks.url = "github:cachix/pre-commit-hooks.nix";
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix, pre-commit-hooks }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; })
          mkPoetryApplication;
        pkgs = import nixpkgs { inherit system; };

        desmata-poetry = mkPoetryApplication { projectDir = ./.; };

        build-docs-script = pkgs.writeShellScriptBin "build-docs" ''
          expect="$PWD/src/desmata/__init__.py"
          from="$PWD/src/desmata"
          to="$PWD/docs"
          if [ ! -f $expect ]
          then
              echo "$expect not found, are you running this from the desmata repo root?"
              exit 1
          fi
          if [ ! -d $to ]
          then
              echo "$to is not a directory, are you running this from the desmata repo root?"
              exit 1
          fi

          echo building docs based on $from
          echo putting them in $to
          ${desmata-poetry.dependencyEnv}/bin/pdoc src/desmata -o docs
        '';
      in
      {

        checks = {
          pre-commit-check = pre-commit-hooks.lib.${system}.run {
            src = ./.;
            hooks = {
              nixpkgs-fmt.enable = true;
            };
          };
        };

        apps = rec {
          desmata = {
            type = "app";
            program = "${desmata-poetry}/bin/desmata";
          };

          dsm = {
            type = "app";
            program = "${desmata-poetry}/bin/desmata";
          };

          build-docs = {
            type = "app";
            program = "${build-docs-script}/bin/build-docs";
          };

          default = desmata;
        };

        packages = rec {
          desmata = desmata-poetry;
          default = desmata;
        };

        devShells.default = pkgs.mkShell {
          inputsFrom = [ desmata-poetry ];
          packages = [
            pkgs.just
            pkgs.poetry
            pkgs.python311Packages.pylsp-mypy
          ];
          inherit (self.checks.${system}.pre-commit-check) shellHook;

        };
      });
}
