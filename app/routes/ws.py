import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, request: Request):
    ws_manager = request.app.state.ws_manager
    moomoo = request.app.state.moomoo
    alert_engine = request.app.state.alert_engine

    await ws_manager.connect(websocket)
    try:
        while True:
            raw = await websocket.receive_text()
            msg = json.loads(raw)
            cmd = msg.get("cmd")

            if cmd == "unlock_trade":
                import asyncio
                loop = asyncio.get_running_loop()
                ret, data = await loop.run_in_executor(
                    None, lambda: moomoo.unlock_trade(msg.get("password", ""))
                )
                await ws_manager.send_to(websocket, {
                    "type": "unlock_result",
                    "ok": ret == 0,
                    "msg": "" if ret == 0 else str(data),
                })

            elif cmd == "add_watchlist":
                symbol = msg.get("symbol", "").strip().upper()
                if symbol:
                    ret, err = await moomoo.subscribe_symbol(symbol)
                    await ws_manager.send_to(websocket, {
                        "type": "watchlist_update",
                        "symbol": symbol,
                        "ok": ret == 0,
                        "msg": "" if ret == 0 else str(err),
                    })

            elif cmd == "remove_watchlist":
                symbol = msg.get("symbol", "").strip().upper()
                if symbol:
                    await moomoo.unsubscribe_symbol(symbol)

            elif cmd == "add_alert":
                alert_id = alert_engine.add_alert(
                    msg.get("code", "").strip().upper(),
                    msg.get("direction", "above"),
                    float(msg.get("threshold", 0)),
                    msg.get("label", ""),
                )
                await ws_manager.send_to(websocket, {
                    "type": "alert_added",
                    "alert_id": alert_id,
                })

            elif cmd == "remove_alert":
                alert_engine.remove_alert(msg.get("alert_id", ""))

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)
