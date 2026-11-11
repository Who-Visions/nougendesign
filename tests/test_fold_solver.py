import unittest
from fold_solver import Viewport, UIElement, FoldSolver


class TestFoldFormulas(unittest.TestCase):
    def setUp(self):
        # 1440x900 MacBook Air / Standard Desktop
        self.vp = Viewport(width=1440, height=900, inset_top=64, inset_bottom=0)
        self.solver = FoldSolver(self.vp)

    def test_viewport_insets(self):
        # Fy = H - I_top - I_bottom = 900 - 64 - 0 = 836
        self.assertEqual(self.vp.fy, 836.0)
        self.assertEqual(self.vp.area_above_fold, 1440 * 836)

    def test_above_fold_factor(self):
        # Element 1: fully above fold (y=0, h=400)
        e1 = UIElement(name="hero_text", y=0, height=400, width=700)
        self.assertEqual(e1.compute_af(self.vp), 1.0)

        # Element 2: crosses fold (y=700, h=300) -> visible range 700 to 836 = 136px
        e2 = UIElement(name="countdown", y=700, height=300, width=1200)
        expected_af = 136.0 / 300.0
        self.assertAlmostEqual(e2.compute_af(self.vp), expected_af, places=4)

        # Element 3: below fold (y=900, h=500)
        e3 = UIElement(name="experiences", y=900, height=500, width=1200)
        self.assertEqual(e3.compute_af(self.vp), 0.0)

    def test_placement_priority(self):
        # Critical action element
        action_elem = UIElement(
            name="rsvp_button",
            y=200,
            height=50,
            width=200,
            goal_relevance=1.0,
            urgency=1.0,
            actionability=1.0,
            context_fit=1.0,
            complexity=0.05,
            distraction=0.0,
        )
        self.assertGreaterEqual(action_elem.priority_score(), 0.95)
        self.assertEqual(self.solver.classify_placement(action_elem), "ABOVE_FOLD")

        # Low urgency footer element
        footer = UIElement(
            name="disclaimer",
            y=1200,
            height=100,
            width=1000,
            goal_relevance=0.2,
            urgency=0.1,
            actionability=0.1,
            context_fit=0.5,
            complexity=0.1,
            distraction=0.1,
        )
        self.assertLess(footer.priority_score(), 0.1)
        self.assertEqual(self.solver.classify_placement(footer), "BELOW_FOLD")

    def test_continuation_peek_constraint(self):
        # 0.08H <= Peek <= 0.18H -> for H=900: 72px <= Peek <= 162px
        valid_peek = 100.0
        is_val, min_p, max_p = self.solver.verify_continuation_peek(valid_peek)
        self.assertTrue(is_val)
        self.assertEqual(min_p, 72.0)
        self.assertEqual(max_p, 162.0)

        # Too small
        self.assertFalse(self.solver.verify_continuation_peek(40.0)[0])
        # Too large
        self.assertFalse(self.solver.verify_continuation_peek(200.0)[0])

    def test_visual_intelligence_density(self):
        # Clean, high-acuity layout
        vid_high = self.solver.compute_vid(
            task_clarity=0.95,
            info_value=0.90,
            actionability=0.92,
            hierarchy=0.95,
            pixel_cost=0.30,
            cognitive_load=0.20,
            visual_noise=0.05,
            interaction_cost=0.15,
        )
        # Cluttered SaaS card wall
        vid_low = self.solver.compute_vid(
            task_clarity=0.50,
            info_value=0.50,
            actionability=0.40,
            hierarchy=0.40,
            pixel_cost=0.80,
            cognitive_load=0.85,
            visual_noise=0.70,
            interaction_cost=0.60,
        )
        self.assertGreater(vid_high, vid_low * 5.0)


if __name__ == "__main__":
    unittest.main()
