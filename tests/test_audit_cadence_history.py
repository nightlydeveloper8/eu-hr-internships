"""Counterfactual freshness and false-saving regression tests."""
import unittest
from scripts.audit_cadence_history import run_backtest,no_hr_complete


def row(day, *, sid='official-feed', matching=0, complete=True, status='ok', req=3):
    return dict(id=sid,checked_at=day+'T10:00:00+00:00',
                matching=matching,status=status,complete=complete,
                closure_complete=complete,records_inspected=2,
                requests=req,bytes_read=100,rendered_pages=0,
                duration_seconds=2.0)


class CadenceReplayTests(unittest.TestCase):
    def test_only_known_complete_zero_hr_sources_are_eligible(self):
        for report in (
            row('2026-11-05',matching=2),
            row('2026-11-05',complete=False),
            row('2026-11-05',status='partial'),
            row('2026-11-05',status='failed')
        ):
            with self.subTest(report=report):
                self.assertFalse(no_hr_complete(report))
        self.assertTrue(no_hr_complete(row('2026-11-05')))

    def test_alternate_day_shadow_skip_and_positive_leads_are_not_ignored(self):
        days=['2026-11-05','2026-11-06','2026-11-07',
              '2026-11-08','2026-11-09','2026-11-10']
        samples={day:[row(day,matching=1 if day=='2026-11-10' else 0)]
                 for day in days}
        r,_=run_backtest(samples)
        # November 8: a would-be skip after three successful prior days.
        # Nov 10: if it were skipped following another success, we must surface
        # the positive HR signal rather than claiming zero risk.
        self.assertEqual(r['counterfactual']['source_day_skips'],2)
        self.assertEqual(r['counterfactual']['delayed_source_days'],1)
        self.assertEqual(r['counterfactual']['future_matching_leads_on_skipped_days'],1)
        self.assertEqual(r['counterfactual']['requests'],6)
        self.assertEqual(r['totals']['requests'],18)

    def test_incomplete_source_does_not_enter_skip_policy(self):
        days=['2026-11-05','2026-11-06','2026-11-07','2026-11-08']
        r,_=run_backtest({day:[row(day,status='partial')]
                          for day in days})
        self.assertEqual(r['counterfactual']['source_day_skips'],0)

    def test_missing_observation_breaks_streak(self):
        days=['2026-11-05','2026-11-06','2026-11-07','2026-11-10']
        r,_=run_backtest({day:[row(day)] for day in days})
        self.assertEqual(r['counterfactual']['source_day_skips'],0)


if __name__=='__main__':unittest.main()
