let inputs = import ./nix/tamal { }; in
{ pkgs ? import inputs.nixpkgs { } }:

let
  inherit (pkgs) lib;

  src = lib.cleanSourceWith {
    src = lib.cleanSource ./.;
    filter = path: _type: !(
      lib.hasSuffix ".nix" path
      || lib.hasSuffix ".md" path
      || lib.hasSuffix ".kdl" path
      || path == toString ./nix/tamal/lock.json
    );
  };

  treefmt-check =
    let
      treefmt = (import inputs.treefmt).evalModule pkgs {
        projectRootFile = "default.nix";
        programs = {
          nixpkgs-fmt.enable = true;
          black.enable = true;
          prettier.enable = true;
        };
        settings.formatter.prettier.excludes = [ "nix/tamal/lock.json" ];
      };
    in
    treefmt.config.build.check ./.;

  kasane-generate = pkgs.writeShellApplication {
    name = "kasane-generate";
    runtimeInputs = with pkgs; [ python3 prettier ];
    text = ''
      python3 scripts/gen_gamma.py
      python3 scripts/gen_palettes.py
      python3 scripts/build_palette_docs.py
      prettier --write docs/*.html
    '';
  };

  kasane = pkgs.stdenvNoCC.mkDerivation {
    name = "kasane";
    inherit src;

    nativeBuildInputs = with pkgs; [ python3 ruff ];

    dontConfigure = true;

    doCheck = true;
    checkPhase = ''
      ruff check scripts/
    '';

    buildPhase = ''
      python3 scripts/gen_gamma.py
      python3 scripts/gen_palettes.py
    '';

    installPhase = ''
      mkdir -p $out/{palettes,themes/helix}
      mv palettes $out/
      cp themes/helix/* $out/themes/helix/
    '';

    doInstallCheck = true;
    installCheckPhase = ''
      stale_files=""

      for f in $out/palettes/*.json; do
        base=$(basename "$f")
        if ! diff -q "$f" "$src/palettes/$base" > /dev/null 2>&1; then
          stale_files="$stale_files palettes/$base"
        fi
      done

      if [ -n "$stale_files" ]; then
        echo "Generated files are out of date in the repository:"
        for f in $stale_files; do
          echo "  $f"
        done
        echo ""
        echo "Run to regenerate:"
        echo "  kasane-generate"
        exit 1
      fi
    '';

    passthru.tests = {
      themes = pkgs.stdenvNoCC.mkDerivation {
        name = "kasane-test-themes";
        inherit src;
        nativeBuildInputs = [ pkgs.python3 ];
        dontConfigure = true;
        buildPhase = ''
          python3 scripts/gen_gamma.py
        '';

        doCheck = true;
        checkPhase = ''
          stale_files=""
          for f in themes/kitty/*-gamma.conf; do
            base=$(basename "$f")
            if ! diff -q "$f" "$src/themes/kitty/$base" > /dev/null 2>&1; then
              stale_files="$stale_files themes/kitty/$base"
            fi
          done
          if [ -n "$stale_files" ]; then
            echo "Generated gamma theme files are out of date in the repository:"
            for f in $stale_files; do
              echo "  $f"
            done
            echo ""
            echo "Run to regenerate:"
            echo "  kasane-generate"
            exit 1
          fi
        '';
        installPhase = "mkdir $out";
      };

      docs = pkgs.stdenvNoCC.mkDerivation {
        name = "kasane-test-docs";
        inherit src;
        nativeBuildInputs = with pkgs; [ python3 prettier ];
        dontConfigure = true;
        buildPhase = ''
          python3 scripts/gen_gamma.py
          python3 scripts/build_palette_docs.py
          prettier --write docs/*.html
        '';
        doCheck = true;
        checkPhase = ''
          stale_files=""
          for f in docs/*.html; do
            base=$(basename "$f")
            if ! diff -q "$f" "$src/docs/$base" > /dev/null 2>&1; then
              stale_files="$stale_files docs/$base"
            fi
          done
          if [ -n "$stale_files" ]; then
            echo "Generated doc files are out of date in the repository:"
            for f in $stale_files; do
              echo "  $f"
            done
            echo ""
            echo "Run to regenerate:"
            echo "  kasane-generate"
            exit 1
          fi
        '';
        installPhase = "mkdir $out";
      };
    };
  };
in
{
  inherit treefmt-check kasane kasane-generate;

  overlay = import ./overlay.nix;
  nixosModule = import ./module.nix;

  devShells.default = pkgs.mkShell {
    inputsFrom = [ treefmt-check kasane ];
    packages = with pkgs; [
      nixtamal
    ];
  };
}
