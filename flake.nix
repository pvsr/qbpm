{
  description = "A tool for creating and managing qutebrowser profiles";

  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.pre-commit-hooks.url = "github:cachix/pre-commit-hooks.nix";

  outputs = {
    self,
    nixpkgs,
    flake-utils,
    pre-commit-hooks,
  }:
    flake-utils.lib.eachDefaultSystem (
      system: let
        pkgs = nixpkgs.legacyPackages.${system};
        mkDevShell = args:
          pkgs.mkShell (args
            // {
              buildInputs = [
                (pkgs.python3.withPackages (ps:
                  with ps; [
                    pyxdg
                    setuptools-scm
                    pytest
                    pylint
                    mypy
                    black
                  ]))
              ];
            });
      in rec {
        packages = flake-utils.lib.flattenTree rec {
          qbpm = import ./. {inherit pkgs;};
          default = qbpm;
        };
        apps = rec {
          qbpm = flake-utils.lib.mkApp {drv = packages.qbpm;};
          default = qbpm;
        };
        devShells.ci = mkDevShell {};
        devShells.default = mkDevShell {
          inherit (self.checks.${system}.pre-commit-check) shellHook;
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
            };
          };
        };
      }
    );
}
