import asyncio
import moomoo as ft
from app.ws_manager import WebSocketManager


class QuoteHandler(ft.StockQuoteHandlerBase):
    def __init__(self, ws_manager: WebSocketManager, alert_engine, loop: asyncio.AbstractEventLoop):
        super().__init__()
        self.ws = ws_manager
        self.alert_engine = alert_engine
        self.loop = loop

    def on_recv_rsp(self, rsp_pb):
        ret, data = super().on_recv_rsp(rsp_pb)
        if ret != ft.RET_OK:
            return ret, data
        for _, row in data.iterrows():
            prev_close = float(row.get("prev_close_price", 0))
            last_price = float(row.get("last_price", 0))
            change_pct = (
                round((last_price - prev_close) / prev_close * 100, 2)
                if prev_close > 0
                else 0.0
            )
            msg = {
                "type": "quote",
                "code": row["code"],
                "last_price": last_price,
                "open_price": float(row.get("open_price", 0)),
                "high_price": float(row.get("high_price", 0)),
                "low_price": float(row.get("low_price", 0)),
                "prev_close": prev_close,
                "volume": int(row.get("volume", 0)),
                "turnover": float(row.get("turnover", 0)),
                "change_pct": change_pct,
            }
            asyncio.run_coroutine_threadsafe(self.ws.broadcast(msg), self.loop)
            asyncio.run_coroutine_threadsafe(
                self.alert_engine.evaluate(row["code"], last_price), self.loop
            )
        return ret, data
