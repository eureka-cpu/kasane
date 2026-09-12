{ config, lib, pkgs, ... }:

let
  cfg = config.programs.kasane;
in
{
  options.programs.kasane = {
    enable = lib.mkEnableOption "kasane color palette";

    package = lib.mkPackageOption pkgs "kasane" { };

    palette = lib.mkOption {
      type = lib.types.enum [
        "shibui"
        "obi"
        "shibui-raised"
        "obi-raised"
        "shibui-gamma"
        "obi-gamma"
        "shibui-raised-gamma"
        "obi-raised-gamma"
      ];
      default = "obi";
      description = "Which kasane palette to expose via programs.kasane.colors.";
    };

    colors = lib.mkOption {
      type = lib.types.attrsOf lib.types.str;
      readOnly = true;
      description = "Flat attrset of color key to hex value for the selected palette.";
    };
  };

  config = lib.mkIf cfg.enable {
    programs.kasane.colors = builtins.fromJSON (
      builtins.readFile (./palettes + "/${cfg.palette}.json")
    );
  };
}
