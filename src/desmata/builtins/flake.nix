{
  description = "Non-python dependencies of desmata itself";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    { self
    , nixpkgs
    , flake-utils
    }:
    flake-utils.lib.eachDefaultSystem (system:
    let
      pkgs = import nixpkgs {
        inherit system;
      };
    in
    {
      packages = {
        ipfs = pkgs.kubo;
        git = pkgs.git;
      };

      devShells.default = pkgs.mkShell {
        packages = with pkgs; [ kubo git ];
      };

    });
}
