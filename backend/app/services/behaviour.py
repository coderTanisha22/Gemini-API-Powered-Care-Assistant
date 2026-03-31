from datetime import datetime


def get_expected_activity(at_time: datetime | None = None):
    now = at_time or datetime.now()
    hour = now.hour

    if 6 <= hour < 10:
        return {
            "period": "morning",
            "description": "regular movement between rooms during the morning routine",
            "activity_band": (40, 75),
            "routine_expected": True,
            "routine_name": "morning movement",
            "locations": ["bedroom", "hallway", "kitchen"],
            "rest_location": "bedroom",
        }

    if 10 <= hour < 18:
        return {
            "period": "daytime",
            "description": "moderate daytime movement with short idle periods",
            "activity_band": (25, 55),
            "routine_expected": False,
            "routine_name": None,
            "locations": ["living_room", "hallway", "kitchen"],
            "rest_location": "living_room",
        }

    if 18 <= hour < 22:
        return {
            "period": "evening",
            "description": "light evening movement before settling down",
            "activity_band": (20, 45),
            "routine_expected": True,
            "routine_name": "evening check-in",
            "locations": ["living_room", "kitchen", "bedroom"],
            "rest_location": "living_room",
        }

    return {
        "period": "night",
        "description": "mostly low overnight activity with occasional movement",
        "activity_band": (0, 15),
        "routine_expected": False,
        "routine_name": None,
        "locations": ["bedroom", "hallway"],
        "rest_location": "bedroom",
    }
