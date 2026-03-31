from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
import logging
import os
import re
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - depends on local dependency install
    def load_dotenv(*args, **kwargs):
        return False


logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parents[3]
load_dotenv(ROOT_DIR / ".env")

DEFAULT_ROLE = "caregiver"
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
REQUEST_TIMEOUT_SECONDS = float(os.getenv("GEMINI_TIMEOUT_SECONDS", "6"))
GEMINI_ENABLED = os.getenv("GEMINI_ENABLED", "false").strip().lower() == "true"
_SDK_MODE = "unavailable"

try:
    from google import genai
    from google.genai import types as genai_types

    _SDK_MODE = "google_genai"
except ImportError:  # pragma: no cover - depends on local SDK install
    genai = None
    genai_types = None
    try:
        import google.generativeai as legacy_genai

        _SDK_MODE = "google_generativeai"
    except ImportError:  # pragma: no cover - depends on local SDK install
        legacy_genai = None


def generate_explanation(anomaly_data: dict, role: str = DEFAULT_ROLE) -> dict:
    safe_role = _normalize_role(role)
    fallback = _fallback_explanation(anomaly_data, safe_role)
    prompt = build_prompt(anomaly_data, safe_role)
    logger.info("Gemini explanation requested for role=%s anomaly=%s", safe_role, anomaly_data.get("anomaly_type"))
    logger.debug("Gemini prompt: %s", prompt)

    for attempt in range(2):
        try:
            response_text = _generate_text(prompt)
            logger.debug("Gemini raw response: %s", response_text)
            parsed = _parse_response(response_text)
            if parsed:
                logger.info(
                    "Gemini live response used successfully for role=%s anomaly=%s sdk=%s model=%s",
                    safe_role,
                    anomaly_data.get("anomaly_type"),
                    _SDK_MODE,
                    DEFAULT_MODEL,
                )
                return {
                    "summary": parsed["summary"],
                    "explanation": parsed["explanation"],
                    "confidence": _safe_confidence(anomaly_data.get("confidence")),
                }
            logger.warning("Gemini returned malformed output; using fallback explanation")
        except Exception as exc:  # pragma: no cover - network/SDK dependent
            logger.warning("Gemini explanation attempt %s failed: %s", attempt + 1, exc)

    logger.info(
        "Using fallback explanation for role=%s anomaly=%s",
        safe_role,
        anomaly_data.get("anomaly_type"),
    )
    return fallback


def generate_normal_insight(activity_data: list[int], role: str = DEFAULT_ROLE) -> dict:
    safe_role = _normalize_role(role)
    average_activity = round(sum(activity_data) / len(activity_data), 2) if activity_data else 0.0
    trend = "stable"
    if len(activity_data) >= 2:
        if activity_data[-1] > activity_data[0] + 8:
            trend = "slightly increasing"
        elif activity_data[-1] < activity_data[0] - 8:
            trend = "slightly decreasing"

    prompt = (
        "You are an interpretation engine for a Gemini-API-Powered Intelligent Care Assistant.\n"
        "You analyze structured non-medical activity data from an IoT care system.\n"
        "Strict rules:\n"
        "- Do not diagnose.\n"
        "- Do not make medical inferences or health predictions.\n"
        "- Do not speculate beyond the provided structured data.\n"
        "- Focus only on behavior, time-based patterns, and activity irregularities.\n"
        "- Use calm, natural dashboard language.\n"
        f"Audience role: {safe_role}.\n"
        "The current state is normal and no anomaly has been detected.\n"
        "Return exactly this format and nothing else:\n"
        "Summary: <one short but informative dashboard summary>\n"
        "Explanation: <one natural explanation of why the current activity looks normal>\n\n"
        "Structured activity context:\n"
        f"- activity_window: {activity_data}\n"
        f"- average_activity: {average_activity}\n"
        f"- trend: {trend}\n"
        "- status: normal\n"
    )

    fallback = {
        "summary": "Recent activity appears to be within the expected routine, with no notable behavioral changes detected in the latest monitoring window.",
        "explanation": "Recent movement levels look steady and consistent with the usual activity pattern for this monitoring period.",
        "confidence": 0.85,
    }

    logger.info("Gemini normal insight requested for role=%s", safe_role)
    logger.debug("Gemini normal insight prompt: %s", prompt)

    for attempt in range(2):
        try:
            response_text = _generate_text(prompt)
            logger.debug("Gemini normal insight raw response: %s", response_text)
            parsed = _parse_response(response_text)
            if parsed:
                logger.info(
                    "Gemini live normal insight used successfully for role=%s sdk=%s model=%s",
                    safe_role,
                    _SDK_MODE,
                    DEFAULT_MODEL,
                )
                return {
                    "summary": parsed["summary"],
                    "explanation": parsed["explanation"],
                    "confidence": 0.85,
                }
            logger.warning("Gemini returned malformed normal insight output; using fallback")
        except Exception as exc:  # pragma: no cover - network/SDK dependent
            logger.warning("Gemini normal insight attempt %s failed: %s", attempt + 1, exc)

    logger.info("Using fallback normal insight for role=%s", safe_role)
    return fallback


def build_prompt(anomaly_data: dict, role: str = DEFAULT_ROLE) -> str:
    safe_role = _normalize_role(role)
    role_instruction = {
        "caregiver": "Provide a calm, natural explanation with practical context for day-to-day monitoring.",
        "supervisor": "Provide a clear explanation that is structured but still natural and easy to read.",
        "family": "Provide a simple, reassuring explanation in plain language without alarmist wording.",
    }[safe_role]

    return (
        "You are an interpretation engine for a Gemini-API-Powered Intelligent Care Assistant.\n"
        "You analyze structured non-medical activity data from an IoT care system.\n"
        "Strict rules:\n"
        "- Do not diagnose.\n"
        "- Do not make medical inferences or health predictions.\n"
        "- Do not speculate beyond the provided structured data.\n"
        "- Focus only on behavior, time-based patterns, and activity irregularities.\n"
        "- Keep the explanation suitable for human review in a human-in-the-loop workflow.\n"
        "- Use warm, natural language rather than technical labels.\n"
        "- Make the summary sound like a dashboard insight, not a diagnostic report.\n"
        f"Audience role: {safe_role}. {role_instruction}\n"
        "Return exactly this format and nothing else:\n"
        "Summary: <one short, human-friendly summary>\n"
        "Explanation: <clear, natural explanation of the behavioral deviation>\n\n"
        "Structured anomaly context:\n"
        f"- anomaly_type: {anomaly_data.get('anomaly_type', 'unknown')}\n"
        f"- expected_pattern: {anomaly_data.get('expected_pattern', 'unknown')}\n"
        f"- observed_behavior: {anomaly_data.get('observed_behavior', 'unknown')}\n"
        f"- activity_level: {anomaly_data.get('activity_level', 'unknown')}\n"
        f"- event_type: {anomaly_data.get('event_type', 'unknown')}\n"
        f"- inactivity_window_seconds: {anomaly_data.get('inactivity_window_seconds', 0)}\n"
        f"- baseline_activity_level: {anomaly_data.get('baseline_activity_level', 'unknown')}\n"
        f"- deviation_from_baseline: {anomaly_data.get('deviation_from_baseline', 'unknown')}\n"
        f"- confidence: {anomaly_data.get('confidence', 0.75)}\n"
    )


def _generate_text(prompt: str) -> str:
    if not GEMINI_ENABLED:
        raise RuntimeError("Gemini integration is disabled; set GEMINI_ENABLED=true to enable live calls")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")

    if _SDK_MODE == "google_genai":
        def _call_google_genai():
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model=DEFAULT_MODEL,
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=220,
                ),
            )
            return (response.text or "").strip()

        return _run_with_timeout(_call_google_genai)

    if _SDK_MODE == "google_generativeai":
        def _call_legacy_sdk():
            legacy_genai.configure(api_key=api_key)
            model = legacy_genai.GenerativeModel(DEFAULT_MODEL)
            response = model.generate_content(prompt)
            return (response.text or "").strip()

        return _run_with_timeout(_call_legacy_sdk)

    raise RuntimeError("No Gemini Python SDK is installed")


def _parse_response(response_text: str) -> dict | None:
    if not response_text:
        return None

    summary_match = re.search(r"Summary:\s*(.+)", response_text)
    explanation_match = re.search(r"Explanation:\s*(.+)", response_text, flags=re.DOTALL)

    if not summary_match or not explanation_match:
        return None

    summary = summary_match.group(1).strip()
    explanation = explanation_match.group(1).strip()
    if not summary or not explanation:
        return None

    return {
        "summary": summary,
        "explanation": explanation,
    }


def _fallback_explanation(anomaly_data: dict, role: str) -> dict:
    summary_map = {
        "prolonged_inactivity": "Activity has been quieter than usual recently.",
        "activity_pattern_deviation": "Recent activity looks different from the usual pattern.",
        "missing_routine_event": "A routine movement pattern has not shown up yet.",
        "activity_variability": "Recent activity has been more uneven than usual.",
        "follow_up_review": "A follow-up check may help confirm whether this change continues.",
    }

    explanation_map = {
        "caregiver": (
            f"The system has noticed a change in recent activity: {_humanize_observed_behavior(anomaly_data)}. "
            f"This differs from the usual pattern of {_humanize_expected_pattern(anomaly_data)}."
        ),
        "supervisor": (
            f"Recent activity suggests a behavioral deviation: {_humanize_observed_behavior(anomaly_data)}. "
            f"This is outside the expected pattern of {_humanize_expected_pattern(anomaly_data)}."
        ),
        "family": "The system noticed a change in recent activity compared with the usual routine. It may be worth taking a quick look.",
    }

    anomaly_type = anomaly_data.get("anomaly_type", "unknown")
    return {
        "summary": summary_map.get(anomaly_type, "A behavioral deviation was detected."),
        "explanation": explanation_map[role],
        "confidence": _safe_confidence(anomaly_data.get("confidence")),
    }


def _normalize_role(role: str) -> str:
    if role in {"caregiver", "supervisor", "family"}:
        return role
    return DEFAULT_ROLE


def _safe_confidence(value) -> float:
    try:
        confidence = float(value)
    except (TypeError, ValueError):
        return 0.75
    return max(0.0, min(confidence, 1.0))


def _run_with_timeout(fn):
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(fn)
        try:
            return future.result(timeout=REQUEST_TIMEOUT_SECONDS)
        except FutureTimeoutError as exc:
            future.cancel()
            raise RuntimeError(f"Gemini request timed out after {REQUEST_TIMEOUT_SECONDS} seconds") from exc


def get_gemini_runtime_status() -> dict:
    api_key = os.getenv("GEMINI_API_KEY", "")
    return {
        "enabled": GEMINI_ENABLED,
        "api_key_present": bool(api_key),
        "api_key_preview": _mask_secret(api_key),
        "sdk_mode": _SDK_MODE,
        "model": DEFAULT_MODEL,
        "timeout_seconds": REQUEST_TIMEOUT_SECONDS,
        "dotenv_path": str(ROOT_DIR / ".env"),
    }


def log_gemini_startup_status() -> None:
    status = get_gemini_runtime_status()
    logger.info(
        "Gemini startup status: enabled=%s api_key_present=%s sdk_mode=%s model=%s dotenv_path=%s",
        status["enabled"],
        status["api_key_present"],
        status["sdk_mode"],
        status["model"],
        status["dotenv_path"],
    )
    if status["api_key_present"]:
        logger.info("Gemini API key detected: %s", status["api_key_preview"])
    if status["enabled"] and not status["api_key_present"]:
        logger.warning("Gemini is enabled but GEMINI_API_KEY is missing")
    if status["enabled"] and status["sdk_mode"] == "unavailable":
        logger.warning("Gemini is enabled but no supported Gemini SDK is installed")


def _mask_secret(secret: str) -> str:
    if not secret:
        return ""
    if len(secret) <= 8:
        return "*" * len(secret)
    return f"{secret[:4]}...{secret[-4:]}"


def _humanize_observed_behavior(anomaly_data: dict) -> str:
    observed = anomaly_data.get("observed_behavior", "activity has changed")
    replacements = {
        "very low movement persisted across the recent monitoring window": "movement has stayed unusually low for a little while",
        "movement has dropped noticeably below the recent baseline": "movement has dropped below the recent usual level",
        "activity spikes are appearing above the recent baseline": "activity has been more active and uneven than usual",
        "the expected routine-associated movement has not appeared in the recent window": "an expected part of the usual routine has not appeared yet",
        "activity is shifting quickly between low and high movement levels": "movement has been shifting quickly between lower and higher activity levels",
        "the recent change may be worth checking again in the next monitoring window": "the recent change may be worth checking again in the next activity window",
    }
    return replacements.get(observed, observed)


def _humanize_expected_pattern(anomaly_data: dict) -> str:
    expected = anomaly_data.get("expected_pattern", "usual routine movement")
    replacements = {
        "recent activity typically stays near": "recent activity normally stays around",
    }
    for source, target in replacements.items():
        if expected.startswith(source):
            return expected.replace(source, target, 1)
    return expected
