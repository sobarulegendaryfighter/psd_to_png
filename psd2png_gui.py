# psd2png_gui.py
"""
PSD -> PNG GUI exporter
- Uses psd-tools + Pillow + PySimpleGUI
- Pads exported PNGs so all have the same canvas size (largest width/height detected)
- Flatten option (merge visible layers)
"""

import os
from pathlib import Path
import PySimpleGUI as sg
from psd_tools import PSDImage
from PIL import Image

def load_psd_as_image(psd_path, flatten=False):
    psd = PSDImage.open(psd_path)
    # composite merges visible layers and preserves transparency
    try:
        img = psd.composite()
    except Exception:
        img = psd.topil()
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    return img

def resize_to_canvas(img, target_w, target_h):
    new_img = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    x = (target_w - img.width) // 2
    y = (target_h - img.height) // 2
    new_img.paste(img, (x, y))
    return new_img

def find_all_psd(path):
    p = Path(path)
    files = []
    if p.is_file() and p.suffix.lower() == ".psd":
        files = [p]
    elif p.is_dir():
        files = list(p.rglob("*.psd"))
    return files

def safe_str(p):
    try:
        return str(p)
    except Exception:
        return p.decode("utf-8") if isinstance(p, bytes) else repr(p)

def main():
    sg.theme("DarkBlue3")

    layout = [
        [sg.Text("PSD → PNG Exporter", font=("Segoe UI", 18))],
        [sg.Text("Input PSD file or folder:"), sg.Input(key="input", expand_x=True), 
         sg.FileBrowse("Browse File", file_types=(("PSD", "*.psd"),)), sg.FolderBrowse("Browse Folder")],
        [sg.Text("Output folder:"), sg.Input(key="out", expand_x=True), sg.FolderBrowse("Choose Output")],
        [sg.Checkbox("Flatten PSD (merge visible layers)", key="flatten")],
        [sg.Checkbox("Make all PNG same canvas size (pad to largest)", key="samecanvas", default=True)],
        [sg.HorizontalSeparator()],
        [sg.Button("Start Export", size=(18,1), button_color=("white","green")), sg.Button("Exit")],
        [sg.Multiline(key="log", size=(100,20), autoscroll=True, disabled=True)]
    ]

    window = sg.Window("PSD2PNG Exporter", layout, finalize=True)

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Exit"):
            break

        if event == "Start Export":
            input_path = values["input"]
            outdir = values["out"]
            flatten = values["flatten"]
            samecanvas = values["samecanvas"]

            log = window['log']
            def writeln(s=""):
                log.update(value=(log.get() + (s + "\n")))

            if not input_path:
                writeln("❗ Please select an input PSD file or a folder containing PSDs.")
                continue
            if not outdir:
                writeln("❗ Please select an output folder.")
                continue

            psd_files = find_all_psd(input_path)
            if not psd_files:
                writeln("❗ No PSD files found at the input location.")
                continue

            writeln(f"Found {len(psd_files)} PSD file(s).")
            target_w = target_h = None

            if samecanvas:
                max_w = 0
                max_h = 0
                writeln("Analyzing canvas sizes...")
                for f in psd_files:
                    try:
                        img = load_psd_as_image(f, flatten)
                        max_w = max(max_w, img.width)
                        max_h = max(max_h, img.height)
                    except Exception as e:
                        writeln(f"[ERROR] Analyze {f.name}: {e}")
                target_w, target_h = max_w, max_h
                writeln(f"All PNGs will be padded to: {target_w} x {target_h}")

            outdir_p = Path(outdir)
            outdir_p.mkdir(parents=True, exist_ok=True)

            for f in psd_files:
                try:
                    img = load_psd_as_image(f, flatten)
                    if samecanvas:
                        img = resize_to_canvas(img, target_w, target_h)
                    out_name = f.stem + ".png"
                    out_path = outdir_p / out_name
                    img.save(out_path)
                    writeln(f"[OK] {f.name} -> {out_name}")
                except Exception as e:
                    writeln(f"[ERROR] {f.name}: {e}")

            writeln("\n✔ Export finished!")

    window.close()

if __name__ == "__main__":
    main()
