{
  pkgs ? import <nixpkgs> { },
  python ? "python3",
  pythonPackages ? builtins.getAttr (python + "Packages") pkgs,
}:
with pythonPackages;
let
  pyproject = pkgs.lib.importTOML ./pyproject.toml;
in
buildPythonPackage rec {
  pname = pyproject.project.name;
  inherit (pyproject.project) version;
  src = ./.;
  format = "pyproject";
  nativeBuildInputs = [
    pkgs.scdoc
    pkgs.installShellFiles
    setuptools
  ];
  propagatedBuildInputs = [
    pyxdg
    click
  ];
  nativeCheckInputs = [ pytestCheckHook ];
  postInstall = ''
    _QBPM_COMPLETE=bash_source $out/bin/qbpm > completions/qbpm.bash
    _QBPM_COMPLETE=zsh_source $out/bin/qbpm > completions/qbpm.zsh
    installShellCompletion completions/qbpm.{bash,zsh,fish}

    scdoc < qbpm.1.scd > qbpm.1
    installManPage qbpm.1
  '';
}
