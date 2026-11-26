import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(name):
    loader = importlib.util.spec_from_file_location(name, ROOT / f'tools/{name}.py')
    mod = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(mod)
    return mod


tm = _load('tweaks_manifest')
vp = _load('variant_plans')

MANIFEST = ROOT / 'designs/nougenai-brand/tweaks/manifest.json'
PACKAGE = ROOT / 'designs/nougenai-brand/design.json'


def spec():
    return json.loads(PACKAGE.read_text())


def good_dimension(**overrides):
    dim = {
        'id': 'accent-role',
        'label': 'Emphasis colour',
        'kind': 'token-enum',
        'values': [{'value': 'gold', 'token': '--accent'},
                   {'value': 'brand-green', 'token': '--brand'}],
        'default': 'gold',
        'effect': {'selector': '.x', 'change': 'Use {token} ({resolved}).'},
    }
    dim.update(overrides)
    return dim


class ValidateManifestTests(unittest.TestCase):
    def test_shipped_manifest_is_valid(self):
        self.assertEqual(tm.validate_manifest(MANIFEST), [])

    def test_locked_status_rejected(self):
        data = json.loads(MANIFEST.read_text())
        data['status'] = 'locked'
        with tempfile.TemporaryDirectory() as tmp:
            # manifest must sit in <pkg>/tweaks/ for the package lookup
            tweaks = Path(tmp) / 'tweaks'
            tweaks.mkdir()
            (Path(tmp) / 'design.json').write_text(PACKAGE.read_text())
            path = tweaks / 'manifest.json'
            path.write_text(json.dumps(data))
            errors = tm.validate_manifest(path)
        self.assertTrue(any('candidate' in e for e in errors))

    def test_wrong_dialect_rejected(self):
        data = json.loads(MANIFEST.read_text())
        data['dialect'] = 'tweaks/v99'
        with tempfile.TemporaryDirectory() as tmp:
            tweaks = Path(tmp) / 'tweaks'
            tweaks.mkdir()
            (Path(tmp) / 'design.json').write_text(PACKAGE.read_text())
            path = tweaks / 'manifest.json'
            path.write_text(json.dumps(data))
            errors = tm.validate_manifest(path)
        self.assertTrue(any('tweaks/v1' in e for e in errors))


class ValidateDimensionTests(unittest.TestCase):
    def test_good_dimension_passes(self):
        self.assertEqual(tm.validate_dimension(good_dimension(), spec(), 't'), [])

    def test_off_package_token_rejected(self):
        dim = good_dimension(values=[{'value': 'gold', 'token': '--accent'},
                                     {'value': 'nope', 'token': '--not-a-token'}],
                             default='gold')
        errors = tm.validate_dimension(dim, spec(), 't')
        self.assertTrue(any('--not-a-token' in e for e in errors))

    def test_unknown_theme_rejected(self):
        dim = good_dimension(kind='theme', values=['base', 'sepia'], default='base')
        dim.pop('token', None)
        errors = tm.validate_dimension(dim, spec(), 't')
        self.assertTrue(any('sepia' in e for e in errors))

    def test_step_ladder_must_pass_through_locked_value(self):
        # --cluster-gap is 1.25rem; a ladder whose default step holds a
        # different value would silently move the locked default.
        dim = good_dimension(
            kind='token-step', token='--cluster-gap',
            steps=['--space-4', '--space-6'], default='--space-4')
        dim.pop('values')
        errors = tm.validate_dimension(dim, spec(), 't')
        self.assertTrue(any('ladder' in e for e in errors))

    def test_non_monotonic_ladder_rejected(self):
        dim = good_dimension(
            kind='token-step', token='--cluster-gap',
            steps=['--space-4', '--space-6', '--cluster-gap'],
            default='--cluster-gap')
        dim.pop('values')
        errors = tm.validate_dimension(dim, spec(), 't')
        self.assertTrue(any('monotonic' in e for e in errors))

    def test_choice_value_needs_its_own_change(self):
        dim = good_dimension(kind='choice',
                             values=[{'value': 'flat', 'change': 'Flat.'},
                                     {'value': 'ghost', 'change': ''}],
                             default='flat')
        dim.pop('token', None)
        errors = tm.validate_dimension(dim, spec(), 't')
        self.assertTrue(any('choice' in e for e in errors))


class PlanTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(MANIFEST.read_text())
        self.spec = spec()

    def test_plan_is_a_valid_variant_plan(self):
        plan = tm.build_plan(self.data, self.spec,
                             {'stale-treatment': 'quiet', 'density': '--space-4'},
                             'boards-explored-quiet-compact')
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'plan.json'
            path.write_text(json.dumps(plan))
            self.assertEqual(vp.validate_plan(path), [])
        self.assertEqual(plan['status'], 'candidate')

    def test_plan_renders_resolved_values(self):
        plan = tm.build_plan(self.data, self.spec, {'density': '--space-4'}, 'boards-x')
        change = plan['mutations'][0]['change']
        self.assertIn('1rem', change)          # --space-4 resolved from the package
        self.assertIn('--space-4', change)

    def test_out_of_space_value_rejected(self):
        with self.assertRaises(ValueError):
            tm.build_plan(self.data, self.spec, {'density': '--space-1'}, 'boards-x')

    def test_off_brand_accent_inexpressible(self):
        with self.assertRaises(ValueError):
            tm.build_plan(self.data, self.spec, {'accent-role': 'purple'}, 'boards-x')

    def test_unknown_dimension_rejected(self):
        with self.assertRaises(ValueError):
            tm.build_plan(self.data, self.spec, {'font': 'serif'}, 'boards-x')

    def test_empty_settings_rejected(self):
        with self.assertRaises(ValueError):
            tm.build_plan(self.data, self.spec, {}, 'boards-x')


class IndexTests(unittest.TestCase):
    def test_index_states_the_lock_rule(self):
        data = json.loads(MANIFEST.read_text())
        text = tm.render_index(data, spec())
        self.assertIn('only when Dave locks it', text)
        for dim in data['dimensions']:
            self.assertIn(dim['id'], text)


if __name__ == '__main__':
    unittest.main()
