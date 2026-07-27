#!/usr/bin/env python3
"""Extract transparent character cutouts from a labeled or unlabeled sprite sheet."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Any

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Pillow is required. Install it with: python -m pip install Pillow") from exc


VERSION = "1.0.0"
SAFE_NAME = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


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


def border_samples(image: Image.Image, count: int = 20) -> list[tuple[int, int, int]]:
    rgb = image.convert("RGB")
    pixels = rgb.load()
    samples: list[tuple[int, int, int]] = []
    for index in range(count):
        x = round(index * (rgb.width - 1) / max(1, count - 1))
        y = round(index * (rgb.height - 1) / max(1, count - 1))
        samples.extend([pixels[x, 0], pixels[x, rgb.height - 1], pixels[0, y], pixels[rgb.width - 1, y]])
    return samples


def estimate_border(image: Image.Image) -> tuple[tuple[int, int, int], float]:
    samples = border_samples(image)
    color = tuple(int(median([pixel[channel] for pixel in samples])) for channel in range(3))
    spread = median([math.dist(pixel, color) for pixel in samples])
    return color, float(spread)


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
        else:
            cleaned.append((red, min(green, max(red, blue) + 12), blue, new_alpha))
    result.putdata(cleaned)
    return result


def key_corner(image: Image.Image, color: tuple[int, int, int]) -> Image.Image:
    result = image.convert("RGBA")
    cleaned: list[tuple[int, int, int, int]] = []
    inner, outer = 14.0, 56.0
    for red, green, blue, alpha in flattened_data(result):
        distance = math.dist((red, green, blue), color)
        if distance <= inner:
            new_alpha = 0
        elif distance >= outer:
            new_alpha = alpha
        else:
            new_alpha = int(round(alpha * (distance - inner) / (outer - inner)))
        cleaned.append((red, green, blue, new_alpha))
    result.putdata(cleaned)
    return result


def remove_background(image: Image.Image, requested: str) -> tuple[Image.Image, str, dict[str, Any]]:
    rgba = image.convert("RGBA")
    if requested == "none":
        return rgba, "none", {}
    if requested == "auto" and rgba.getchannel("A").getextrema()[0] < 240:
        return rgba, "existing-alpha", {}
    color, spread = estimate_border(rgba)
    method = requested
    if requested == "auto":
        red, green, blue = color
        if green > red + 24 and green > blue + 16:
            method = "green"
        elif spread <= 30:
            method = "corner"
        else:
            method = "none"
    details = {"border_color": list(color), "border_spread": round(spread, 3)}
    if method == "green":
        return key_green(rgba), "green", details
    if method == "corner":
        return key_corner(rgba, color), "corner", details
    return rgba, "none", details


def visible_bbox(image: Image.Image, threshold: int) -> tuple[int, int, int, int] | None:
    mask = image.convert("RGBA").getchannel("A").point(lambda value: 255 if value > threshold else 0)
    return mask.getbbox()


def trim_visible(image: Image.Image, threshold: int, padding: int) -> tuple[Image.Image, list[int]]:
    bbox = visible_bbox(image, threshold)
    if bbox is None:
        raise ValueError("No visible pixels remain")
    left, top, right, bottom = bbox
    crop_box = [
        max(0, left - padding),
        max(0, top - padding),
        min(image.width, right + padding),
        min(image.height, bottom + padding),
    ]
    return image.crop(tuple(crop_box)), crop_box


def connected_components(alpha: Image.Image, threshold: int) -> list[list[int]]:
    width, height = alpha.size
    visible = bytearray(1 if value > threshold else 0 for value in flattened_data(alpha))
    visited = bytearray(width * height)
    components: list[list[int]] = []
    for start in range(width * height):
        if not visible[start] or visited[start]:
            continue
        queue: deque[int] = deque([start])
        visited[start] = 1
        component: list[int] = []
        while queue:
            index = queue.popleft()
            component.append(index)
            x = index % width
            y = index // width
            if x > 0:
                neighbor = index - 1
                if visible[neighbor] and not visited[neighbor]:
                    visited[neighbor] = 1
                    queue.append(neighbor)
            if x + 1 < width:
                neighbor = index + 1
                if visible[neighbor] and not visited[neighbor]:
                    visited[neighbor] = 1
                    queue.append(neighbor)
            if y > 0:
                neighbor = index - width
                if visible[neighbor] and not visited[neighbor]:
                    visited[neighbor] = 1
                    queue.append(neighbor)
            if y + 1 < height:
                neighbor = index + width
                if visible[neighbor] and not visited[neighbor]:
                    visited[neighbor] = 1
                    queue.append(neighbor)
        components.append(component)
    components.sort(key=len, reverse=True)
    return components


def isolate_subject(
    image: Image.Image,
    mode: str,
    threshold: int,
    keep_prop_ratio: float,
    min_component_area: int,
) -> tuple[Image.Image, dict[str, Any]]:
    rgba = image.convert("RGBA")
    if mode == "none":
        return rgba, {"mode": "none"}
    components = connected_components(rgba.getchannel("A"), threshold)
    if not components:
        raise ValueError("No connected subject was found")
    largest = len(components[0])
    if mode == "main":
        kept = [components[0]]
    else:
        minimum = max(min_component_area, int(math.ceil(largest * keep_prop_ratio)))
        kept = [component for component in components if len(component) >= minimum]
    keep_mask = bytearray(rgba.width * rgba.height)
    for component in kept:
        for index in component:
            keep_mask[index] = 1
    pixels = list(flattened_data(rgba))
    rgba.putdata([(r, g, b, a if keep_mask[index] else 0) for index, (r, g, b, a) in enumerate(pixels)])
    return rgba, {
        "mode": mode,
        "component_count": len(components),
        "kept_component_count": len(kept),
        "largest_component_area": largest,
        "kept_component_areas": [len(component) for component in kept],
    }


def parse_regions(path: Path) -> tuple[list[dict[str, Any]], str, str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    coordinate_space = "normalized"
    background = "auto"
    if isinstance(data, dict) and "regions" in data:
        regions = data["regions"]
        coordinate_space = data.get("coordinate_space", coordinate_space)
        background = data.get("background", background)
    elif isinstance(data, list):
        regions = data
    elif isinstance(data, dict):
        regions = [{"name": name, "box": box} for name, box in data.items()]
    else:
        raise ValueError("Regions JSON must be an array, a name-to-box object, or an object with a regions array")
    if coordinate_space not in {"normalized", "pixels", "auto"}:
        raise ValueError("coordinate_space must be normalized, pixels, or auto")
    if not isinstance(regions, list) or not regions:
        raise ValueError("At least one region is required")
    seen: set[str] = set()
    for region in regions:
        if not isinstance(region, dict) or "name" not in region or "box" not in region:
            raise ValueError("Every region needs name and box")
        name = str(region["name"])
        if not SAFE_NAME.fullmatch(name):
            raise ValueError(f"Unsafe region name {name!r}; use lowercase letters, numbers, _ or -")
        if name in seen:
            raise ValueError(f"Duplicate region name: {name}")
        seen.add(name)
        box = region["box"]
        if not isinstance(box, list) or len(box) != 4 or not all(isinstance(value, (int, float)) for value in box):
            raise ValueError(f"Region {name} box must be [x, y, width, height]")
    return regions, coordinate_space, background


def box_to_pixels(box: list[float], space: str, width: int, height: int) -> list[int]:
    x, y, box_width, box_height = box
    normalized = space == "normalized" or (space == "auto" and max(box) <= 1.000001)
    if normalized:
        values = [round(x * width), round(y * height), round((x + box_width) * width), round((y + box_height) * height)]
    else:
        values = [round(x), round(y), round(x + box_width), round(y + box_height)]
    left, top, right, bottom = values
    left, top = max(0, left), max(0, top)
    right, bottom = min(width, right), min(height, bottom)
    if right <= left or bottom <= top:
        raise ValueError(f"Invalid or out-of-range box: {box}")
    return [left, top, right, bottom]


def checkerboard(size: tuple[int, int], cell: int = 12) -> Image.Image:
    board = Image.new("RGBA", size, (239, 239, 239, 255))
    draw = ImageDraw.Draw(board)
    for y in range(0, size[1], cell):
        for x in range(0, size[0], cell):
            if (x // cell + y // cell) % 2:
                draw.rectangle((x, y, min(size[0], x + cell), min(size[1], y + cell)), fill=(211, 211, 211, 255))
    return board


def make_contact_sheet(items: list[tuple[str, Image.Image]], output: Path, columns: int) -> None:
    tile, label_height = 220, 34
    columns = max(1, min(columns, len(items)))
    rows = math.ceil(len(items) / columns)
    sheet = Image.new("RGB", (columns * tile, rows * (tile + label_height)), (250, 247, 240))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for index, (name, image) in enumerate(items):
        column, row = index % columns, index // columns
        preview = image.copy()
        preview.thumbnail((tile - 18, tile - 18), Image.Resampling.LANCZOS)
        background = checkerboard((tile, tile))
        background.alpha_composite(preview, ((tile - preview.width) // 2, (tile - preview.height) // 2))
        origin = (column * tile, row * (tile + label_height))
        sheet.paste(background.convert("RGB"), origin)
        text_box = draw.textbbox((0, 0), name, font=font)
        text_width = text_box[2] - text_box[0]
        draw.text((origin[0] + (tile - text_width) // 2, origin[1] + tile + 10), name, fill=(35, 35, 35), font=font)
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, format="PNG", optimize=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sheet", required=True, type=Path)
    parser.add_argument("--regions", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--key-background", choices=("auto", "none", "green", "corner"))
    parser.add_argument("--alpha-threshold", type=int, default=20)
    parser.add_argument("--padding", type=int, default=6)
    parser.add_argument("--keep-prop-ratio", type=float, default=0.15)
    parser.add_argument("--min-component-area", type=int, default=12)
    parser.add_argument("--contact-columns", type=int, default=6)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.sheet.is_file():
        raise SystemExit(f"Missing sheet: {args.sheet}")
    if not args.regions.is_file():
        raise SystemExit(f"Missing regions JSON: {args.regions}")
    if not 0 <= args.alpha_threshold <= 254:
        raise SystemExit("--alpha-threshold must be between 0 and 254")
    if args.padding < 0 or args.padding > 128:
        raise SystemExit("--padding must be between 0 and 128")
    if not 0 <= args.keep_prop_ratio <= 1:
        raise SystemExit("--keep-prop-ratio must be between 0 and 1")

    try:
        regions, coordinate_space, declared_background = parse_regions(args.regions)
    except (ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Invalid regions JSON: {exc}") from exc
    background = args.key_background or declared_background
    if background not in {"auto", "none", "green", "corner"}:
        raise SystemExit(f"Unsupported background mode: {background}")

    with Image.open(args.sheet) as opened:
        sheet = opened.convert("RGBA")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest_regions: list[dict[str, Any]] = []
    contact_items: list[tuple[str, Image.Image]] = []

    for region in regions:
        name = str(region["name"])
        try:
            pixel_box = box_to_pixels(region["box"], coordinate_space, sheet.width, sheet.height)
            crop = sheet.crop(tuple(pixel_box))
            region_background = str(region.get("background", background))
            crop, background_method, background_details = remove_background(crop, region_background)
            mode = str(region.get("isolate", "main+props"))
            if mode not in {"main", "main+props", "none"}:
                raise ValueError(f"unsupported isolate mode {mode!r}")
            ratio = float(region.get("keep_prop_ratio", args.keep_prop_ratio))
            isolated, component_details = isolate_subject(
                crop,
                mode,
                args.alpha_threshold,
                ratio,
                args.min_component_area,
            )
            trimmed, trim_box = trim_visible(isolated, args.alpha_threshold, args.padding)
        except ValueError as exc:
            raise SystemExit(f"Region {name!r} failed: {exc}") from exc

        output_path = args.output_dir / f"{name}.png"
        trimmed.save(output_path, format="PNG", optimize=True)
        contact_items.append((name, trimmed))
        manifest_regions.append(
            {
                "name": name,
                "display_name": region.get("display_name", name),
                "category": region.get("category", "cutout"),
                "source_box": region["box"],
                "pixel_box": pixel_box,
                "background_method": background_method,
                "background_details": background_details,
                "isolation": component_details,
                "trim_box": trim_box,
                "output_size": list(trimmed.size),
                "output": str(output_path.resolve()),
                "output_sha256": sha256_file(output_path),
            }
        )

    contact_path = args.output_dir / "_contact-sheet.png"
    make_contact_sheet(contact_items, contact_path, args.contact_columns)
    manifest = {
        "schema_version": "1.0",
        "tool": "extract_cutout_sheet.py",
        "tool_version": VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_sheet": str(args.sheet.resolve()),
        "source_sha256": sha256_file(args.sheet),
        "sheet_size": list(sheet.size),
        "regions_file": str(args.regions.resolve()),
        "coordinate_space": coordinate_space,
        "background": background,
        "alpha_threshold": args.alpha_threshold,
        "regions": manifest_regions,
        "contact_sheet": str(contact_path.resolve()),
    }
    manifest_path = args.output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "ok", "count": len(contact_items), "manifest": str(manifest_path), "contact_sheet": str(contact_path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
