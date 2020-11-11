import unittest
from unittest import mock

from flumine import config
from flumine.markets.market import Market
from flumine.markets.markets import Markets
from flumine.order.order import (
    BaseOrder,
    BetfairOrder,
)
from flumine.order.process import process_current_orders
from flumine.strategy.strategy import Strategies
from flumine.utils import create_cheap_hash


class BaseOrderTest(unittest.TestCase):
    def setUp(self) -> None:
        mock_client = mock.Mock(paper_trade=False)
        self.mock_trade = mock.Mock(client=mock_client)
        self.mock_order_type = mock.Mock()
        self.order = BaseOrder(self.mock_trade, "BACK", self.mock_order_type, 1)
        config.simulated = True

    def tearDown(self) -> None:
        config.simulated = False

    def test_process_current_orders_with_default_sep(self):
        market_book = mock.Mock()
        markets = Markets()
        market = Market(
            flumine=mock.Mock(), market_id="market_id", market_book=market_book
        )

        markets.add_market("market_id", market)

        strategies = Strategies()

        cheap_hash = create_cheap_hash("strategy_name", 13)

        trade = mock.Mock(market_id="market_id")
        trade.strategy.name_hash = cheap_hash

        current_order = mock.Mock(
            customer_order_ref=f"{cheap_hash}I123", market_id="market_id", bet_id=None
        )

        betfair_order = BetfairOrder(trade=trade, side="BACK", order_type=mock.Mock())
        betfair_order.id = "123"
        market.blotter = {"123": betfair_order}

        event = mock.Mock(event=[mock.Mock(orders=[current_order])])

        process_current_orders(markets=markets, strategies=strategies, event=event)

        self.assertEqual(current_order, betfair_order.responses.current_order)