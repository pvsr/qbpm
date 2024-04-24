{
  description = "A tool for creating and managing qutebrowser profiles";

  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  inputs.flake-utils.url = "github:numtide/flake-utils";

  outputs = {
    self,
    nixpkgs,
    flake-utils,
  }:
    flake-utils.lib.eachDefaultSystem (
      system: let
        pkgs = nixpkgs.legacyPackages.${system};
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
      }
    );
}
