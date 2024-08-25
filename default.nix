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
    setuptools
  ];
  propagatedBuildInputs = [
    pyxdg
    click
  ];
  nativeCheckInputs = [ pytestCheckHook ];
  postInstall = ''
    install -D -m644 completions/qbpm.fish $out/share/fish/vendor_completions.d/qbpm.fish

    install -vd $out/share/{bash-completion/completions,zsh/site-functions}
    _QBPM_COMPLETE=bash_source $out/bin/qbpm > $out/share/bash-completion/completions/qbpm
    _QBPM_COMPLETE=zsh_source $out/bin/qbpm > $out/share/zsh/site-functions/qbpm

    mkdir -p $out/share/man/man1
    scdoc < qbpm.1.scd > $out/share/man/man1/qbpm.1
  '';
}
