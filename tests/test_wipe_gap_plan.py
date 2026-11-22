import unittest

from scripts.wipe_gap_plan import (cuts_passed, item_shift, overlay_local, pick_cut, split_ranges, subtitle_shift,
                                   video_fillers, wipe_ranges, wipe_record, whoosh_record)

CUTS = [782, 1546, 3150, 4189, 5357, 6464]
WIPES = [782, 1546, 3141, 4180, 5348, 6464]
G = 96


class WipeGapPlanTests(unittest.TestCase):
    def test_bunny_ep1_shifts(self):
        self.assertEqual(item_shift(883, CUTS, G), 96)
        self.assertEqual(item_shift(8323, CUTS, G), 576)
        self.assertEqual(cuts_passed(782, CUTS), 1)
        self.assertEqual(wipe_record(782, CUTS, G), 782)          # a wipe at a cut does not move by that cut
        self.assertEqual(wipe_record(3141, CUTS, G), 3333)        # ch05 starts 9 frames before its cut
        self.assertEqual(whoosh_record(4180, CUTS, G), 4466)

    def test_subtitle_rule_uses_the_end(self):
        self.assertEqual(subtitle_shift(4180, 4237, CUTS, G), 384)   # starts before the cut, ends after it
        self.assertEqual(subtitle_shift(4122, 4164, CUTS, G), 288)
        self.assertEqual(subtitle_shift(6466, 6531, CUTS, G), 576)

    def test_wipe_ranges_match_the_placed_overlays(self):
        wipes = [782, 1546, 3141, 4180, 5348, 6464]
        starts = [782, 1546, 2437, 3141, 4180, 5348, 6464, 7347]   # ch04 (2437) has no card
        self.assertEqual(wipe_ranges(wipes, starts, CUTS, G),
                         [(782, 782, 860), (1546, 1642, 987), (3141, 3333, 1135),
                          (4180, 4468, 1264), (5348, 5732, 1212), (6464, 6944, 979)])

    def test_wipe_ranges_reject_bad_input(self):
        with self.assertRaises(ValueError):
            wipe_ranges([782, 1546], [782, 1546], CUTS, G)
        with self.assertRaises(ValueError):
            wipe_ranges([782, 1600], [782, 1546, 2437], CUTS, G)

    def test_overlay_local_time(self):
        self.assertEqual(overlay_local(14.7, 782, 60, 1.6), 3.2667)
        self.assertEqual(overlay_local(52.35, 3141, 60, 1.6), 1.6)

    def test_split_and_fillers(self):
        self.assertEqual(split_ranges(0, 8376, CUTS), [(0, 782), (782, 1546), (1546, 3150), (3150, 4189),
                                                       (4189, 5357), (5357, 6464), (6464, 8376)])
        self.assertEqual(video_fillers(CUTS, G)[0], (782, 878, 686))
        self.assertEqual(video_fillers(CUTS, G)[-1], (6944, 7040, 6368))
        rows = video_fillers(CUTS, G)
        pieces = [(s + item_shift(s, CUTS, G), e + item_shift(s, CUTS, G)) for s, e in split_ranges(0, 8376, CUTS)]
        all_rows = sorted([(a, b) for a, b, _ in rows] + pieces)
        self.assertTrue(all(a[1] == b[0] for a, b in zip(all_rows, all_rows[1:])), 'V1 must stay contiguous')

    def test_pick_cut_lands_in_the_pause(self):
        db = [-20.0] * 130 + [-60.0] * 20 + [-20.0] * 50   # silence 1.30-1.50 s, speech at 1.50
        self.assertEqual(pick_cut(db, 1.50, 96, 60), 78)    # 1.50 - 1.6 < pause start -> earliest silent frame (1.30)
        db2 = [-20.0] * 150 + [-60.0] * 30 + [-20.0] * 50  # silence 1.50-1.80, speech 1.80
        self.assertEqual(pick_cut(db2, 1.80, 96, 60), 90)   # 1.80 - 1.6 = 0.20 -> clamped to 1.50 s
        self.assertIsNone(pick_cut([-20.0] * 300, 1.50, 96, 60))
        self.assertIsNone(pick_cut([-20.0] * 149 + [-60.0] * 5 + [-20.0] * 50, 1.54, 96, 60))


if __name__ == '__main__':
    unittest.main()
