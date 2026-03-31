from datetime import datetime, timedelta

from .behaviour import get_expected_activity


def detect_anomaly(events):
    anomalies = detect_anomalies(events)
    return anomalies[0] if anomalies else None


def detect_anomalies(events):
    if not events:
        return []

    parsed_events = []
    for event in events:
        parsed_events.append(
            {
                **event,
                "_dt": datetime.fromisoformat(event["timestamp"]),
            }
        )

    parsed_events.sort(key=lambda item: item["_dt"])
    now = parsed_events[-1]["_dt"]
    expected = get_expected_activity(now)

    recent_window = [event for event in parsed_events if event["_dt"] >= now - timedelta(seconds=45)]
    baseline_window = [event for event in parsed_events if now - timedelta(seconds=150) <= event["_dt"] < now - timedelta(seconds=45)]

    recent_average = _average_activity(recent_window)
    baseline_average = _average_activity(baseline_window or parsed_events)
    recent_range = _activity_range(recent_window)
    baseline_range = _activity_range(baseline_window or parsed_events)
    anomalies = []

    if expected["period"] in {"morning", "daytime", "evening"} and recent_average <= 8:
        anomalies.append(
            {
                "anomaly_type": "prolonged_inactivity",
                "expected_pattern": expected["description"],
                "observed_behavior": "very low movement persisted across the recent monitoring window",
                "severity": 0.91,
                "confidence": 0.92,
                "activity_level": round(recent_average, 2),
                "baseline_activity_level": round(baseline_average, 2),
                "event_type": _dominant_event_type(recent_window),
                "inactivity_window_seconds": 45,
                "deviation_from_baseline": round(recent_average - baseline_average, 2),
            }
        )

    if baseline_average and recent_window:
        drop_ratio = recent_average / baseline_average if baseline_average else 1
        spike_ratio = recent_average / baseline_average if baseline_average else 1
        if drop_ratio <= 0.45 and recent_average > 8:
            anomalies.append(
                {
                    "anomaly_type": "activity_pattern_deviation",
                    "expected_pattern": f"recent activity typically stays near {baseline_average:.0f}",
                    "observed_behavior": "movement has dropped noticeably below the recent baseline",
                    "severity": 0.78,
                    "confidence": 0.85,
                    "activity_level": round(recent_average, 2),
                    "baseline_activity_level": round(baseline_average, 2),
                    "event_type": _dominant_event_type(recent_window),
                    "inactivity_window_seconds": 0,
                    "deviation_from_baseline": round(recent_average - baseline_average, 2),
                }
            )
        elif spike_ratio >= 1.8:
            anomalies.append(
                {
                    "anomaly_type": "activity_pattern_deviation",
                    "expected_pattern": f"recent activity typically stays near {baseline_average:.0f}",
                    "observed_behavior": "activity spikes are appearing above the recent baseline",
                    "severity": 0.72,
                    "confidence": 0.83,
                    "activity_level": round(recent_average, 2),
                    "baseline_activity_level": round(baseline_average, 2),
                    "event_type": _dominant_event_type(recent_window),
                    "inactivity_window_seconds": 0,
                    "deviation_from_baseline": round(recent_average - baseline_average, 2),
                }
            )

    if recent_range >= 55 and recent_range >= baseline_range + 20:
        anomalies.append(
            {
                "anomaly_type": "activity_variability",
                "expected_pattern": f"recent movement changes usually stay within a range of about {baseline_range:.0f}",
                "observed_behavior": "activity is shifting quickly between low and high movement levels",
                "severity": 0.76,
                "confidence": 0.82,
                "activity_level": round(recent_average, 2),
                "baseline_activity_level": round(baseline_average, 2),
                "event_type": _dominant_event_type(recent_window),
                "inactivity_window_seconds": 0,
                "deviation_from_baseline": round(recent_range - baseline_range, 2),
            }
        )

    routine_expected = expected["routine_expected"]
    recent_routine_events = [event for event in recent_window if event["event_type"] == "routine_event"]
    if routine_expected and not recent_routine_events and recent_average < expected["activity_band"][0] * 0.6:
        anomalies.append(
                {
                    "anomaly_type": "missing_routine_event",
                    "expected_pattern": f"{expected['routine_name']} should usually appear during this period",
                    "observed_behavior": "the expected routine-associated movement has not appeared in the recent window",
                    "severity": 0.74,
                    "confidence": 0.81,
                    "activity_level": round(recent_average, 2),
                    "baseline_activity_level": round(baseline_average, 2),
                    "event_type": _dominant_event_type(recent_window),
                    "inactivity_window_seconds": 45,
                    "deviation_from_baseline": round(recent_average - baseline_average, 2),
                }
            )

    return _dedupe_anomalies(anomalies)


def _average_activity(events):
    if not events:
        return 0.0
    return sum(event["activity_level"] for event in events) / len(events)


def _activity_range(events):
    if not events:
        return 0.0
    levels = [event["activity_level"] for event in events]
    return float(max(levels) - min(levels))


def _dominant_event_type(events):
    if not events:
        return "idle"
    counts = {}
    for event in events:
        event_type = event["event_type"]
        counts[event_type] = counts.get(event_type, 0) + 1
    return max(counts, key=counts.get)


def _dedupe_anomalies(anomalies):
    seen = set()
    unique = []
    for anomaly in anomalies:
        anomaly_type = anomaly["anomaly_type"]
        if anomaly_type in seen:
            continue
        seen.add(anomaly_type)
        unique.append(anomaly)
    return unique
