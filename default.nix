{ pkgs ? import <nixpkgs> {}
, python ? "python3"
, pythonPackages ? builtins.getAttr (python + "Packages") pkgs }:

with pythonPackages;
buildPythonPackage rec {
  pname = "qbpm";
  version = "0.3";
  src = ./.;
  doCheck = true;
  propagatedBuildInputs = [ pyxdg ];
  checkInputs = [ pytest ];
}
