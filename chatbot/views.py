"""
Rule-based assistant: routes intents to static answers and safe deep links.
Future: swap `match_rules` output for an LLM API with guardrails.
"""

import re

from django.http import JsonResponse
from django.urls import reverse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


def match_rules(message: str) -> tuple[str, list[dict]]:
    """
    Return (reply_text, suggested_actions) where actions are {label, url} for the client.
    """
    m = message.lower().strip()
    actions: list[dict] = []

    if re.search(r"\b(emergency|ambulance|urgent|critical)\b", m):
        actions.append({"label": "Open Emergency Finder", "url": reverse("hospitals:emergency")})
        return (
            "If this is a life-threatening emergency, call your local emergency number immediately "
            "(for example 911 or 112). I can also open the Emergency Finder to locate the nearest ER.",
            actions,
        )

    if re.search(r"\b(hospital|near|nearby|find|location|map)\b", m):
        actions.append({"label": "Search hospitals", "url": reverse("hospitals:search")})
        return (
            "You can search hospitals by location and filters on the Hospital Search page. "
            "Allow location access or enter coordinates for distance sorting.",
            actions,
        )

    if re.search(r"\b(book|appointment|schedule|slot)\b", m):
        actions.append({"label": "Hospital search", "url": reverse("hospitals:search")})
        return (
            "To book: pick a hospital, department, doctor, and an open time slot. "
            "Start from Hospital Search, open a hospital, then use Book appointment.",
            actions,
        )

    if re.search(r"\b(doctor|specialist|cardio|ortho|pediatric)\b", m):
        return (
            "Browse doctors from a hospital’s page under Doctors. Each profile shows specialization "
            "and weekly schedules.",
            [{"label": "Find hospitals", "url": reverse("hospitals:search")}],
        )

    if re.search(r"\b(help|hi|hello|start)\b", m):
        return (
            "I can help you find hospitals, suggest next steps for booking, or guide you to emergency resources. "
            "Try: “find hospitals near me”, “book appointment”, or “emergency”.",
            [],
        )

    return (
        "I’m a rule-based assistant for this demo. Rephrase with words like “hospital”, “book”, or “emergency”, "
        "or use the navigation links.",
        [{"label": "Home", "url": reverse("hospitals:home")}],
    )


@method_decorator(csrf_exempt, name="dispatch")
class ChatbotMessageView(View):
    """POST JSON { \"message\": \"...\" } → { reply, actions }"""

    def post(self, request):
        import json

        try:
            body = json.loads(request.body.decode() or "{}")
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        text = (body.get("message") or "").strip()
        if not text:
            return JsonResponse({"error": "message required"}, status=400)
        reply, actions = match_rules(text)
        return JsonResponse({"reply": reply, "actions": actions})
