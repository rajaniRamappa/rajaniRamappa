from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.ws_manager import WebSocketManager
from app.alert_engine import AlertEngine
from app.moomoo_client import MoomooClient
from app.routes import ws as ws_route
from app.routes import market as market_route
from app.routes import trade as trade_route


@asynccontextmanager
async def lifespan(app: FastAPI):
    await app.state.moomoo.connect()
    yield
    await app.state.moomoo.disconnect()


def create_app() -> FastAPI:
    ws_manager = WebSocketManager()
    alert_engine = AlertEngine(ws_manager)
    moomoo = MoomooClient(ws_manager, alert_engine)

    app = FastAPI(title="SGX Trading Dashboard", lifespan=lifespan)
    app.state.ws_manager = ws_manager
    app.state.alert_engine = alert_engine
    app.state.moomoo = moomoo

    app.include_router(ws_route.router)
    app.include_router(market_route.router, prefix="/api")
    app.include_router(trade_route.router, prefix="/api")
    app.mount("/", StaticFiles(directory="static", html=True), name="static")

    return app


app = create_app()
