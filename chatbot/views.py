"""
Chatbot endpoint.

The browser POSTs a user message to /api/chat/. This view calls the AI
provider *server-side* using a key stored in an environment variable, so the
key is never exposed to the client. The reply is returned as JSON.

Swap providers by replacing the `call_ai_model` function — the rest of the
view (validation, CSRF, error handling) stays the same.
"""

import json

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST

MAX_MESSAGE_CHARS = 2000

SYSTEM_PROMPT = (
    "You are a friendly assistant embedded on Sanjeev Shrestha's personal "
    "portfolio website. Answer questions about Sanjeev's work, skills, and "
    "projects concisely and warmly. If you don't know something specific, say "
    "so and suggest the visitor use the contact details on the site. Keep "
    "replies short — a few sentences at most."
)


def call_ai_model(message: str) -> str:
    """Call the AI provider and return the reply text.

    Default implementation uses the Anthropic API. To use a different
    provider, rewrite only this function.
    """
    # Imported lazily so the app still boots if the SDK isn't installed yet.
    import anthropic

    client = anthropic.Anthropic(api_key=settings.AI_API_KEY)
    response = client.messages.create(
        model=settings.AI_MODEL,
        max_tokens=400,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": message}],
    )
    # The response content is a list of blocks; collect the text blocks.
    return "".join(
        block.text for block in response.content if block.type == "text"
    ).strip()


@require_POST
def chat(request):
    # 1. Parse and validate the incoming message.
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Invalid request body."}, status=400)

    message = (payload.get("message") or "").strip()
    if not message:
        return JsonResponse({"error": "Message cannot be empty."}, status=400)
    if len(message) > MAX_MESSAGE_CHARS:
        return JsonResponse(
            {"error": f"Message too long (max {MAX_MESSAGE_CHARS} characters)."},
            status=400,
        )

    # 2. Make sure the server is configured before calling out.
    if not settings.AI_API_KEY:
        return JsonResponse(
            {"error": "The chatbot is not configured yet."}, status=503
        )

    # 3. Call the model and return its reply.
    try:
        reply = call_ai_model(message)
    except Exception:
        # Don't leak provider internals to the client.
        return JsonResponse(
            {"error": "The assistant is unavailable right now. Try again later."},
            status=502,
        )

    return JsonResponse({"reply": reply})
