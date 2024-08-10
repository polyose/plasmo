{
  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryApplication;
        inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryEditablePackage;

        desmata = mkPoetryApplication { projectDir = ./.; };
        desmata-dev = mkPoetryEditablePackage {
          python = pkgs.python312;
          projectDir = ./.;
          editablePackageSources = {
            desmata = ./src;
          };
        };
      in
      {

        packages = {
          default = desmata;
        };

        devShells.default = pkgs.mkShell {
          inputsFrom = [ desmata desmata-dev ];
          packages = [ pkgs.nixpkgs-fmt ];
        };
      });
}
