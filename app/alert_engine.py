from typing import Dict
from app.ws_manager import WebSocketManager


class AlertRule:
    def __init__(self, alert_id: str, code: str, direction: str, threshold: float, label: str):
        self.alert_id = alert_id
        self.code = code
        self.direction = direction  # "above" | "below"
        self.threshold = float(threshold)
        self.label = label
        self.triggered = False


class AlertEngine:
    def __init__(self, ws_manager: WebSocketManager):
        self.ws = ws_manager
        self._rules: Dict[str, AlertRule] = {}
        self._counter = 0

    def add_alert(self, code: str, direction: str, threshold: float, label: str = "") -> str:
        self._counter += 1
        alert_id = f"alert_{self._counter}"
        self._rules[alert_id] = AlertRule(alert_id, code, direction, threshold, label)
        return alert_id

    def remove_alert(self, alert_id: str):
        self._rules.pop(alert_id, None)

    def list_alerts(self) -> list:
        return [
            {
                "alert_id": r.alert_id,
                "code": r.code,
                "direction": r.direction,
                "threshold": r.threshold,
                "label": r.label,
                "triggered": r.triggered,
            }
            for r in self._rules.values()
        ]

    async def evaluate(self, code: str, last_price: float):
        for rule in list(self._rules.values()):
            if rule.code != code or rule.triggered:
                continue
            triggered = (
                (rule.direction == "above" and last_price >= rule.threshold)
                or (rule.direction == "below" and last_price <= rule.threshold)
            )
            if triggered:
                rule.triggered = True
                await self.ws.broadcast(
                    {
                        "type": "alert_triggered",
                        "alert_id": rule.alert_id,
                        "code": rule.code,
                        "direction": rule.direction,
                        "threshold": rule.threshold,
                        "last_price": last_price,
                        "label": rule.label,
                    }
                )
