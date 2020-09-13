with import <nixpkgs> {};

mkShell {
  buildInputs = [
    (python3.withPackages (ps: with ps; [
      pyxdg
      pytest
      pylint
      mypy
      black
    ]))
  ];
}
