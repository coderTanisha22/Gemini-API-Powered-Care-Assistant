import threading
from datetime import datetime

from .anamoly import detect_anomalies
from .gemini_client import generate_explanation, generate_normal_insight
from .simulator import simulator


_ALERT_IDS = {
    "prolonged_inactivity": 1,
    "activity_pattern_deviation": 2,
    "missing_routine_event": 3,
    "activity_variability": 4,
    "follow_up_review": 5,
}

_ALERT_TITLES = {
    "prolonged_inactivity": "Prolonged inactivity detected",
    "activity_pattern_deviation": "Recent activity pattern changed",
    "missing_routine_event": "Expected routine event missing",
    "activity_variability": "Activity variability increased",
    "follow_up_review": "Follow-up review suggested",
}

_action_lock = threading.Lock()
_resolved_alerts: dict[int, str] = {}
_DEMO_ALERT_ID = 9001
_demo_alert_enabled = False


def get_recent_events(limit: int | None = None):
    return simulator.get_recent_events(limit)


def get_simulation_status():
    return simulator.status()


def get_activity_timeline(size: int = 7):
    events = get_recent_events(size)
    if not events:
        return [0] * size
    levels = [event["activity_level"] for event in events]
    if len(levels) < size:
        levels = ([levels[0]] * (size - len(levels))) + levels
    return levels[-size:]


def get_alerts_data(role: str = "caregiver"):
    events = get_recent_events()
    anomalies = detect_anomalies(events)
    current_time = datetime.now().strftime("%I:%M %p").lstrip("0")

    alerts = []
    with _action_lock:
        resolved_ids = set(_resolved_alerts.keys())
        include_demo_alert = _demo_alert_enabled

    for anomaly in anomalies:
        alert_id = _ALERT_IDS[anomaly["anomaly_type"]]
        if alert_id in resolved_ids:
            continue
        interpretation = generate_explanation(anomaly, role=role)
        alerts.append(
            {
                "id": alert_id,
                "title": _ALERT_TITLES[anomaly["anomaly_type"]],
                "time": current_time,
                "severity": _severity_label(anomaly["severity"]),
                "confidence": interpretation["confidence"],
                "type": anomaly["anomaly_type"],
                "summary": interpretation["summary"],
                "explanation": interpretation["explanation"],
                "status": "pending",
                "anomaly": anomaly,
            }
        )

    if len(alerts) == 1:
        support_alert = _build_supporting_alert(alerts[0], role)
        if support_alert and support_alert["id"] not in resolved_ids:
            alerts.append(support_alert)

    if include_demo_alert and _DEMO_ALERT_ID not in resolved_ids:
        alerts.append(_build_demo_alert(role=role, current_time=current_time))

    return alerts


def get_dashboard_data(role: str = "caregiver"):
    activity_data = get_activity_timeline()
    alerts = get_alerts_data(role=role)
    primary_alert = alerts[0] if alerts else None
    explanation = (
        {
            "summary": primary_alert["summary"],
            "explanation": primary_alert["explanation"],
            "confidence": primary_alert["confidence"],
        }
        if primary_alert
        else generate_normal_insight(activity_data, role=role)
    )

    return {
        "activity": activity_data,
        "alerts": alerts,
        "alert": primary_alert["anomaly"] if primary_alert else None,
        "explanation": explanation,
        "status": "alert" if alerts else "normal",
    }


def resolve_alert(alert_id: int, action: str):
    global _demo_alert_enabled
    with _action_lock:
        _resolved_alerts[alert_id] = action
        if alert_id == _DEMO_ALERT_ID:
            _demo_alert_enabled = False
    return {
        "message": f"Alert {alert_id} {action}d successfully",
        "status": "updated",
    }


def seed_demo_alert(role: str = "supervisor"):
    global _demo_alert_enabled
    with _action_lock:
        _demo_alert_enabled = True
        _resolved_alerts.pop(_DEMO_ALERT_ID, None)
    current_time = datetime.now().strftime("%I:%M %p").lstrip("0")
    return _build_demo_alert(role=role, current_time=current_time)


def _severity_label(score: float):
    if score >= 0.85:
        return "high"
    if score >= 0.7:
        return "medium"
    return "low"


def _build_supporting_alert(primary_alert: dict, role: str):
    base_anomaly = primary_alert["anomaly"]
    if base_anomaly["anomaly_type"] in {"missing_routine_event", "follow_up_review"}:
        return None

    supporting_anomaly = {
        "anomaly_type": "follow_up_review",
        "expected_pattern": base_anomaly["expected_pattern"],
        "observed_behavior": "the recent change may be worth checking again in the next monitoring window",
        "severity": 0.68,
        "confidence": max(0.7, round(base_anomaly["confidence"] - 0.06, 2)),
        "activity_level": base_anomaly.get("activity_level", 0),
        "baseline_activity_level": base_anomaly.get("baseline_activity_level", 0),
        "event_type": base_anomaly.get("event_type", "movement"),
        "inactivity_window_seconds": base_anomaly.get("inactivity_window_seconds", 0),
        "deviation_from_baseline": base_anomaly.get("deviation_from_baseline", 0),
    }
    interpretation = generate_explanation(supporting_anomaly, role=role)
    return {
        "id": _ALERT_IDS["follow_up_review"],
        "title": _ALERT_TITLES["follow_up_review"],
        "time": primary_alert["time"],
        "severity": "low",
        "confidence": interpretation["confidence"],
        "type": supporting_anomaly["anomaly_type"],
        "summary": interpretation["summary"],
        "explanation": interpretation["explanation"],
        "status": "pending",
        "anomaly": supporting_anomaly,
    }


def _build_demo_alert(role: str, current_time: str):
    demo_anomaly = {
        "anomaly_type": "manual_demo",
        "expected_pattern": "typical routine activity",
        "observed_behavior": "manual demo alert triggered for supervisor workflow",
        "severity": 0.88,
        "confidence": 0.91,
        "activity_level": 14,
        "baseline_activity_level": 36,
        "event_type": "manual",
        "inactivity_window_seconds": 45,
        "deviation_from_baseline": -22,
    }
    interpretation = generate_explanation(demo_anomaly, role=role)
    return {
        "id": _DEMO_ALERT_ID,
        "title": "Demo alert: activity check required",
        "time": current_time,
        "severity": "high",
        "confidence": interpretation["confidence"],
        "type": demo_anomaly["anomaly_type"],
        "summary": interpretation["summary"],
        "explanation": interpretation["explanation"],
        "status": "pending",
        "anomaly": demo_anomaly,
    }
