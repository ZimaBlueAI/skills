#!/usr/bin/env python3
"""Normalize character turnaround views onto a shared transparent canvas."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Iterable

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError as exc:  # pragma: no cover - dependency failure path
    raise SystemExit("Pillow is required. Install it with: python -m pip install Pillow") from exc


VERSION = "1.0.0"
VIEW_ORDER = ("front", "left", "back", "right")


def flattened_data(image: Image.Image):
    getter = getattr(image, "get_flattened_data", None)
    return getter() if getter else image.getdata()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def border_samples(image: Image.Image, count: int = 24) -> list[tuple[int, int, int]]:
    rgb = image.convert("RGB")
    width, height = rgb.size
    pixels = rgb.load()
    samples: list[tuple[int, int, int]] = []
    for index in range(count):
        tx = round(index * (width - 1) / max(1, count - 1))
        ty = round(index * (height - 1) / max(1, count - 1))
        samples.extend(
            [pixels[tx, 0], pixels[tx, height - 1], pixels[0, ty], pixels[width - 1, ty]]
        )
    return samples


def estimate_border(image: Image.Image) -> tuple[tuple[int, int, int], float]:
    samples = border_samples(image)
    color = tuple(int(median([pixel[channel] for pixel in samples])) for channel in range(3))
    distances = [math.dist(pixel, color) for pixel in samples]
    return color, float(median(distances))


def key_green(image: Image.Image) -> Image.Image:
    result = image.convert("RGBA")
    cleaned: list[tuple[int, int, int, int]] = []
    for red, green, blue, alpha in flattened_data(result):
        dominance = min(green - red, green - blue)
        if green < 55 or dominance <= 8:
            cleaned.append((red, green, blue, alpha))
            continue
        strength = clamp((dominance - 8) / 52.0, 0.0, 1.0)
        if green > 130 and dominance > 38:
            strength = 1.0
        new_alpha = int(round(alpha * (1.0 - strength)))
        if new_alpha < 6:
            cleaned.append((red, green, blue, 0))
            continue
        despilled_green = min(green, max(red, blue) + 12)
        cleaned.append((red, despilled_green, blue, new_alpha))
    result.putdata(cleaned)
    return result


def key_corner_color(image: Image.Image, color: tuple[int, int, int]) -> Image.Image:
    result = image.convert("RGBA")
    cleaned: list[tuple[int, int, int, int]] = []
    inner, outer = 16.0, 62.0
    for red, green, blue, alpha in flattened_data(result):
        distance = math.dist((red, green, blue), color)
        if distance <= inner:
            cleaned.append((red, green, blue, 0))
        elif distance >= outer:
            cleaned.append((red, green, blue, alpha))
        else:
            factor = (distance - inner) / (outer - inner)
            cleaned.append((red, green, blue, int(round(alpha * factor))))
    result.putdata(cleaned)
    return result


def remove_background(image: Image.Image, mode: str) -> tuple[Image.Image, str, dict[str, object]]:
    rgba = image.convert("RGBA")
    alpha = rgba.getchannel("A")
    alpha_extrema = alpha.getextrema()
    if mode == "none":
        return rgba, "none", {}
    if mode == "auto" and alpha_extrema[0] < 240:
        return rgba, "existing-alpha", {}

    border_color, border_spread = estimate_border(rgba)
    selected = mode
    if mode == "auto":
        red, green, blue = border_color
        if green > red + 24 and green > blue + 16:
            selected = "green"
        elif border_spread <= 28:
            selected = "corner"
        else:
            selected = "none"

    details: dict[str, object] = {
        "border_color": list(border_color),
        "border_spread": round(border_spread, 3),
    }
    if selected == "green":
        return key_green(rgba), "green", details
    if selected == "corner":
        return key_corner_color(rgba, border_color), "corner", details
    return rgba, "none", details


def visible_bbox(image: Image.Image, threshold: int) -> tuple[int, int, int, int] | None:
    alpha = image.convert("RGBA").getchannel("A")
    mask = alpha.point(lambda value: 255 if value > threshold else 0)
    return mask.getbbox()


def crop_visible(image: Image.Image, threshold: int, margin_ratio: float) -> tuple[Image.Image, list[int]]:
    bbox = visible_bbox(image, threshold)
    if bbox is None:
        raise ValueError("No visible subject was found after background removal")
    left, top, right, bottom = bbox
    subject_width = right - left
    subject_height = bottom - top
    margin = max(8, int(round(max(subject_width, subject_height) * margin_ratio)))
    crop_box = (
        max(0, left - margin),
        max(0, top - margin),
        min(image.width, right + margin),
        min(image.height, bottom + margin),
    )
    return image.crop(crop_box), list(crop_box)


def premultiplied_resize(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    width, height = max(1, size[0]), max(1, size[1])
    rgba = image.convert("RGBA")
    try:
        premultiplied = rgba.convert("RGBa")
        resized = premultiplied.resize((width, height), Image.Resampling.LANCZOS)
        return resized.convert("RGBA")
    except ValueError:
        return rgba.resize((width, height), Image.Resampling.LANCZOS)


def checkerboard(size: tuple[int, int], cell: int = 16) -> Image.Image:
    width, height = size
    board = Image.new("RGBA", size, (238, 238, 238, 255))
    draw = ImageDraw.Draw(board)
    for y in range(0, height, cell):
        for x in range(0, width, cell):
            if (x // cell + y // cell) % 2:
                draw.rectangle((x, y, min(width, x + cell), min(height, y + cell)), fill=(211, 211, 211, 255))
    return board


def make_contact_sheet(images: dict[str, Image.Image], output_path: Path) -> None:
    tile = 280
    label_height = 36
    columns = len(images)
    sheet = Image.new("RGB", (columns * tile, tile + label_height), (250, 247, 240))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for column, (name, image) in enumerate(images.items()):
        preview = image.copy()
        preview.thumbnail((tile - 20, tile - 20), Image.Resampling.LANCZOS)
        background = checkerboard((tile, tile), 14)
        x = (tile - preview.width) // 2
        y = (tile - preview.height) // 2
        background.alpha_composite(preview, (x, y))
        sheet.paste(background.convert("RGB"), (column * tile, 0))
        text_box = draw.textbbox((0, 0), name.upper(), font=font)
        text_width = text_box[2] - text_box[0]
        draw.text((column * tile + (tile - text_width) // 2, tile + 11), name.upper(), fill=(35, 35, 35), font=font)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output_path, format="PNG", optimize=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--front", required=True, type=Path)
    parser.add_argument("--left", required=True, type=Path)
    parser.add_argument("--back", required=True, type=Path)
    parser.add_argument("--right", type=Path)
    parser.add_argument("--mirror-right-from-left", action="store_true")
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--character-name", default="character")
    parser.add_argument("--anchor", action="append", default=[])
    parser.add_argument("--asymmetry-note", action="append", default=[])
    parser.add_argument("--size", type=int, default=768)
    parser.add_argument("--alpha-threshold", type=int, default=18)
    parser.add_argument("--margin-ratio", type=float, default=0.025)
    parser.add_argument("--baseline", type=float, default=0.93)
    parser.add_argument("--max-width", type=float, default=0.84)
    parser.add_argument("--max-height", type=float, default=0.86)
    parser.add_argument("--scale-mode", choices=("common", "equal-height"), default="common")
    parser.add_argument("--background", choices=("none", "auto", "green", "corner"), default="none")
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    if args.right and args.mirror_right_from_left:
        raise SystemExit("Use either --right or --mirror-right-from-left, not both")
    if args.mirror_right_from_left and args.asymmetry_note:
        raise SystemExit("Refusing to mirror a character with recorded asymmetry. Supply a real --right view")
    if args.size < 128:
        raise SystemExit("--size must be at least 128")
    if not 0 <= args.alpha_threshold <= 254:
        raise SystemExit("--alpha-threshold must be between 0 and 254")
    if not 0.5 <= args.baseline <= 0.99:
        raise SystemExit("--baseline must be between 0.5 and 0.99")
    if not 0.1 <= args.max_width <= 0.98 or not 0.1 <= args.max_height <= 0.98:
        raise SystemExit("--max-width and --max-height must be between 0.1 and 0.98")
    if args.margin_ratio < 0 or args.margin_ratio > 0.25:
        raise SystemExit("--margin-ratio must be between 0 and 0.25")


def main() -> int:
    args = parse_args()
    validate_args(args)

    sources: dict[str, Path] = {"front": args.front, "left": args.left, "back": args.back}
    if args.right:
        sources["right"] = args.right
    for view_name, path in sources.items():
        if not path.is_file():
            raise SystemExit(f"Missing {view_name} input: {path}")

    processed: dict[str, dict[str, object]] = {}
    cropped: dict[str, Image.Image] = {}
    for view_name in (name for name in VIEW_ORDER if name in sources):
        path = sources[view_name]
        with Image.open(path) as opened:
            rgba, background_method, background_details = remove_background(opened, args.background)
        crop, crop_box = crop_visible(rgba, args.alpha_threshold, args.margin_ratio)
        cropped[view_name] = crop
        processed[view_name] = {
            "source": str(path.resolve()),
            "source_sha256": sha256_file(path),
            "source_size": list(rgba.size),
            "background_method": background_method,
            "background_details": background_details,
            "crop_box": crop_box,
            "crop_size": list(crop.size),
        }

    if args.mirror_right_from_left:
        cropped["right"] = cropped["left"].transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        processed["right"] = {
            "source": str(args.left.resolve()),
            "source_sha256": sha256_file(args.left),
            "derived_from": "left",
            "mirrored": True,
            "crop_size": list(cropped["right"].size),
        }

    max_crop_width = max(image.width for image in cropped.values())
    max_crop_height = max(image.height for image in cropped.values())
    target_width = args.size * args.max_width
    target_height = args.size * args.max_height
    common_scale = min(target_width / max_crop_width, target_height / max_crop_height)

    views_dir = args.output_dir / "views"
    views_dir.mkdir(parents=True, exist_ok=True)
    normalized: dict[str, Image.Image] = {}
    baseline_y = int(round(args.size * args.baseline))

    for view_name in (name for name in VIEW_ORDER if name in cropped):
        crop = cropped[view_name]
        if args.scale_mode == "common":
            scale = common_scale
        else:
            scale = min(target_width / crop.width, target_height / crop.height)
        resized_size = (int(round(crop.width * scale)), int(round(crop.height * scale)))
        resized = premultiplied_resize(crop, resized_size)
        canvas = Image.new("RGBA", (args.size, args.size), (0, 0, 0, 0))
        offset_x = (args.size - resized.width) // 2
        offset_y = baseline_y - resized.height
        if offset_y < 0:
            raise SystemExit(f"{view_name} does not fit above the requested baseline")
        canvas.alpha_composite(resized, (offset_x, offset_y))
        output_path = views_dir / f"{view_name}.png"
        canvas.save(output_path, format="PNG", optimize=True)
        normalized[view_name] = canvas
        processed[view_name].update(
            {
                "scale": round(scale, 8),
                "resized_size": list(resized.size),
                "offset": [offset_x, offset_y],
                "output": str(output_path.resolve()),
                "output_sha256": sha256_file(output_path),
            }
        )

    contact_path = args.output_dir / "views-contact-sheet.png"
    make_contact_sheet(normalized, contact_path)
    manifest = {
        "schema_version": "1.0",
        "tool": "prepare_character_views.py",
        "tool_version": VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "character_name": args.character_name,
        "identity_anchors": args.anchor,
        "asymmetry_notes": args.asymmetry_note,
        "canvas": [args.size, args.size],
        "baseline_ratio": args.baseline,
        "baseline_y": baseline_y,
        "scale_mode": args.scale_mode,
        "alpha_threshold": args.alpha_threshold,
        "views": processed,
        "contact_sheet": str(contact_path.resolve()),
    }
    manifest_path = views_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "ok", "views": list(normalized), "manifest": str(manifest_path), "contact_sheet": str(contact_path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
