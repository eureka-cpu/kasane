let
  inputs = import ./nix/tamal { };
  pkgs = import inputs.nixpkgs { };

  inherit (pkgs) lib;

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
      python3 scripts/build_palette_docs.py
      prettier --write docs/*.html
    '';
  };

  kasane = pkgs.stdenvNoCC.mkDerivation {
    name = "kasane";
    src = lib.cleanSourceWith {
      src = lib.cleanSource ./.;
      filter = path: _type: !(
        lib.hasSuffix ".nix" path
        || lib.hasSuffix ".md" path
        || lib.hasSuffix ".json" path
        || lib.hasSuffix ".kdl" path
      );
    };

    nativeBuildInputs = [ kasane-generate pkgs.ruff ];

    dontConfigure = true;

    doCheck = true;
    checkPhase = ''
      ruff check scripts/
    '';

    buildPhase = ''
      kasane-generate
    '';

    installPhase = ''
      mkdir -p $out/{themes,docs}
      mv {themes,docs} $out/
    '';

    doInstallCheck = true;
    installCheckPhase = ''
      stale_files=""

      for f in $out/themes/*-gamma.conf; do
        base=$(basename "$f")
        if ! diff -q "$f" "$src/themes/$base" > /dev/null 2>&1; then
          stale_files="$stale_files themes/$base"
        fi
      done

      for f in $out/docs/*.html; do
        base=$(basename "$f")
        if ! diff -q "$f" "$src/docs/$base" > /dev/null 2>&1; then
          stale_files="$stale_files docs/$base"
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
  };
in
{
  inherit treefmt-check kasane kasane-generate;

  devShells.default = pkgs.mkShell {
    inputsFrom = [ treefmt-check kasane ];
    packages = with pkgs; [
      nixtamal
    ];
  };
}
