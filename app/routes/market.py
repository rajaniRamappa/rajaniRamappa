import asyncio
from fastapi import APIRouter, Request, Query

router = APIRouter()


@router.get("/symbols")
async def get_subscribed_symbols(request: Request):
    moomoo = request.app.state.moomoo
    return {"symbols": sorted(moomoo._subscribed_symbols)}


@router.get("/klines/{symbol}")
async def get_klines(
    symbol: str,
    request: Request,
    ktype: str = Query("1min", pattern="^(1min|5min|15min)$"),
    num: int = Query(120, ge=10, le=500),
):
    moomoo = request.app.state.moomoo
    loop = asyncio.get_running_loop()
    data = await loop.run_in_executor(None, lambda: moomoo.get_klines(symbol, ktype, num))
    return {"symbol": symbol, "ktype": ktype, "data": data}


@router.get("/snapshot/{symbol}")
async def get_snapshot(symbol: str, request: Request):
    moomoo = request.app.state.moomoo
    loop = asyncio.get_running_loop()
    data = await loop.run_in_executor(None, lambda: moomoo.get_snapshot(symbol))
    return data


@router.get("/alerts")
async def list_alerts(request: Request):
    alert_engine = request.app.state.alert_engine
    return {"alerts": alert_engine.list_alerts()}
