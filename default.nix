{ pkgs ? import <nixpkgs> {}
, python ? "python3"
, pythonPackages ? builtins.getAttr (python + "Packages") pkgs }:

with pythonPackages;
buildPythonPackage rec {
  pname = "qpm";
  version = "0.1.0";
  src = ./.;
  doCheck = true;
  preCheck = ''
    export HOME=$PWD/test-home
  '';
  propagatedBuildInputs = [ pyxdg ];
  checkInputs = [ pytest ];
}
