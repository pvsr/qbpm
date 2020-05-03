with import <nixpkgs> {};

python3.pkgs.buildPythonPackage rec {
  pname = "qpm";
  version = "0.1.0";
  src = ./.;
  doCheck = false;
  propagatedBuildInputs = [ python3.pkgs.pyxdg ];
}
