from settings import CFG
from PIL import Image, ImageDraw, ImageFont, ImageColor
import json
import os


H_ALIGN = {"left": 0.0, "center": 0.5, "right": 1.0}
V_ALIGN = {"top": 0.0, "left": 0.0, "center": 0.5, "bottom": 1.0, "right": 1.0}


class DayPostprocess:

    def __init__(self, cfg: CFG):
        self.cfg = cfg
        self.data = None
        self._fonts = {}

        fn = cfg.PP_FILE_NAME
        if os.path.isfile(fn):
            with open(fn, encoding="utf-8") as f:
                self.data = json.load(f)
            print(f"Using {fn} postprocess file.")
        else:
            print(f"{fn} file not found. Postprocess step disabled.")

    def update(self, img: Image.Image, year: int, month: int, day: int) -> Image.Image:
        if self.data is None:
            return img

        events = [e for e in self.data.get("events", [])
                  if self._matches(e, year, month, day)]
        if not events:
            return img

        original_mode = img.mode
        result = img.convert("RGBA")

        for ev in events:
            age = year - ev["year"] if ev.get("type") == "birthday" else None
            for action in ev.get("action", []):
                kind = action.get("type")
                if kind == "image":
                    self._draw_image(result, action)
                elif kind == "text":
                    self._draw_text(result, action, age)
                else:
                    print(f"Postprocess: unknown action type '{kind}' "
                          f"in event '{ev.get('title', '')}', skipped.")

        return result if original_mode == "RGBA" else result.convert(original_mode)

    @staticmethod
    def _matches(ev: dict, year: int, month: int, day: int) -> bool:
        if ev.get("month") != month or ev.get("day") != day:
            return False
        if ev.get("type") == "birthday":
            return year >= ev["year"]
        return ev.get("year", year) == year

    def _draw_image(self, canvas: Image.Image, action: dict):
        path = action.get("src", "")
        if not os.path.isabs(path):
            path = os.path.join(self.cfg.PP_IMAGES_DIR, path)
        if not os.path.isfile(path):
            print(f"Postprocess: image '{path}' not found, skipped.")
            return

        overlay = Image.open(path).convert("RGBA")

        m = self.cfg.PP_MARGIN
        scale = float(action.get("scale", 1.0))
        max_w, max_h = max(1, canvas.width - 2 * m), max(1, canvas.height - 2 * m)
        scale = min(scale, max_w / overlay.width, max_h / overlay.height)
        if scale != 1.0:
            size = (max(1, round(overlay.width * scale)), max(1, round(overlay.height * scale)))
            overlay = overlay.resize(size, Image.LANCZOS)

        x, y = self._position(canvas.size, overlay.size, action)
        canvas.paste(overlay, (x, y), overlay)

    def _draw_text(self, canvas: Image.Image, action: dict, age=None):
        text = str(action.get("src", ""))
        if age is not None:
            text = text.replace("{age}", str(age))
        if not text:
            return

        font = self._font(action.get("font", "medium"), canvas.height)
        color = self._color(action.get("color"))
        align = action.get("hpos", "center")
        align = align if align in H_ALIGN else "center"

        draw = ImageDraw.Draw(canvas)
        l, t, r, b = draw.multiline_textbbox((0, 0), text, font=font, align=align)
        x, y = self._position(canvas.size, (r - l, b - t), action)
        draw.multiline_text((x - l, y - t), text, font=font, fill=color, align=align)

    def _position(self, canvas_size, obj_size, action):
        m = self.cfg.PP_MARGIN
        fx = H_ALIGN.get(action.get("hpos", "center"), 0.5)
        fy = V_ALIGN.get(action.get("vpos", "center"), 0.5)
        x = m + (canvas_size[0] - 2 * m - obj_size[0]) * fx
        y = m + (canvas_size[1] - 2 * m - obj_size[1]) * fy
        return int(round(x)), int(round(y))

    @staticmethod
    def _color(name):
        try:
            return ImageColor.getcolor(str(name or "black").strip().lower(), "RGBA")
        except ValueError:
            print(f"Postprocess: unknown color '{name}', using black.")
            return (0, 0, 0, 255)

    def _font(self, size_name: str, image_height: int):
        sizes = self.cfg.PP_FONT_SIZES
        px = max(8, int(image_height * sizes.get(size_name, sizes["medium"])))
        if px not in self._fonts:
            self._fonts[px] = ImageFont.truetype(self.cfg.PP_FONT, px)
        return self._fonts[px]