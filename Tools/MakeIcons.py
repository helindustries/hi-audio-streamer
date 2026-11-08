"""Renders Source/Resources/AppIcon.svg into the Windows .ico and the macOS .icns the build embeds.
   Needs ImageMagick's `magick` on PATH for the SVG and Pillow for the icon containers. The .icns
   keeps the SVG's margin, which macOS expects around an app icon; the .ico is cut to the rounded
   square, as Windows icons fill their cell."""
import os
import subprocess
import sys
import tempfile

from PIL import Image

resources_dir: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Source", "Resources")
svg_size: int = 1024
square_margin: int = 100
ico_sizes: tuple[int, ...] = (16, 24, 32, 48, 64, 128, 256)

def _render(svg: str, png: str, crop: bool) -> None:
    # The explicit formats keep magick from reading the drive letter of a Windows path as one.
    command = ["magick", "-background", "none", "-density", "96", f"svg:{svg}"]
    if crop:
        side = svg_size - 2 * square_margin
        command += ["-crop", f"{side}x{side}+{square_margin}+{square_margin}", "+repage"]
    # Pillow cannot open the 16-bit RGBA PNG magick writes by default.
    command += ["-resize", f"{svg_size}x{svg_size}", "-depth", "8", f"png:{png}"]
    if (result := subprocess.run(command, capture_output=True, text=True)).returncode != 0:
        raise SystemExit(f"magick could not render {svg}: {result.stderr.strip()}")

def main() -> None:
    svg = os.path.join(resources_dir, "AppIcon.svg")
    if not os.path.isfile(svg):
        raise SystemExit(f"expected the icon source at {svg}")
    with tempfile.TemporaryDirectory() as work_dir:
        padded = os.path.join(work_dir, "padded.png")
        square = os.path.join(work_dir, "square.png")
        _render(svg, padded, crop=False)
        _render(svg, square, crop=True)
        with Image.open(square) as image:
            image.save(os.path.join(resources_dir, "AppIcon.ico"), sizes=[(size, size) for size in ico_sizes])
        with Image.open(padded) as image:
            image.save(os.path.join(resources_dir, "AppIcon.icns"))

if __name__ == "__main__":
    if len(sys.argv) != 1:
        raise SystemExit("usage: MakeIcons.py (takes no arguments)")
    main()
