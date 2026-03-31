from fastapi import APIRouter
from pydantic import BaseModel

from ..services.alert_service import (
    get_alerts_data,
    get_dashboard_data,
    get_simulation_status,
    resolve_alert,
    seed_demo_alert,
)
from ..services.gemini_client import get_gemini_runtime_status
from ..services.simulator import simulator

router = APIRouter()

@router.get("/activity")
def get_activity(role: str = "caregiver"):
    data = get_dashboard_data(role=role)
    return {
        "timeline": data["activity"],
        "status": data["status"]
    }

@router.get("/alerts")
def get_alerts(role: str = "caregiver"):
    alerts = get_alerts_data(role=role)
    return [
        {
            "id": alert["id"],
            "title": alert["title"],
            "time": alert["time"],
            "severity": alert["severity"],
            "confidence": alert["confidence"],
            "type": alert["type"],
            "summary": alert["summary"],
            "explanation": alert["explanation"],
            "status": alert["status"],
        }
        for alert in alerts
    ]


@router.get("/insight")
def get_insight(role: str = "caregiver"):
    data = get_dashboard_data(role=role)
    explanation = data.get("explanation")

    if isinstance(explanation, dict):
        return {
            "summary": explanation.get("summary", explanation.get("explanation", "No issues detected")),
            "confidence": explanation.get("confidence", 0.85),
        }

    return {
        "summary": "Recent activity appears to be within the expected routine, with no notable behavioral changes detected in the latest monitoring window.",
        "confidence": 0.85
    }


@router.get("/dashboard")
def get_dashboard(role: str = "caregiver"):
    return get_dashboard_data(role=role)


#request body
class AlertAction(BaseModel):
    alert_id: int
    action: str  #"approve" or "reject"


@router.post("/alerts/action")
def handle_alert_action(payload: AlertAction):
    return resolve_alert(payload.alert_id, payload.action)


@router.post("/alerts/demo/seed")
def create_demo_alert(role: str = "supervisor"):
    alert = seed_demo_alert(role=role)
    return {
        "id": alert["id"],
        "title": alert["title"],
        "time": alert["time"],
        "severity": alert["severity"],
        "confidence": alert["confidence"],
        "type": alert["type"],
        "summary": alert["summary"],
        "explanation": alert["explanation"],
        "status": alert["status"],
    }


@router.post("/simulate/start")
async def start_simulation():
    return await simulator.start()


@router.post("/simulate/stop")
async def stop_simulation():
    return await simulator.stop()


@router.get("/simulate/status")
def simulation_status():
    return get_simulation_status()


@router.get("/gemini/status")
def gemini_status():
    return get_gemini_runtime_status()
