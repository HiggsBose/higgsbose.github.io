"""Run with requirements-photos.txt installed to verify the import pipeline."""
import importlib.util
from pathlib import Path
import runpy
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
HAS_PHOTO_DEPS = all(importlib.util.find_spec(name) for name in ('PIL', 'pillow_heif'))
if HAS_PHOTO_DEPS:
    from PIL import Image
    importer = runpy.run_path(str(ROOT / 'scripts/import_travel.py'))


@unittest.skipUnless(HAS_PHOTO_DEPS, 'Install requirements-photos.txt to test photo importing')
class TravelImportTests(unittest.TestCase):
    def test_import_preserves_destination_and_actual_locality(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'originals'
            source.mkdir()
            Image.new('RGB', (20, 20), 'blue').save(source / 'pier.jpg')
            labels = {'pier.jpg': {'country': 'United States', 'city': 'Santa Monica',
                                  'destination': 'Los Angeles area', 'place': 'Santa Monica Pier'}}
            result = importer['import_photos'](source, root / 'web', root / 'travel.json', labels)
            photo = result['photos'][0]
            self.assertEqual(photo['destination'], 'Los Angeles area')
            self.assertEqual(photo['city'], 'Santa Monica')
            self.assertEqual(photo['place'], 'Santa Monica Pier')
            self.assertIsNone(photo['coordinates'])

    def test_manual_pin_fallback_and_gps_priority(self):
        resolve = importer['resolve_location']
        self.assertEqual(resolve(None, {'coordinates': [0, 0]}), ([0, 0], 'manual'))
        self.assertEqual(resolve([1, 2], {'coordinates': [3, 4]}), ([1, 2], 'exif'))
        self.assertEqual(resolve(None, {}), (None, None))
        for point in ([91, 0], [0, 181], [float('nan'), 1], [True, 0], '1,2', [1]):
            with self.assertRaises(ValueError):
                resolve(None, {'coordinates': point})

    def test_gps_hemispheres_zero_and_missing(self):
        coordinates = importer['coordinates']
        self.assertEqual(coordinates({1: 'S', 2: (33, 30, 0), 3: 'W', 4: (70, 15, 0)}), [-33.5, -70.25])
        self.assertEqual(coordinates({1: 'N', 2: (0, 0, 0), 3: 'E', 4: (0, 0, 0)}), [0, 0])
        self.assertIsNone(coordinates({}))
        self.assertIsNone(coordinates({1: 'N', 2: (91, 0, 0), 3: 'E', 4: (2, 0, 0)}))
        self.assertIsNone(coordinates({1: 'N', 2: (30, 75, 0), 3: 'E', 4: (2, 0, 0)}))

    def test_grouping_does_not_chain_merge(self):
        photos = [{'id': str(i), 'coordinates': point, 'place': str(i)} for i, point in enumerate([[0, 0], [0, .002], [0, .004], None])]
        groups = importer['group_places'](photos)
        self.assertEqual([g['count'] for g in groups], [2, 1])
        self.assertIsNone(photos[-1]['place_id'])
        self.assertLess(importer['distance']([0, 179.999], [0, -179.999]), 250)

    def test_orientation_metadata_duplicates_and_missing_gps(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'originals'
            source.mkdir()
            exif = Image.Exif()
            exif[274] = 6
            exif[306] = '2026:09:10 12:00:00'
            exif[34853] = {1: 'S', 2: (33, 30, 0), 3: 'W', 4: (70, 15, 0)}
            Image.new('RGB', (120, 80), 'red').save(source / 'one.jpg', exif=exif)
            original = (source / 'one.jpg').read_bytes()
            (source / 'duplicate.jpg').write_bytes(original)
            Image.new('RGB', (80, 90), 'blue').save(source / 'unlocated.jpg')
            result = importer['import_photos'](source, root / 'web', root / 'travel.json', {})
            self.assertEqual(len(result['photos']), 2)
            self.assertEqual(len(result['places']), 1)
            photo = next(p for p in result['photos'] if p['coordinates'])
            self.assertEqual(photo['coordinates'], [-33.5, -70.25])
            self.assertEqual((photo['width'], photo['height']), (80, 120))
            self.assertEqual(photo['date'], '2026-09-10')
            for path in (root / 'web').glob('*.jpg'):
                with Image.open(path) as image:
                    self.assertFalse(image.getexif())
            self.assertEqual((source / 'one.jpg').read_bytes(), original)

    def test_empty_source_preserves_existing_gallery(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'originals').mkdir()
            manifest = root / 'travel.json'
            manifest.write_text('existing')
            with self.assertRaises(ValueError):
                importer['import_photos'](root / 'originals', root / 'web', manifest, {})
            self.assertEqual(manifest.read_text(), 'existing')

    def test_output_cannot_replace_originals(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaises(ValueError):
                importer['import_photos'](root, root / 'web', root / 'travel.json', {})
