{
  description = "A tool for creating and managing qutebrowser profiles";

  inputs.flake-utils.url = "github:numtide/flake-utils";

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let pkgs = nixpkgs.legacyPackages.${system}; in
      rec {
        packages = flake-utils.lib.flattenTree {
          qbpm = import ./. { inherit pkgs; };
        };
        defaultPackage = packages.qbpm;
        apps.qbpm = flake-utils.lib.mkApp { drv = packages.qbpm; };
        defaultApp = apps.qbpm;
        devShell = import ./shell.nix { inherit pkgs; };
      }
    );
}
