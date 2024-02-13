{
  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:nixos/nixpkgs?ref=23.11";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; })
          mkPoetryApplication;
        pkgs = import nixpkgs { inherit system; };
      in rec {

        medina-poetry = mkPoetryApplication{ projectDir = ./.; };

        apps = rec {
          medina = {
            type="app";
            program="${medina}/bin/medina";
          };
          default = medina;
        };

        devShells.default = pkgs.mkShell {
          inputsFrom = [ medina-poetry ];
          packages = [
            pkgs.poetry
            pkgs.python311Packages.pylsp-mypy
          ];
        };
      });
}
