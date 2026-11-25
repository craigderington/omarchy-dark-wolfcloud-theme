#!/usr/bin/env python3
"""Add theme-scoped motion through Omarchy's supported background clone."""
from datetime import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

MARKER = "// Dark Wolfcloud motion overlay v2"
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
      var monitors = []
      for (var panel of backgrounds.instances) {
        monitors.push({
          name: panel.modelData.name,
          ready: panel.backgroundReady,
          incomingReady: panel.incomingReady,
          visible: panel.visible,
          participating: panel.maskReady,
          opacity: panel.incomingOpacity,
          renderedFrames: panel.motionFrames
        })
      }
      return JSON.stringify({
        monitors: monitors,
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
replace_once("""    panel.maskReady = true
    if (revealStartedVersion === backgroundVersion) return""", """    if (root.driftTransition) {
      // A small display can decode first. Start only when every output has
      // its incoming image, then reveal all of them in the same animation.
      for (var output of backgrounds.instances)
        if (!output.incomingReady) return
      for (var output of backgrounds.instances) {
        output.maskReady = true
        output.motionFrames = 0
      }
    } else {
      panel.maskReady = true
    }
    if (revealStartedVersion === backgroundVersion) return""")
replace_once("""      property bool maskReady: false""", """      property bool maskReady: false
      readonly property bool incomingReady: incomingFrame.status === Image.Ready
      readonly property real incomingOpacity: incomingLayer.opacity
      property int motionFrames: 0

      FrameAnimation {
        running: root.driftTransition && revealAnimation.running && incomingLayer.visible
        onTriggered: panel.motionFrames += 1
      }""")
replace_once("""  function prepareBackground(path) {""", """  // Retain the incoming layer until every output has submitted its final
  // still. A quick small display must not clear a slower output's cover.
  function finishReveal() {
    if (!finishingTransition || !root.ready) return
    incomingBackground = ""
    oldBackground = ""
    preparedBackground = ""
    finishingTransition = false
    pruneNativeSizes()
  }

  onReadyChanged: finishReveal()

  function prepareBackground(path) {""")
replace_once("""          if (ready && root.finishingTransition) {
            root.incomingBackground = ""
            root.oldBackground = ""
            root.preparedBackground = ""
            root.finishingTransition = false
            root.pruneNativeSizes()
          }""", """          if (ready) Qt.callLater(root.finishReveal)""")
replace_once("""      root.revealProgress = 1
    }
  }

  Component.onCompleted: refreshBackground()""", """      root.revealProgress = 1
      Qt.callLater(root.finishReveal)
    }
  }

  Component.onCompleted: refreshBackground()""")

code = MARKER + "\n" + code

def ensure_loaded():
    # Some Quickshell versions retain a component after a plugin rescan.
    for _ in range(15):
        probe = subprocess.run(["omarchy-shell", "background", "motionStatus"],
                               text=True, capture_output=True)
        if probe.returncode == 0:
            try:
                if "monitors" in json.loads(probe.stdout):
                    return
            except (ValueError, TypeError):
                pass
        time.sleep(0.1)
    subprocess.run(["omarchy", "restart", "shell"], check=True)
    probe = subprocess.run(["omarchy-shell", "background", "motionStatus"],
                           text=True, capture_output=True, check=True)
    if "monitors" not in json.loads(probe.stdout):
        raise SystemExit("Background motion did not load after the shell restart.")

if target.exists():
    manifest = json.loads((target / "manifest.json").read_text())
    if manifest.get("omarchy", {}).get("clonedFrom") != "omarchy.background":
        raise SystemExit(f"Existing {target} is not a background clone; leaving it untouched.")
    original = (target / "Background.qml").read_text()
    if not original.startswith("// Dark Wolfcloud motion overlay v"):
        raise SystemExit(f"An existing clone lives at {target}; leaving it untouched.")
else:
    # Let Omarchy own clone routing and source-replacement bookkeeping.
    shell_config = config / "omarchy/shell.json"
    if shell_config.exists():
        backup = shell_config.with_name("shell.json.bak.wolfcloud-motion-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
        shutil.copy2(shell_config, backup)
    subprocess.run(["omarchy", "plugin", "clone", "omarchy.background"], check=True)
    original = (target / "Background.qml").read_text()

qml = target / "Background.qml"
try:
    if original != code:
        qml.write_text(code)
        subprocess.run(["omarchy-shell", "shell", "rescanPlugins"], check=True)
    subprocess.run(["omarchy", "plugin", "enable", plugin_id], check=True)
    ensure_loaded()
except BaseException:
    qml.write_text(original)
    raise
print(f"Installed synchronized Dark Wolfcloud fade + horizontal drift in {qml}")
