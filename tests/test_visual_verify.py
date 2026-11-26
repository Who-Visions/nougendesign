import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
loader = importlib.util.spec_from_file_location('visual_verify', ROOT / 'tools/visual_verify.py')
vv = importlib.util.module_from_spec(loader)
loader.loader.exec_module(vv)

BRAND = ROOT / 'designs/nougenai-brand'


class ContrastTests(unittest.TestCase):
    def test_black_on_white_is_21(self):
        self.assertAlmostEqual(vv.contrast_ratio('#000000', '#ffffff'), 21.0, places=1)

    def test_same_colour_is_1(self):
        self.assertAlmostEqual(vv.contrast_ratio('#73fd7c', '#73fd7c'), 1.0, places=2)

    def test_short_hex_expands(self):
        self.assertAlmostEqual(vv.contrast_ratio('#000', '#fff'), 21.0, places=1)


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.tokens, self.spec = vv.package_tokens(BRAND)

    def test_tokens_loaded(self):
        self.assertEqual(self.tokens['--brand'], '#73fd7c')
        self.assertEqual(self.tokens['--accent'], '#d4af37')
        self.assertIn('--shard', self.tokens)

    def test_declared_pairs_all_resolve_and_pass(self):
        findings = vv.check_contrast(self.spec, self.tokens)
        self.assertTrue(findings)
        self.assertFalse([f for f in findings if f['severity'] == 'fail'])

    def test_pinned_asset_matches_its_pin(self):
        findings = vv.check_asset_parity(self.spec, BRAND, '<p>no mark here</p>', BRAND)
        parity = [f for f in findings if f['selector'] == 'assets/n-pin.webp']
        self.assertTrue(parity and parity[0]['severity'] == 'info')


class SurfaceScanTests(unittest.TestCase):
    def setUp(self):
        self.tokens, self.spec = vv.package_tokens(BRAND)

    def test_off_palette_flags_unknown_colour_only(self):
        findings = vv.check_off_palette('a{color:#73fd7c} b{color:#123456}', self.tokens, self.spec)
        self.assertEqual([f['selector'] for f in findings], ['#123456'])

    def test_anti_patterns_caught(self):
        css = ('a{background:linear-gradient(red,blue)} '
               'b{box-shadow:0 0 24px #73fd7c} c{border-radius:32px}')
        checks = {f['selector'] for f in vv.check_anti_patterns(css)}
        self.assertEqual(checks, {'gradient', 'box-shadow', 'border-radius'})

    def test_clean_css_passes(self):
        self.assertEqual(vv.check_anti_patterns('a{border-radius:4px; box-shadow:0 1px 2px #000}'), [])


class AssetParitySurfaceTests(unittest.TestCase):
    def test_surface_serving_wrong_bytes_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            fake = tmp / 'n-pin.webp'
            fake.write_bytes(b'not the pinned mark')
            html = '<img src="n-pin.webp">'
            _, spec = vv.package_tokens(BRAND)
            findings = vv.check_asset_parity(spec, BRAND, html, tmp)
            surface = [f for f in findings if 'img' in f['selector']]
            self.assertTrue(surface and surface[0]['severity'] == 'fail')


if __name__ == '__main__':
    unittest.main()
