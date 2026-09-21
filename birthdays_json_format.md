## Postprocess events file (`birthdays.json`)

The postprocess step draws extra elements (images and text) on the day image when the date matches one of the events described in a JSON file. If the file does not exist, the step is disabled and the image is returned unchanged.

The file is read as UTF-8, so non-Latin text (e.g. Cyrillic) can be used directly. It must be valid JSON: no comments and no trailing commas.

### Configuration

The following settings are read from the `CFG` object in `settings.py`:

| Setting | Description | Example |
|---|---|---|
| `PP_FILE_NAME` | Path to the events JSON file. | `"birthdays.json"` |
| `PP_IMAGES_DIR` | Folder where image files referenced by `src` are searched. Ignored when `src` is an absolute path. | `"draw/images"` |
| `PP_FONT` | Path to a `.ttf` / `.otf` font file used for text. The font must contain the glyphs you use. | `FONT_DIR + "/arial.ttf"` |
| `PP_FONT_SIZES` | Font sizes as a fraction of the image height, for `small`, `medium` and `big`. | `{"small": 0.04, "medium": 0.07, "big": 0.12}` |
| `PP_MARGIN` | Distance in pixels kept between drawn elements and the image border. | `10` |

### File structure

The root object has a single key, `events`, containing a list of events. Each event has a list of `action` items that are drawn when the event matches.

```json
{
  "events": [
    {
      "type": "birthday",
      "title": "Ivan",
      "day": 12,
      "month": 1,
      "year": 2011,
      "action": [
        { "type": "image", "src": "ring.png", "hpos": "center", "vpos": "center" },
        { "type": "text", "src": "Іван {age}", "hpos": "center", "vpos": "bottom",
          "color": "red", "font": "medium" }
      ]
    }
  ]
}
```

### Event fields

| Field | Type | Required | Description |
|---|---|---|---|
| `type` | string | no | Event type. `"birthday"` has special matching and enables the `{age}` placeholder (see below). |
| `title` | string | no | Free-form name of the event. Only used in log messages. |
| `day` | integer | yes | Day of the month (1–31). |
| `month` | integer | yes | Month (1–12). |
| `year` | integer | birthday: yes | For `birthday`: the birth year. For other types: the exact year in which the event applies. |
| `action` | list | yes | Elements to draw, see [Actions](#actions). |

#### Matching rules

An event applies to a given date only if `day` and `month` are equal to the date's day and month, and additionally:

- **`type: "birthday"`**: repeats every year, starting from the birth year in `year`. It does not apply to years before the birth year.
- **any other type**: applies only in the year given in `year`. If `year` is omitted, the event repeats every year.

If several events match the same date, all of them are drawn, in the order they appear in the file.

### Actions

Actions are drawn in the order they are listed, so later actions are drawn on top of earlier ones. Every action has a `type` (`"image"` or `"text"`) and the position fields `hpos` and `vpos`. An action with an unknown `type` is skipped with a message in the log.

#### Common position fields

| Field | Values | Default |
|---|---|---|
| `hpos` | `"left"`, `"center"`, `"right"` | `"center"` |
| `vpos` | `"top"`, `"center"`, `"bottom"` | `"center"` |

`"left"` and `"right"` are also accepted for `vpos` as aliases of `"top"` and `"bottom"`. Elements are placed inside the area left after applying `PP_MARGIN` on every side.

#### `image` action

Draws a picture on top of the day image. Transparency (for example in PNG files) is preserved.

| Field | Type | Required | Description |
|---|---|---|---|
| `src` | string | yes | Image file name, relative to `PP_IMAGES_DIR`, or an absolute path. If the file is not found, the action is skipped with a message in the log. |
| `hpos`, `vpos` | string | no | Position, see above. |
| `scale` | number | no | Scale factor, default `1.0`. Images that would not fit inside the day image (minus margins) are shrunk automatically, keeping the aspect ratio. |

#### `text` action

Draws text on top of the day image.

| Field | Type | Required | Description |
|---|---|---|---|
| `src` | string | yes | Text to draw. Use `\n` for a new line. May contain placeholders, see below. |
| `hpos`, `vpos` | string | no | Position, see above. For multi-line text `hpos` also sets the alignment of the lines. |
| `color` | string | no | Basic color name (`"red"`, `"green"`, `"blue"`, `"black"`, `"white"`, `"yellow"`, ...) or hex value such as `"#ff8800"`. Case-insensitive. Default `"black"`; an unknown value also falls back to black. |
| `font` | string | no | `"small"`, `"medium"` or `"big"`. Default `"medium"`. The real size is the fraction from `PP_FONT_SIZES` multiplied by the image height (at least 8 px). |

##### Placeholders

| Placeholder | Available in | Replaced with |
|---|---|---|
| `{age}` | events with `"type": "birthday"` | The current year minus the birth year from `year`. |

For example, with `"year": 2011`, the text `"Іван {age}"` is drawn as `Іван 15` on any date in 2026 that matches the event.
