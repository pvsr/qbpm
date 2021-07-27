{ pkgs ? import <nixpkgs> { }
, python ? "python3"
, pythonPackages ? builtins.getAttr (python + "Packages") pkgs
}:

with pythonPackages;
buildPythonPackage rec {
  pname = "qbpm";
  version = "0.4";
  src = ./.;
  doCheck = true;
  SETUPTOOLS_SCM_PRETEND_VERSION = version;
  nativeBuildInputs = [ setuptools-scm ];
  propagatedBuildInputs = [ pyxdg ];
  checkInputs = [ pytest ];
  postInstall = ''
    mkdir -p $out/share/fish/vendor_completions.d
    cp completions/qbpm.fish $out/share/fish/vendor_completions.d/
  '';
}
