{
  description = "A tool for creating and managing qutebrowser profiles";

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    pre-commit-hooks.url = "github:cachix/pre-commit-hooks.nix";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
    pre-commit-hooks,
  }:
    flake-utils.lib.eachDefaultSystem (
      system: let
        pkgs = nixpkgs.legacyPackages.${system};
        devEnv = pkgs.poetry2nix.mkPoetryEnv {
          projectDir = ./.;
          preferWheels = true;
        };
      in rec {
        packages = flake-utils.lib.flattenTree rec {
          qbpm = pkgs.poetry2nix.mkPoetryApplication {
            projectDir = ./.;
            preferWheels = true;
          };
          default = qbpm;
        };
        apps = rec {
          qbpm = flake-utils.lib.mkApp {
            drv = packages.default;
          };
          default = qbpm;
        };
        devShells.default = pkgs.mkShell {
          inherit (self.checks.${system}.pre-commit-check) shellHook;
          buildInputs = [
            pkgs.python3Packages.poetry
            devEnv
          ];
        };

        checks = {
          pre-commit-check = pre-commit-hooks.lib.${system}.run {
            src = ./.;
            hooks = {
              alejandra.enable = true;
              deadnix.enable = true;
              statix.enable = true;

              black.enable = true;
              isort.enable = true;
              pylint.enable = true;
            };
          };
        };
      }
    );
}
