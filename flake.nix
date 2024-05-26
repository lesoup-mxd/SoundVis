{
 description = "A flake for my project";

 inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

 outputs = { self, nixpkgs }: {
    defaultPackage.x86_64-linux = with nixpkgs.legacyPackages.x86_64-linux; stdenv.mkDerivation {
      name = "my-project";
      buildInputs = [
        python312
        python312Packages.numpy
        python312Packages.scikit-learn
        python312Packages.opencv4
        python312Packages.pyserial
        python312Packages.tkinter
        python312Packages.pyaudio
        python312Packages.matplotlib
        python312Packages.pulsectl
        python312Packages.numba
        stdenv.cc.cc.lib
        tk
        portaudio
        mesa
        pulseaudio
      ];
      src = ./.;
    };
 };
}
