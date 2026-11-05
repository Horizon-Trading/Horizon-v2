import unittest
from src.portfolio import performance


class PortfolioTests(unittest.TestCase):
    def test_drawdown_uses_reported_performance_not_deposit_equity(self):
        result=performance({"timestamp":[1,2,3],"equity":[100,220,198],"base_value":100,"profit_loss_pct":[0,.1,-.01]})
        self.assertEqual(result["total_return"],-.01)
        self.assertAlmostEqual(result["max_drawdown"],.1)
        self.assertEqual(len(result["equity_curve"]),3)

    def test_missing_or_invalid_history_is_unavailable(self):
        for history in (None,{}, {"base_value":0,"timestamp":[1],"profit_loss_pct":[0]},
                        {"base_value":100,"timestamp":[1],"profit_loss_pct":[float("nan")]}):
            self.assertIsNone(performance(history)["total_return"])

    def test_complete_loss_is_full_drawdown(self):
        result=performance({"timestamp":[1,2],"equity":[100,0],"base_value":100,"profit_loss_pct":[0,-1]})
        self.assertEqual(result["max_drawdown"],1)
