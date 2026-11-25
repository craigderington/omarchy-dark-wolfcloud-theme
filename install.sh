#!/usr/bin/env bash
# Register this working tree as a local Omarchy theme; no files are overwritten.
set -euo pipefail
source_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
theme_dir="${XDG_CONFIG_HOME:-$HOME/.config}/omarchy/themes/dark-wolfcloud"
mkdir -p -- "$(dirname -- "$theme_dir")"
if [[ -e "$theme_dir" || -L "$theme_dir" ]]; then
  if [[ "$(readlink -f -- "$theme_dir")" != "$source_dir" ]]; then
    printf 'A different theme already exists at %s; leaving it untouched.\n' "$theme_dir" >&2
    exit 1
  fi
else
  ln -s -- "$source_dir" "$theme_dir"
fi
omarchy theme set dark-wolfcloud
python "$source_dir/tools/install-wallpaper-motion.py"
