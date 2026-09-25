"""Import local travel originals into a static gallery (no network requests)."""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
from io import BytesIO
import json
import math
from pathlib import Path
import re

from PIL import Image, ImageCms, ImageOps
from pillow_heif import register_heif_opener

ROOT = Path(__file__).resolve().parents[1]
SUPPORTED = {".heic", ".heif", ".jpg", ".jpeg", ".png", ".webp"}
register_heif_opener()


def coordinates(gps):
    """Return decimal degrees, including valid equator/prime-meridian values."""
    if not gps:
        return None
    try:
        def degrees(values, ref, positive, negative):
            if isinstance(ref, bytes):
                ref = ref.decode("ascii").rstrip("\0")
            if ref not in (positive, negative) or len(values) != 3:
                raise ValueError("Invalid GPS reference")
            d, m, s = map(float, values)
            if not (0 <= m < 60 and 0 <= s < 60 and d >= 0):
                raise ValueError("Invalid GPS degrees")
            return (d + m / 60 + s / 3600) * (-1 if ref == negative else 1)
        lat = degrees(gps[2], gps[1], "N", "S")
        lon = degrees(gps[4], gps[3], "E", "W")
        if not (math.isfinite(lat) and math.isfinite(lon) and abs(lat) <= 90 and abs(lon) <= 180):
            return None
        return [round(lat, 6), round(lon, 6)]
    except (KeyError, TypeError, ValueError, ZeroDivisionError, UnicodeError):
        return None


def distance(a, b):
    lat1, lat2 = map(math.radians, (a[0], b[0]))
    dlat, dlon = math.radians(b[0] - a[0]), math.radians(b[1] - a[1])
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 6371000 * 2 * math.asin(math.sqrt(min(1, max(0, h))))


def group_places(photos, radius=250):
    """Group within a fixed anchor radius, avoiding unbounded chain merging."""
    groups = []
    for photo in photos:
        if photo["coordinates"] is None:
            photo["place_id"] = None
            continue
        group = next((g for g in groups if distance(g["coordinates"], photo["coordinates"]) <= radius), None)
        if group is None:
            group = {"id": photo["id"], "name": photo["place"], "coordinates": photo["coordinates"], "count": 0}
            groups.append(group)
        group["count"] += 1
        photo["place_id"] = group["id"]
    return groups


def import_photos(source, image_dir, manifest_path, labels):
    source, image_dir = source.resolve(), image_dir.resolve()
    if source.is_relative_to(image_dir) or image_dir.is_relative_to(source):
        raise ValueError("The originals directory and generated image directory must not overlap.")
    files = sorted(p for p in source.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED)
    if not files:
        raise ValueError(f"No supported photos in {source}; existing gallery was left unchanged.")
    photos, seen = [], set()
    image_dir.mkdir(parents=True, exist_ok=True)
    for path in files:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()[:20]
        if digest in seen:
            continue
        seen.add(digest)
        label = labels.get(path.relative_to(source).as_posix(), {})
        with Image.open(path) as original:
            exif = original.getexif()
            location = coordinates(exif.get_ifd(34853))
            raw_date = exif.get_ifd(34665).get(36867) or exif.get(306)
            try:
                taken = datetime.strptime(raw_date, "%Y:%m:%d %H:%M:%S").date().isoformat()
            except (ValueError, TypeError):
                taken = None
            place = label.get("place") or (f"{location[0]:.3f}°, {location[1]:.3f}°" if location else "Location not recorded")
            alt = label.get("alt") or f"Travel photograph at {place}"
            oriented = ImageOps.exif_transpose(original)
            icc = original.info.get("icc_profile")
            if icc:
                oriented = ImageCms.profileToProfile(oriented, ImageCms.ImageCmsProfile(BytesIO(icc)), ImageCms.createProfile("sRGB"), outputMode="RGB")
            else:
                oriented = oriented.convert("RGB")
            # New pixel-only images prevent EXIF/XMP copying into web derivatives.
            clean = Image.new("RGB", oriented.size)
            clean.paste(oriented)
            clean.thumbnail((2000, 2000), Image.Resampling.LANCZOS)
            clean.save(image_dir / f"{digest}.jpg", quality=86, optimize=True, progressive=True)
            width, height = clean.size
            clean.thumbnail((640, 640), Image.Resampling.LANCZOS)
            clean.save(image_dir / f"{digest}-thumb.jpg", quality=82, optimize=True)
        photos.append({"id": digest, "date": taken, "coordinates": location,
                       "country": label.get("country"), "city": label.get("city"),
                       "place": place, "alt": alt, "width": width, "height": height,
                       "_sort_time": raw_date or "9999",
                       "image": f"images/travel/{digest}.jpg", "thumbnail": f"images/travel/{digest}-thumb.jpg"})
        print(f"{path.name}: {taken or 'no date'} / {'GPS OK' if location else 'no GPS (gallery only)'}")
    photos.sort(key=lambda p: (p["_sort_time"], p["id"]))
    for photo in photos:
        del photo["_sort_time"]
    places = group_places(photos)
    manifest = {"version": 1, "group_radius_m": 250, "photos": photos, "places": places}
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = manifest_path.with_suffix(".tmp")
    temporary.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(manifest_path)
    # The importer owns only its hash-named derivatives, never the originals.
    for stale in image_dir.glob("*.jpg"):
        if stale.stem.removesuffix("-thumb") not in seen and re.fullmatch(r"[0-9a-f]{20}(?:-thumb)?", stale.stem):
            stale.unlink()
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "local-photos/travel-originals")
    args = parser.parse_args()
    labels_path = ROOT / "content/travel-labels.json"
    labels = json.loads(labels_path.read_text(encoding="utf-8")) if labels_path.exists() else {}
    result = import_photos(args.source.resolve(), ROOT / "images/travel", ROOT / "content/travel.json", labels)
    print(f"Imported {len(result['photos'])} photos, {len(result['places'])} places. Run scripts/site.py build next.")


if __name__ == "__main__":
    main()
