import asyncio
import moomoo as ft
from app.ws_manager import WebSocketManager


class OrderHandler(ft.TradeOrderHandlerBase):
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
                "type": "order_update",
                "order_id": str(row["order_id"]),
                "code": row["code"],
                "status": str(row["order_status"]),
                "trd_side": str(row["trd_side"]),
                "qty": int(row["qty"]),
                "price": float(row["price"]),
            }
            asyncio.run_coroutine_threadsafe(self.ws.broadcast(msg), self.loop)
        return ret, data
