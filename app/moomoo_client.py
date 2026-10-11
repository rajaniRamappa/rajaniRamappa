import asyncio
import moomoo as ft
from app.config import settings
from app.ws_manager import WebSocketManager
from app.alert_engine import AlertEngine
from app.handlers.quote_handler import QuoteHandler
from app.handlers.kline_handler import KlineHandler
from app.handlers.order_handler import OrderHandler

_SUB_TYPES = [
    ft.SubType.QUOTE,
    ft.SubType.K_1M,
    ft.SubType.K_5M,
    ft.SubType.K_15M,
]

_KTYPE_MAP = {
    "1min": ft.KLType.K_1M,
    "5min": ft.KLType.K_5M,
    "15min": ft.KLType.K_15M,
}

_TRD_ENV_MAP = {
    "REAL": ft.TrdEnv.REAL,
    "SIMULATE": ft.TrdEnv.SIMULATE,
}


class MoomooClient:
    def __init__(self, ws_manager: WebSocketManager, alert_engine: AlertEngine):
        self.ws = ws_manager
        self.alert_engine = alert_engine
        self.quote_ctx: ft.OpenQuoteContext = None
        self.trade_ctx: ft.OpenSecTradeContext = None
        self._loop: asyncio.AbstractEventLoop = None
        self._trade_unlocked = False
        self._subscribed_symbols: set = set()

    async def connect(self):
        self._loop = asyncio.get_running_loop()

        self.quote_ctx = ft.OpenQuoteContext(
            host=settings.opend_host,
            port=settings.opend_port,
        )
        self.trade_ctx = ft.OpenSecTradeContext(
            filter_trdmarket=ft.TrdMarket.SG,
            host=settings.opend_host,
            port=settings.opend_port,
            security_firm=ft.SecurityFirm.FUTUSECURITIES,
        )

        self.quote_ctx.set_handler(QuoteHandler(self.ws, self.alert_engine, self._loop))
        self.quote_ctx.set_handler(KlineHandler(self.ws, self._loop))
        self.trade_ctx.set_handler(OrderHandler(self.ws, self._loop))

        for symbol in settings.default_symbols:
            await self.subscribe_symbol(symbol)

    async def subscribe_symbol(self, symbol: str) -> tuple:
        loop = asyncio.get_running_loop()
        ret, msg = await loop.run_in_executor(
            None,
            lambda: self.quote_ctx.subscribe(symbol, _SUB_TYPES, is_first_push=True),
        )
        if ret == ft.RET_OK:
            self._subscribed_symbols.add(symbol)
        return ret, msg

    async def unsubscribe_symbol(self, symbol: str) -> tuple:
        loop = asyncio.get_running_loop()
        ret, msg = await loop.run_in_executor(
            None,
            lambda: self.quote_ctx.unsubscribe(symbol, _SUB_TYPES),
        )
        if ret == ft.RET_OK:
            self._subscribed_symbols.discard(symbol)
        return ret, msg

    def unlock_trade(self, password: str) -> tuple:
        ret, data = self.trade_ctx.unlock_trade(password=password)
        if ret == ft.RET_OK:
            self._trade_unlocked = True
        return ret, data

    def _trd_env(self) -> ft.TrdEnv:
        return _TRD_ENV_MAP.get(settings.trade_env, ft.TrdEnv.REAL)

    def get_account_info(self) -> dict:
        ret, data = self.trade_ctx.accinfo_query(trd_env=self._trd_env())
        if ret != ft.RET_OK:
            return {"error": str(data)}
        row = data.iloc[0]
        return {
            "cash": float(row.get("cash", 0)),
            "total_assets": float(row.get("total_assets", 0)),
            "market_val": float(row.get("market_val", 0)),
            "unrealized_pl": float(row.get("unrealized_pl", 0)),
            "realized_pl": float(row.get("realized_pl", 0)),
        }

    def get_positions(self) -> list:
        ret, data = self.trade_ctx.position_list_query(trd_env=self._trd_env())
        if ret != ft.RET_OK:
            return []
        cols = ["code", "stock_name", "qty", "cost_price", "market_val", "pl_val", "pl_ratio"]
        return data[[c for c in cols if c in data.columns]].to_dict(orient="records")

    def get_orders(self) -> list:
        ret, data = self.trade_ctx.order_list_query(trd_env=self._trd_env())
        if ret != ft.RET_OK:
            return []
        cols = ["order_id", "code", "stock_name", "trd_side", "order_type",
                "order_status", "qty", "price", "create_time"]
        return data[[c for c in cols if c in data.columns]].to_dict(orient="records")

    def place_order(self, code: str, trd_side: str, order_type: str,
                    qty: int, price: float = None) -> dict:
        if not self._trade_unlocked:
            return {"error": "Trading is locked. Enter your trade password first."}
        side = ft.TrdSide.BUY if trd_side == "BUY" else ft.TrdSide.SELL
        otype = ft.OrderType.NORMAL if order_type == "LIMIT" else ft.OrderType.MARKET
        kwargs = dict(
            code=code,
            qty=qty,
            trd_side=side,
            order_type=otype,
            trd_env=self._trd_env(),
            trd_market=ft.TrdMarket.SG,
        )
        if price is not None and order_type == "LIMIT":
            kwargs["price"] = float(price)
        ret, data = self.trade_ctx.place_order(**kwargs)
        if ret != ft.RET_OK:
            return {"error": str(data)}
        return {"order_id": str(data["order_id"].iloc[0])}

    def cancel_order(self, order_id: str) -> dict:
        ret, data = self.trade_ctx.modify_order(
            modify_order_op=ft.ModifyOrderOp.CANCEL,
            order_id=order_id,
            qty=0,
            price=0,
            trd_env=self._trd_env(),
        )
        if ret != ft.RET_OK:
            return {"error": str(data)}
        return {"ok": True}

    def get_klines(self, code: str, ktype: str, num: int = 120) -> list:
        kl = _KTYPE_MAP.get(ktype, ft.KLType.K_1M)
        ret, data = self.quote_ctx.get_cur_kline(code, num=num, ktype=kl)
        if ret != ft.RET_OK:
            return []
        cols = ["time_key", "open", "close", "high", "low", "volume"]
        return data[[c for c in cols if c in data.columns]].to_dict(orient="records")

    def get_snapshot(self, code: str) -> dict:
        ret, data = self.quote_ctx.get_market_snapshot([code])
        if ret != ft.RET_OK:
            return {"error": str(data)}
        row = data.iloc[0]
        return {
            "code": code,
            "last_price": float(row.get("last_price", 0)),
            "volume": int(row.get("volume", 0)),
            "bid_price": float(row.get("bid_price", 0)),
            "ask_price": float(row.get("ask_price", 0)),
            "open_price": float(row.get("open_price", 0)),
            "high_price": float(row.get("high_price", 0)),
            "low_price": float(row.get("low_price", 0)),
            "prev_close": float(row.get("prev_close_price", 0)),
        }

    async def disconnect(self):
        if self.quote_ctx:
            self.quote_ctx.close()
        if self.trade_ctx:
            self.trade_ctx.close()
