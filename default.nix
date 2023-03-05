{
  pkgs ? import <nixpkgs> {},
  python ? "python3",
  pythonPackages ? builtins.getAttr (python + "Packages") pkgs,
}:
with pythonPackages;
  buildPythonPackage rec {
    pname = "qbpm";
    version = "0.6";
    src = ./.;
    doCheck = true;
    SETUPTOOLS_SCM_PRETEND_VERSION = version;
    nativeBuildInputs = [pkgs.scdoc setuptools-scm];
    propagatedBuildInputs = [pyxdg click];
    checkInputs = [pytest];
    postInstall = ''
      mkdir -p $out/share/fish/vendor_completions.d
      cp completions/qbpm.fish $out/share/fish/vendor_completions.d/

      mkdir -p $out/share/man/man1
      scdoc < qbpm.1.scd > $out/share/man/man1/qbpm.1
    '';
  }
