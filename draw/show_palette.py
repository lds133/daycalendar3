from PIL import Image
import sys


def show_palette(filename):
    img = Image.open(filename)

    print(f"File: {filename}")
    print(f"Image mode: {img.mode}")
    print(f"Size: {img.size}")

    if img.mode != "P":
        print("\nThis image is not a paletted image.")
        return

    palette = img.getpalette()

    if palette is None:
        print("\nNo palette found.")
        return

    # Pillow stores palette entries as consecutive R, G, B values.
    num_colors = len(palette) // 3

    print(f"\nPalette entries: {num_colors}")
    print()
    print(f"{'Index':>5}  {'R':>3} {'G':>3} {'B':>3}   {'Hex':>7}")
    print("-" * 30)

    for i in range(num_colors):
        r = palette[i * 3]
        g = palette[i * 3 + 1]
        b = palette[i * 3 + 2]

        print(f"{i:5}  {r:3} {g:3} {b:3}   #{r:02X}{g:02X}{b:02X}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python palette.py image.bmp")
        sys.exit(1)

    show_palette(sys.argv[1])