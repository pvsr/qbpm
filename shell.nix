{ pkgs ? import <nixpkgs> {}, ... }:
with pkgs;
mkShell {
  buildInputs = [
    (python3.withPackages (ps: with ps; [
      pyxdg
      setuptools-scm
      pytest
      pylint
      mypy
      black
    ]))
  ];
}
