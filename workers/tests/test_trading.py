import unittest
import importlib
import sys
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta, timezone
from types import ModuleType, SimpleNamespace
from trader.decisions import qualifies, order_quantity, exit_reason, age_seconds


class TradingTests(unittest.TestCase):
    def setUp(self):
        self.now=datetime(2026,11,4,15,tzinfo=timezone.utc)
        self.settings=SimpleNamespace(max_signal_age_seconds=900,max_quote_age_seconds=120,
            min_signal_score=60,min_profit_probability=.6,min_share_price=5,max_order_notional=100,
            max_equity_fraction=.01,max_holding_days=5,stop_loss_fraction=.05,take_profit_fraction=.1)
        self.signal={"model_version":"normal-log-returns-v1","analysis":{"direction":"long"},
            "score":75,"probability_profit":.7,"expected_return":.01,
            "news_event":{"provider":"alpaca","source":"news","published_at":self.now.isoformat()},
            "market_snapshot":{"price_observed_at":self.now.isoformat()}}

    def test_only_fresh_nonseed_native_signals_qualify(self):
        self.assertTrue(qualifies(self.signal,self.now,self.settings))
        for key,value in (("model_version","baseline-v1"),("score",59),("probability_profit",.59),("expected_return",-.01),("score",float("nan"))):
            with self.subTest(key=key,value=value):
                self.assertFalse(qualifies({**self.signal,key:value},self.now,self.settings))
        for provider in ("seed","test"):
            self.assertFalse(qualifies({**self.signal,"news_event":{**self.signal["news_event"],"provider":provider}},self.now,self.settings))
        self.assertFalse(qualifies(self.signal,self.now+timedelta(minutes=20),self.settings))
        self.assertFalse(qualifies({**self.signal,"market_snapshot":{"price_observed_at":None}},self.now,self.settings))

    def test_budget_is_cash_capped_integer_sizing(self):
        account={"status":"ACTIVE","equity":"10000","cash":"75","buying_power":"100000"}
        self.assertEqual(order_quantity(account,20,self.settings),3)
        self.assertEqual(order_quantity({**account,"trading_blocked":True},20,self.settings),0)
        self.assertEqual(order_quantity(account,1,self.settings),0)
        self.assertEqual(order_quantity(account,float("nan"),self.settings),0)
        self.assertEqual(order_quantity({**account,"cash":"-1"},20,self.settings),0)

    def test_explicit_exit_rules(self):
        position={"avg_entry_price":100,"opened_at":self.now.isoformat()}
        self.assertEqual(exit_reason(position,94,self.now,self.settings),"stop_loss")
        self.assertEqual(exit_reason(position,111,self.now,self.settings),"take_profit")
        self.assertIsNone(exit_reason(position,102,self.now,self.settings))
        self.assertEqual(exit_reason(position,float("nan"),self.now+timedelta(days=5),self.settings),"max_holding_period")
        self.assertIsNone(age_seconds((self.now+timedelta(seconds=1)).isoformat(),self.now))

    def test_reserved_entry_uses_persisted_limit_and_stops_after_three_attempts(self):
        repository=ModuleType("news.repository")
        repository.supabase=MagicMock()
        with patch.dict(sys.modules,{"news.repository":repository}):
            reconcile=importlib.import_module("trader.reconcile")
        intent={"id":"local","client_order_id":"hzn-entry","ticker":"AAPL","side":"buy",
                "quantity":2,"status":"pending_submit","limit_price":25,"submission_attempts":0}
        with patch.object(reconcile,"supabase"), patch.object(reconcile,"apply_broker_order") as apply, \
             patch.object(reconcile.broker,"submit_order",return_value={"id":"broker"}) as submit:
            reconcile.send_reserved_order(intent)
            self.assertEqual(submit.call_args.args[0]["type"],"limit")
            self.assertEqual(submit.call_args.args[0]["limit_price"],"25")
            apply.assert_called_once()
            reconcile.send_reserved_order({**intent,"submission_attempts":3})
            self.assertEqual(submit.call_count,1)
