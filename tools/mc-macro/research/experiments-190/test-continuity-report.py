import unittest
from summarize_app_trials import continuity


def pose(t, x, ground, phase):
    return (t, x, 80, 0, 0, 45, ground, phase)


class ContinuityReportTests(unittest.TestCase):
    def test_survival_does_not_hide_repair_or_final_release(self):
        poses = [pose(0, 0, True, 'preparing'), pose(.1, .1, False, 'takeoff'),
                 pose(.6, 2, True, 'landing'), pose(.65, 2, True, 'flight'),
                 pose(.7, 2, True, 'flight'), pose(.75, 2, True, 'landing'),
                 pose(.8, 2.1, False, 'takeoff'),
                 pose(1.3, 4, True, 'landing'), pose(1.35, 4, True, 'flight')]
        result = continuity(poses, [.67, 1.37], 1.0)
        self.assertEqual(result['return_to_placement_count'], 1)
        self.assertEqual(result['grounded_clicks_observed'], 1)
        self.assertEqual(result['completed_ground_dwell_count'], 1)
        self.assertAlmostEqual(result['stationary_ground_seconds'], .15)
        self.assertFalse(result['continuous_acceptance'])

    def test_moving_ground_contact_is_not_a_repair_loop(self):
        result = continuity([pose(0, 0, False, 'flight'), pose(.1, 1, True, 'landing'),
                             pose(.15, 1.2, True, 'runup'), pose(.2, 1.4, False, 'takeoff')], [], .3)
        self.assertEqual(result['return_to_placement_count'], 0)
        self.assertEqual(result['stationary_ground_seconds'], 0)
        self.assertFalse(result['continuous_acceptance'])

    def test_stale_ground_sample_is_unknown(self):
        result = continuity([pose(0, 0, False, 'flight'), pose(.1, 1, True, 'flight')], [.3], None)
        self.assertEqual(result['grounded_clicks_observed'], 0)
        self.assertEqual(result['clicks_without_fresh_ground_sample'], 1)

    def test_backing_after_opening_is_counted_but_release_is_excluded(self):
        result = continuity([pose(0, 0, True, 'backing'),
                             pose(.1, .1, False, 'takeoff'),
                             pose(.6, 2, True, 'landing'),
                             pose(.65, 2, True, 'backing'),
                             pose(.7, 1.9, True, 'backing'),
                             pose(.8, 2, True, 'runup'),
                             pose(.9, 2, True, 'backing')], [], .85)
        self.assertEqual(result['repeat_runup_count'], 1)
        self.assertEqual(result['repeat_runup_times'], [.65])


if __name__ == '__main__':
    unittest.main()
