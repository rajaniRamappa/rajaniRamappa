import asyncio
from typing import Optional
from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()


class OrderRequest(BaseModel):
    code: str
    side: str        # "BUY" | "SELL"
    order_type: str  # "LIMIT" | "MARKET"
    qty: int
    price: Optional[float] = None


@router.post("/order")
async def place_order(req: OrderRequest, request: Request):
    moomoo = request.app.state.moomoo
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,
        lambda: moomoo.place_order(req.code, req.side, req.order_type, req.qty, req.price),
    )
    return result


@router.delete("/order/{order_id}")
async def cancel_order(order_id: str, request: Request):
    moomoo = request.app.state.moomoo
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, lambda: moomoo.cancel_order(order_id))
    return result


@router.get("/orders")
async def list_orders(request: Request):
    moomoo = request.app.state.moomoo
    loop = asyncio.get_running_loop()
    data = await loop.run_in_executor(None, moomoo.get_orders)
    return {"orders": data}


@router.get("/positions")
async def get_positions(request: Request):
    moomoo = request.app.state.moomoo
    loop = asyncio.get_running_loop()
    data = await loop.run_in_executor(None, moomoo.get_positions)
    return {"positions": data}


@router.get("/account")
async def get_account(request: Request):
    moomoo = request.app.state.moomoo
    loop = asyncio.get_running_loop()
    data = await loop.run_in_executor(None, moomoo.get_account_info)
    return data
