{
  description = "A profile manager for qutebrowser";

  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  inputs.pyproject-nix.url = "github:nix-community/pyproject.nix";
  inputs.pyproject-nix.inputs.nixpkgs.follows = "nixpkgs";
  inputs.flake-utils.url = "github:numtide/flake-utils";

  outputs =
    {
      self,
      nixpkgs,
      pyproject-nix,
      flake-utils,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        pyproject = pyproject-nix.lib.project.loadPyproject { projectRoot = ./.; };
        python = pkgs.python3;
        pyprojectPackage =
          args:
          python.pkgs.buildPythonApplication (
            args // pyproject.renderers.buildPythonPackage { inherit python; }
          );
        pyprojectEnv =
          extraPackages:
          python.withPackages (pyproject.renderers.withPackages { inherit python extraPackages; });
      in
      {
        packages.qbpm = pyprojectPackage {
          nativeBuildInputs = [
            pkgs.scdoc
            pkgs.installShellFiles
          ];
          nativeCheckInputs = [ python.pkgs.pytestCheckHook ];
          postInstallCheck = "$out/bin/qbpm --help";
          postInstall = ''
            _QBPM_COMPLETE=bash_source $out/bin/qbpm > completions/qbpm.bash
            _QBPM_COMPLETE=zsh_source $out/bin/qbpm > completions/qbpm.zsh
            installShellCompletion completions/qbpm.{bash,zsh,fish}
            scdoc < qbpm.1.scd > qbpm.1
            installManPage qbpm.1
          '';

          meta = {
            homepage = "https://github.com/pvsr/qbpm";
            changelog = "https://github.com/pvsr/qbpm/blob/main/CHANGELOG.md";
            description = "A profile manager for qutebrowser";
            license = pkgs.lib.licenses.gpl3Plus;
          };
        };
        packages.default = self.packages.${system}.qbpm;
        apps.qbpm = flake-utils.lib.mkApp { drv = self.packages.${system}.qbpm; };
        apps.default = self.apps.${system}.qbpm;

        devShells.default = pkgs.mkShell {
          packages = [
            pkgs.ruff
            (pyprojectEnv (
              ps: with ps; [
                flit
                pytest
                mypy
                pylsp-mypy
              ]
            ))
          ];
        };

        formatter = pkgs.nixfmt-tree.override {
          runtimeInputs = [ pkgs.ruff ];
          settings = {
            tree-root-file = "flake.nix";
            formatter.ruff = {
              command = "ruff";
              options = [ "format" ];
              includes = [ "*.py" ];
            };
          };
        };
      }
    );
}
