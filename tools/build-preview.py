#!/usr/bin/env python3
"""Render a reproducible design study and crest artwork with native SVG tools."""
from pathlib import Path
import base64
import html
import subprocess
import tomllib

ROOT = Path(__file__).resolve().parent.parent
P = tomllib.loads((ROOT / 'colors.toml').read_text())
parts = []
def add(s):
    parts.append(s)
def rect(x, y, w, h, fill, radius=0, stroke=None, sw=1, extra=''):
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" '
        + (f'stroke="{stroke}" stroke-width="{sw}" ' if stroke else '') + extra + '/>')
def text(x, y, value, color=None, size=16, weight=400, mono=False, extra=''):
    font = 'CaskaydiaMono Nerd Font' if mono else 'Inter, sans-serif'
    add(f'<text x="{x}" y="{y}" fill="{color or P["foreground"]}" font-size="{size}" '
        f'font-weight="{weight}" font-family="{font}" {extra}>{html.escape(value)}</text>')
def rich(x, y, tokens, size=15):
    add(f'<text x="{x}" y="{y}" font-family="CaskaydiaMono Nerd Font" font-size="{size}" xml:space="preserve">')
    for value, color in tokens:
        add(f'<tspan fill="{color}">{html.escape(value)}</tspan>')
    add('</text>')
def image(path, x, y, w, h, extra=''):
    mime = 'image/svg+xml' if path.suffix == '.svg' else 'image/png'
    data = base64.b64encode(path.read_bytes()).decode()
    add(f'<image x="{x}" y="{y}" width="{w}" height="{h}" href="data:{mime};base64,{data}" {extra}/>')
def render(svg, name, width=None):
    source = ROOT / 'assets' / (name + '.svg')
    source.write_text(svg)
    command = ['rsvg-convert', str(source), '-o', str(ROOT / (name + '.png'))]
    if width:
        command += ['-w', str(width)]
    subprocess.run(command, check=True)

def window(x, y, w, h, title, active=False):
    rect(x, y, w, h, '#05090c', 10, extra='filter="url(#shadow)"')
    rect(x, y, w, h, P['background'], 10, 'url(#ion)' if active else '#31515c', 2 if active else 1)
    rect(x+2, y+2, w-4, 36, '#111d23', 8)
    rect(x+2, y+26, w-4, 12, '#111d23')
    text(x+18, y+25, title, P['light_foreground'], 13, mono=True)
    for i, color in enumerate(['#31515c', '#31515c', '#ffbf69' if active else '#31515c']):
        add(f'<circle cx="{x+w-52+i*15}" cy="{y+19}" r="3" fill="{color}"/>')

add('<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080">')
add('''<defs>
 <linearGradient id="ion"><stop stop-color="#71e5e8"/><stop offset=".58" stop-color="#a6d4d2"/><stop offset="1" stop-color="#ffbf69"/></linearGradient>
 <linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#05090c" stop-opacity="0"/><stop offset="1" stop-color="#05090c" stop-opacity=".8"/></linearGradient>
 <filter id="shadow" x="-15%" y="-15%" width="140%" height="150%"><feGaussianBlur stdDeviation="13"/></filter>
 <clipPath id="desktop"><rect x="48" y="142" width="1824" height="764" rx="12"/></clipPath>
</defs>''')
rect(0, 0, 1920, 1080, '#080e12')
text(52, 40, 'O M A R C H Y   /   O R I G I N A L   T H E M E', '#789095', 11, 600)
text(48, 92, 'DARK WOLFCLOUD', '#edfaf5', 46, 700, extra='letter-spacing="-1.4"')
text(51, 119, 'Volcanic glass. Ion storms. A molten eye in the dark.', '#b5cacb', 16)
image(ROOT / 'assets/wolfcrest.svg', 1745, 18, 100, 100)
text(1701, 120, 'DESIGN STUDY  /  01', '#789095', 10, 600)
add('<g clip-path="url(#desktop)">')
image(ROOT / 'backgrounds/01-dark-wolfcloud.png', 48, 142, 1824, 764)
rect(48, 540, 1824, 366, 'url(#fade)')
rect(48, 142, 1824, 33, '#080e12')
text(67, 164, '◈', '#71e5e8', 17)
rect(101, 148, 26, 21, '#18262d', 4)
text(109, 163, '1', '#71e5e8', 12, 600, True)
text(142, 163, '2   3   4', '#789095', 12, mono=True)
text(234, 163, 'dark-wolfcloud', '#b5cacb', 12, mono=True)
text(850, 163, 'TUESDAY  21:42', '#d4e2df', 12, mono=True)
text(1563, 163, 'NET  ↑   VOL  62%   PWR', '#b5cacb', 12, mono=True)
window(80, 218, 566, 389, 'wolfcloud  /  terminal', True)
text(104, 280, '❯', '#71e5e8', 18, mono=True)
text(128, 280, 'fastfetch', '#edfaf5', 16, mono=True)
image(ROOT / 'assets/wolfcrest.svg', 103, 305, 142, 142)
text(274, 323, 'W O L F C L O U D', '#71e5e8', 16, 600, True)
text(274, 354, 'OS      Omarchy', '#d4e2df', 14, mono=True)
text(274, 381, 'WM      Hyprland', '#b5cacb', 14, mono=True)
text(274, 408, 'SHELL   bash', '#b5cacb', 14, mono=True)
text(274, 435, 'MOOD    ion / ember', '#ffbf69', 14, mono=True)
for i, key in enumerate(['red', 'orange', 'yellow', 'green', 'cyan', 'blue', 'magenta']):
    rect(108+i*37, 477, 30, 14, P[key], 2)
text(104, 534, '~/Projects/dark-wolfcloud', '#83b8ce', 14, mono=True)
rich(104, 563, [('❯ ', '#71e5e8'), ('omarchy theme set ', '#d4e2df'), ('dark-wolfcloud', '#ffbf69')], 14)
rect(104, 578, 8, 15, '#edfaf5')
# Editor shows the same syntax roles as the installed aether integration.
window(675, 497, 672, 375, 'neovim  /  storm.lua')
rect(677, 535, 668, 29, '#080e12')
text(699, 555, 'storm.lua', '#ffbf69', 13, mono=True)
rect(688, 562, 115, 2, '#ffbf69')
code = [
 [('local ', '#d78db8'), ('storm', '#d4e2df'), (' = {}', '#b5cacb')],
 [],
 [('function ', '#d78db8'), ('storm', '#d4e2df'), ('.', '#b5cacb'), ('awaken', '#71e5e8'), ('(cloud)', '#d4e2df')],
 [('  local ', '#d78db8'), ('eye', '#d4e2df'), (' = ', '#b5cacb'), ('"molten amber"', '#9dbfa4')],
 [('  local ', '#d78db8'), ('charge', '#d4e2df'), (' = ', '#b5cacb'), ('0.98', '#ffad66')],
 [],
 [('  return ', '#d78db8'), ('cloud', '#d4e2df'), (':', '#b5cacb'), ('ignite', '#71e5e8'), ('(eye, charge)', '#d4e2df')],
 [('end', '#d78db8')],
 [],
 [('-- cold steel. warm signal.', '#789095')],
]
rect(737, 619, 592, 23, '#18262d')
rect(904, 642, 151, 23, '#493b2c')
for i, row in enumerate(code):
    text(698, 589+i*24, str(i+1).rjust(2), '#789095', 14, mono=True)
    rich(742, 589+i*24, row, 15)
rect(677, 844, 668, 26, '#111d23')
rect(677, 844, 89, 26, '#71e5e8', 0)
text(688, 862, 'NORMAL', '#0b1216', 12, 700, True)
text(781, 862, 'storm.lua', '#b5cacb', 12, mono=True)
text(1190, 862, 'Lua   3:1', '#83b8ce', 12, mono=True)
# Amber-selected launcher echoes the wolf's eye.
window(1415, 645, 421, 225, 'launcher')
text(1438, 708, 'Search applications…', '#8ba2a4', 15)
rect(1431, 725, 389, 42, '#2b261f', 6, '#806242', 1)
text(1450, 752, '◈   Terminal', '#ffe2a8', 15, 500)
text(1770, 752, '↵', '#ffbf69', 15)
text(1450, 797, '◇   Files', '#b5cacb', 15)
text(1450, 839, '◇   Editor', '#b5cacb', 15)
text(1570, 606, 'COLD FOCUS / WARM INTENT', '#b5cacb', 10, 600, extra='letter-spacing="1.5"')
add('</g>')
rect(48, 142, 1824, 764, 'none', 12, '#294149')
text(48, 945, 'THE STORM SPECTRUM', '#789095', 11, 600, extra='letter-spacing="2"')
colors = [('OBSIDIAN', '#0b1216'), ('CLOUD', '#18262d'), ('MIST', '#d4e2df'), ('ION', '#71e5e8'), ('WOLF EYE', '#ffbf69'), ('EMBER', '#f47770'), ('STORM ROSE', '#d78db8'), ('LICHEN', '#9dbfa4')]
for i, (label, color) in enumerate(colors):
    x = 48+i*232
    rect(x, 963, 200, 36, color, 4, '#294149' if i<2 else None)
    text(x, 1022, label, '#b5cacb', 11, 600)
    text(x, 1043, color.upper(), '#789095', 11, mono=True)
add('</svg>')
render(''.join(parts), 'preview')
# Wide transparent wordmark follows Omarchy's stock unlock-art aspect ratio.
crest_data = base64.b64encode((ROOT / 'assets/wolfcrest.svg').read_bytes()).decode()
wordmark = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="188" viewBox="0 0 800 188">
<image x="6" y="6" width="176" height="176" href="data:image/svg+xml;base64,{crest_data}"/>
<text x="211" y="87" font-family="Inter, sans-serif" font-size="43" font-weight="700" letter-spacing="3" fill="#edfaf5">DARK</text>
<text x="211" y="136" font-family="Inter, sans-serif" font-size="43" font-weight="700" letter-spacing="3" fill="#edfaf5">WOLFCLOUD</text>
<path d="M213 157H532" stroke="#31515c" stroke-width="2"/><path d="M213 157H305" stroke="#71e5e8" stroke-width="2"/><path d="M532 157H606" stroke="#ffbf69" stroke-width="2"/>
</svg>'''
render(wordmark, 'unlock')
preview_unlock = f'''<svg xmlns="http://www.w3.org/2000/svg" width="640" height="360" viewBox="0 0 640 360">
<rect width="640" height="360" fill="#080e12"/>
<image x="236" y="34" width="168" height="168" href="data:image/svg+xml;base64,{crest_data}"/>
<text x="320" y="242" text-anchor="middle" font-family="Inter, sans-serif" font-size="25" font-weight="700" letter-spacing="3" fill="#edfaf5">DARK WOLFCLOUD</text>
<text x="320" y="274" text-anchor="middle" font-family="Inter, sans-serif" font-size="11" letter-spacing="2" fill="#789095">VOLCANIC GLASS / ION STORM</text>
</svg>'''
render(preview_unlock, 'preview-unlock')
print('Rendered preview.png, unlock.png, and preview-unlock.png')
