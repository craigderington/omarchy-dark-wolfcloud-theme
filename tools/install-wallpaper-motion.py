#!/usr/bin/env python3
"""Add theme-scoped motion through Omarchy's supported background clone."""
from datetime import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess

MARKER = "// Dark Wolfcloud motion overlay v1"
config = Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config")))
plugin_id = f"{os.environ.get('USER') or Path.home().name}.background"
target = config / "omarchy/plugins" / plugin_id
source = Path(os.environ.get("OMARCHY_PATH", "/usr/share/omarchy")) / "shell/plugins/background/Background.qml"
code = source.read_text()

def replace_once(old, new):
    global code
    if code.count(old) != 1:
        raise SystemExit("Installed Omarchy background source changed; no customization was written.")
    code = code.replace(old, new, 1)

replace_once('  property real revealProgress: 1', r'''  // Theme name is watched separately from the wallpaper path: the latter is
  // always current/theme/backgrounds, regardless of which theme owns it.
  property bool wolfcloudMotion: false
  property bool driftTransition: false
  property int driftDirection: 1
  property int motionCount: 0

  FileView {
    id: themeName
    path: root.stateHome + "/omarchy/current/theme.name"
    blockLoading: true
    watchChanges: true
    printErrors: false
    onLoaded: root.wolfcloudMotion = String(text() || "").trim() === "dark-wolfcloud"
    onFileChanged: reload()
    onLoadFailed: root.wolfcloudMotion = false
  }

  property real revealProgress: 1''')
replace_once('    oldBackground = fromPath || displayedBackground', r'''    driftTransition = wolfcloudMotion
    if (driftTransition) {
      driftDirection = -driftDirection
      motionCount += 1
    }
    oldBackground = fromPath || displayedBackground''')
replace_once('    duration: Style.duration(840)',
             '    duration: Style.duration(root.driftTransition ? 280 : 840)')
replace_once('    function refresh(): void {', r'''    function motionStatus(): string {
      return JSON.stringify({
        enabled: root.wolfcloudMotion,
        style: root.wolfcloudMotion ? "fade-drift" : "native",
        durationMs: Style.duration(root.wolfcloudMotion ? 280 : 840),
        progress: root.revealProgress,
        running: revealAnimation.running,
        count: root.motionCount,
        current: root.currentBackground,
        displayed: root.displayedBackground,
        incoming: root.incomingBackground,
        ready: root.ready
      })
    }

    function refresh(): void {''')
replace_once('        layer.enabled: root.incomingBackground !== "" && root.revealProgress < 1', r'''        // Crossfade the decoded frame; keep Omarchy's reveal mask for other themes.
        opacity: root.driftTransition ? root.revealProgress : 1
        layer.enabled: !root.driftTransition && root.incomingBackground !== "" && root.revealProgress < 1''')
replace_once('          id: incomingFrame\n          anchors.fill: parent', r'''          id: incomingFrame
          anchors.fill: parent
          // A little overscan covers the horizontal drift. Both settle exactly
          // onto the original still, without a crop jump at handoff.
          scale: root.driftTransition ? 1 + 0.03 * (1 - root.revealProgress) : 1
          transform: Translate {
            x: root.driftTransition ? root.driftDirection * incomingFrame.width * 0.012 * (1 - root.revealProgress) : 0
          }''')
code = MARKER + "\n" + code

if target.exists():
    manifest = json.loads((target / "manifest.json").read_text())
    if manifest.get("omarchy", {}).get("clonedFrom") != "omarchy.background":
        raise SystemExit(f"Existing {target} is not a background clone; leaving it untouched.")
    if MARKER in (target / "Background.qml").read_text():
        print(f"Wallpaper motion already installed: {plugin_id}")
        subprocess.run(["omarchy", "plugin", "enable", plugin_id], check=True)
        raise SystemExit(0)
    raise SystemExit(f"An existing unmodified-by-us clone lives at {target}; leaving it untouched.")

# Clone with Omarchy's own command so its routing and replacement bookkeeping
# remain authoritative. Back up the user configuration before that command.
shell_config = config / "omarchy/shell.json"
if shell_config.exists():
    backup = shell_config.with_name("shell.json.bak.wolfcloud-motion-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
    shutil.copy2(shell_config, backup)
subprocess.run(["omarchy", "plugin", "clone", "omarchy.background"], check=True)
qml = target / "Background.qml"
original = qml.read_text()
try:
    qml.write_text(code)
    subprocess.run(["omarchy-shell", "shell", "rescanPlugins"], check=True)
except BaseException:
    qml.write_text(original)
    raise
print(f"Installed Dark Wolfcloud fade + horizontal drift in {qml}")
