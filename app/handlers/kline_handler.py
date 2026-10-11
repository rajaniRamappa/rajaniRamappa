import asyncio
import moomoo as ft
from app.ws_manager import WebSocketManager


class KlineHandler(ft.CurKlineHandlerBase):
    def __init__(self, ws_manager: WebSocketManager, loop: asyncio.AbstractEventLoop):
        super().__init__()
        self.ws = ws_manager
        self.loop = loop

    def on_recv_rsp(self, rsp_pb):
        ret, data = super().on_recv_rsp(rsp_pb)
        if ret != ft.RET_OK:
            return ret, data
        for _, row in data.iterrows():
            msg = {
                "type": "kline",
                "code": row["code"],
                "ktype": str(row.get("k_type", "")),
                "time_key": str(row["time_key"]),
                "open": float(row["open"]),
                "close": float(row["close"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "volume": int(row["volume"]),
            }
            asyncio.run_coroutine_threadsafe(self.ws.broadcast(msg), self.loop)
        return ret, data
