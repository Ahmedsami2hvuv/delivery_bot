# الملف: .railway/nix/flake.nix

{
  description = "A flake for Railway";

  inputs = {
    nixpkgs.url = "github.com/nixos/nixpkgs/nixos-23.05";
  };

  outputs = { self, nixpkgs }: {
    packages.x86_64-linux.default = nixpkgs.legacyPackages.x86_64-linux.stdenv.mkDerivation {
      name = "my-packages";
      buildInputs = [
        nixpkgs.legacyPackages.x86_64-linux.google-chrome
      ];
      src = ./.;
      installPhase = ''
        mkdir -p $out/bin
      '';
    };
  };
}
