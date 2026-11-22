from __future__ import annotations

import unittest
from types import SimpleNamespace

from app.order_page import OrderPage


def _make_page(max_relogin: int, handler_result: bool = True):
    order_page = OrderPage.__new__(OrderPage)
    order_page._cfg = SimpleNamespace(max_relogin_per_run=max_relogin)
    order_page._relogin_count = 0
    order_page.filters_applied = []
    order_page.apply_campaign_filter = lambda label: order_page.filters_applied.append(label)
    calls = []

    def handler():
        calls.append(1)
        return handler_result

    order_page.relogin_handler = handler
    return order_page, calls


class SessionRecoveryTests(unittest.TestCase):
    def test_recover_relogs_and_restores_filter(self):
        order_page, calls = _make_page(max_relogin=3)
        self.assertTrue(order_page.recover_session("LIVE 20/11/2026"))
        self.assertEqual(len(calls), 1)
        self.assertEqual(order_page.filters_applied, ["LIVE 20/11/2026"])

    def test_recover_stops_at_limit(self):
        order_page, calls = _make_page(max_relogin=2)
        self.assertTrue(order_page.recover_session("x"))
        self.assertTrue(order_page.recover_session("x"))
        self.assertFalse(order_page.recover_session("x"))
        self.assertEqual(len(calls), 2)

    def test_recover_disabled_when_limit_zero(self):
        order_page, calls = _make_page(max_relogin=0)
        self.assertFalse(order_page.recover_session("x"))
        self.assertEqual(calls, [])

    def test_recover_fails_when_handler_fails(self):
        order_page, _ = _make_page(max_relogin=3, handler_result=False)
        self.assertFalse(order_page.recover_session("x"))
        self.assertEqual(order_page.filters_applied, [])

    def test_recover_without_handler(self):
        order_page, _ = _make_page(max_relogin=3)
        order_page.relogin_handler = None
        self.assertFalse(order_page.recover_session("x"))

    def test_is_logged_out_by_url(self):
        order_page = OrderPage.__new__(OrderPage)
        order_page.page = SimpleNamespace(url="https://x.tpos.vn/tpagev2/#/account/login")
        self.assertTrue(order_page.is_logged_out())


if __name__ == "__main__":
    unittest.main()
