{
  description = "A profile manager for qutebrowser";

  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  inputs.pyproject-nix.url = "github:nix-community/pyproject.nix";
  inputs.pyproject-nix.inputs.nixpkgs.follows = "nixpkgs";

  outputs =
    {
      self,
      nixpkgs,
      pyproject-nix,
    }:
    let
      pyproject = pyproject-nix.lib.project.loadPyproject { projectRoot = ./.; };
      pyprojectPackage =
        python: args:
        python.pkgs.buildPythonApplication (
          args // pyproject.renderers.buildPythonPackage { inherit python; }
        );
      pyprojectEnv =
        python: extraPackages:
        python.withPackages (pyproject.renderers.withPackages { inherit python extraPackages; });
      forAllSystems =
        mkOutputs:
        nixpkgs.lib.genAttrs [
          "aarch64-linux"
          "aarch64-darwin"
          "x86_64-darwin"
          "x86_64-linux"
        ] (system: mkOutputs nixpkgs.legacyPackages.${system});
    in
    {
      packages = forAllSystems (pkgs: {
        qbpm = pyprojectPackage pkgs.python3 {
          nativeBuildInputs = [
            pkgs.scdoc
            pkgs.installShellFiles
          ];
          nativeCheckInputs = [ pkgs.python3.pkgs.pytestCheckHook ];
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
        default = self.packages.${pkgs.system}.qbpm;
      });

      apps = forAllSystems (pkgs: {
        qbpm = {
          type = "app";
          program = pkgs.lib.getExe self.packages.${pkgs.system}.qbpm;
        };
        default = self.apps.${pkgs.system}.qbpm;
      });

      devShells = forAllSystems (pkgs: {
        default = pkgs.mkShell {
          packages = [
            pkgs.ruff
            pkgs.xdg-utils
            (pyprojectEnv pkgs.python3 (ps: [
              ps.flit
              ps.pytest
              ps.pytest-cov
              ps.mypy
              ps.pylsp-mypy
              ps.types-pillow
            ]))
          ];
        };
      });

      formatter = forAllSystems (
        pkgs:
        pkgs.nixfmt-tree.override {
          runtimeInputs = [ pkgs.ruff ];
          settings = {
            tree-root-file = "flake.nix";
            formatter.ruff = {
              command = "ruff";
              options = [ "format" ];
              includes = [ "*.py" ];
            };
          };
        }
      );
    };
}
