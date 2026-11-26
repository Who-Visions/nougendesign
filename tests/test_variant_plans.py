import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
loader = importlib.util.spec_from_file_location('variant_plans', ROOT / 'tools/variant_plans.py')
vp = importlib.util.module_from_spec(loader)
loader.loader.exec_module(vp)

VARIANTS = ROOT / 'designs/nougenai-brand/variants'


def good_plan(**overrides):
    plan = {
        'variant': 'test-plan',
        'status': 'candidate',
        'package': 'nougenai-brand',
        'surface': 'fleet-boards',
        'summary': 'Does a thing.',
        'lock_effect': 'The thing becomes permanent.',
        'mutations': [{'selector': '.x', 'change': 'Make it so.'}],
    }
    plan.update(overrides)
    return plan


class ValidateTests(unittest.TestCase):
    def _write(self, tmp, plan):
        path = Path(tmp) / 'plan.json'
        path.write_text(json.dumps(plan))
        return path

    def test_shipped_plans_are_valid(self):
        for path in vp.collect_plans(VARIANTS):
            self.assertEqual(vp.validate_plan(path), [], path)

    def test_good_plan_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(vp.validate_plan(self._write(tmp, good_plan())), [])

    def test_locked_status_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            errors = vp.validate_plan(self._write(tmp, good_plan(status='locked')))
            self.assertTrue(any('candidate' in e for e in errors))

    def test_empty_mutations_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            errors = vp.validate_plan(self._write(tmp, good_plan(mutations=[])))
            self.assertTrue(any('non-empty' in e for e in errors))


class DiffTests(unittest.TestCase):
    def test_added_removed_changed(self):
        before = [{'selector': '.a', 'change': 'one'},
                  {'selector': '.b', 'change': 'two'},
                  {'selector': '.c', 'change': 'three'}]
        after = [{'selector': '.a', 'change': 'one'},
                 {'selector': '.b', 'change': 'TWO'},
                 {'selector': '.d', 'change': 'four'}]
        result = vp.diff_mutations(before, after)
        self.assertEqual([m['selector'] for m in result['added']], ['.d'])
        self.assertEqual([m['selector'] for m in result['removed']], ['.c'])
        self.assertEqual([m['selector'] for m in result['changed']], ['.b'])
        self.assertEqual(result['unchanged'], ['.a'])

    def test_bare_mutations_list_unwrapped(self):
        base = json.loads((ROOT / 'designs/nougenai-brand/mutations.json').read_text())
        self.assertEqual(vp.mutations_of(base), base)


class IndexTests(unittest.TestCase):
    def test_index_names_lock_effect(self):
        plans = [vp.load_plan(p) for p in vp.collect_plans(VARIANTS)]
        text = vp.render_index(plans)
        self.assertIn('applied only on Dave', text)
        for plan in plans:
            self.assertIn(plan['variant'], text)
            self.assertIn(plan['lock_effect'], text)


if __name__ == '__main__':
    unittest.main()
