{
  description = "A tool for creating and managing qutebrowser profiles";

  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.treefmt-nix.url = "github:numtide/treefmt-nix";
  inputs.treefmt-nix.inputs.nixpkgs.follows = "nixpkgs";

  outputs = {
    self,
    nixpkgs,
    flake-utils,
    treefmt-nix,
  }:
    flake-utils.lib.eachDefaultSystem (
      system: let
        pkgs = nixpkgs.legacyPackages.${system};
        treefmt = treefmt-nix.lib.evalModule pkgs {
          projectRootFile = "flake.nix";
          programs.mypy.enable = true;
          programs.mypy.directories."." = {
            modules = ["qbpm" "tests"];
            extraPythonPackages = with pkgs.python3.pkgs; [pyxdg click];
          };
          programs.ruff.check = true;
          programs.ruff.format = true;
          programs.alejandra.enable = true;
        };
      in rec {
        packages = flake-utils.lib.flattenTree rec {
          qbpm = import ./. {inherit pkgs;};
          default = qbpm;
        };
        apps = rec {
          qbpm = flake-utils.lib.mkApp {drv = packages.qbpm;};
          default = qbpm;
        };
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            ruff
            (python3.withPackages (ps:
              with ps; [
                pyxdg
                click

                pytest
                mypy
                pylsp-mypy
                ruff-lsp
              ]))
          ];
        };
        formatter = treefmt.config.build.wrapper;
        checks.formatting = treefmt.config.build.check self;
      }
    );
}
