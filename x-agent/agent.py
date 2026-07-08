import json
import re
import anthropic
from prompts import BRAND_VOICE, CONTENT_PROMPT


def generate_drafts(context: str) -> list[dict]:
    """Generate 4 bilingual tweet draft options from a context string."""
    client = anthropic.Anthropic()

    message = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=1500,
        system=BRAND_VOICE,
        messages=[{"role": "user", "content": CONTENT_PROMPT.format(context=context)}],
    )

    raw = message.content[0].text.strip()

    # Strip markdown code fences if model wraps output
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    return json.loads(raw.strip())
