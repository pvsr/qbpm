{
  description = "Tool for creating, managing, and running qutebrowser profiles";

  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  inputs.pyproject-nix.url = "github:nix-community/pyproject.nix";
  inputs.pyproject-nix.inputs.nixpkgs.follows = "nixpkgs";
  inputs.pyproject-nix.inputs.treefmt-nix.follows = "treefmt-nix";
  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.treefmt-nix.url = "github:numtide/treefmt-nix";
  inputs.treefmt-nix.inputs.nixpkgs.follows = "nixpkgs";

  outputs =
    {
      self,
      nixpkgs,
      pyproject-nix,
      flake-utils,
      treefmt-nix,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        project = pyproject-nix.lib.project.loadPyproject { projectRoot = ./.; };
        treefmt = treefmt-nix.lib.evalModule pkgs {
          projectRootFile = "flake.nix";
          programs.mypy.enable = true;
          programs.mypy.directories."." = {
            modules = [
              "src/qbpm"
              "tests"
            ];
            extraPythonPackages = self.packages.${system}.default.propagatedBuildInputs;
          };
          programs.ruff.check = true;
          programs.ruff.format = true;
          programs.nixfmt.enable = true;
        };
        python = pkgs.python3;
        projectPackage =
          args:
          python.pkgs.buildPythonApplication (
            args // project.renderers.buildPythonPackage { inherit python; }
          );
        projectEnv =
          extraPackages:
          python.withPackages (project.renderers.withPackages { inherit python extraPackages; });
      in
      {
        packages.qbpm = projectPackage {
          nativeBuildInputs = [
            pkgs.scdoc
            pkgs.installShellFiles
          ];
          nativeCheckInputs = [ python.pkgs.pytestCheckHook ];
          postInstall = ''
            _QBPM_COMPLETE=bash_source $out/bin/qbpm > completions/qbpm.bash
            _QBPM_COMPLETE=zsh_source $out/bin/qbpm > completions/qbpm.zsh
            installShellCompletion completions/qbpm.{bash,zsh,fish}
            scdoc < qbpm.1.scd > qbpm.1
            installManPage qbpm.1
          '';
        };
        packages.default = self.packages.${system}.qbpm;
        apps.qbpm = flake-utils.lib.mkApp { drv = self.packages.${system}.qbpm; };
        apps.default = self.apps.${system}.qbpm;

        devShells.default = pkgs.mkShell {
          inputsFrom = [ treefmt.config.build.devShell ];
          buildInputs = [
            (projectEnv (
              ps: with ps; [
                pytest
                mypy
                pylsp-mypy
              ]
            ))
          ];
        };

        formatter = treefmt.config.build.wrapper;
        checks.formatting = treefmt.config.build.check self;
      }
    );
}
