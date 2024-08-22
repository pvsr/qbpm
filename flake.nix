{
  description = "Tool for creating, managing, and running qutebrowser profiles";

  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.treefmt-nix.url = "github:numtide/treefmt-nix";
  inputs.treefmt-nix.inputs.nixpkgs.follows = "nixpkgs";

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
      treefmt-nix,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        treefmt = treefmt-nix.lib.evalModule pkgs {
          projectRootFile = "flake.nix";
          programs.mypy.enable = true;
          programs.mypy.directories."." = {
            modules = [
              "src/qbpm"
              "tests"
            ];
            extraPythonPackages = self.packages.x86_64-linux.default.propagatedBuildInputs;
          };
          programs.ruff.check = true;
          programs.ruff.format = true;
          programs.nixfmt-rfc-style.enable = true;
        };
        package = import ./. { inherit pkgs; };
        app = flake-utils.lib.mkApp { drv = package; };
      in
      {
        packages.qbpm = package;
        packages.default = package;
        apps.qbpm = app;
        apps.default = app;

        devShells.default = pkgs.mkShell {
          packages =
            with pkgs;
            [
              ruff
              (python3.withPackages (
                ps: with ps; [
                  pytest
                  mypy
                  pylsp-mypy
                  ruff-lsp
                ]
              ))
            ]
            ++ self.packages.${system}.default.propagatedBuildInputs;
        };
        formatter = treefmt.config.build.wrapper;
        checks.formatting = treefmt.config.build.check self;
      }
    );
}
