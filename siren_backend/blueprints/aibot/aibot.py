from flask import Blueprint, request, jsonify
from google import genai
from google.genai import types
import json
import re
import globals

aibot_bp = Blueprint("aibot", __name__)

client = genai.Client(api_key=globals.gemini_API_key)


# ----------------------------
# Helpers
# ----------------------------

def heuristic_features(text):
    hedges = ["just", "maybe", "I think", "sorry", "perhaps"]
    hedge_count = sum(1 for w in hedges if w in text.lower())

    return {
        "hedge_count": hedge_count,
        "length": len(text.split())
    }


def get_mode_config(mode):
    """
    Returns tone + behavior rules safely.
    """

    if mode == "general":
        return {
            "tone": "direct, confident, executive-level professional clarity",
            "behavior_rules": """
- Be concise and action-oriented
- Remove softeners like "please", "just", "I think", "maybe" unless necessary for politeness
- Avoid excessive politeness padding
- Use strong verbs and clear requests
"""
        }

    elif mode == "sympathetic":
        return {
            "tone": "warm, respectful, and confident professional tone",
            "behavior_rules": """
- Maintain warmth and empathy
- Do NOT become passive or overly apologetic
- Keep language confident, not hesitant
- Preserve politeness but avoid weakening statements
"""
        }

    else:
        return {
            "tone": "clear, assertive, confident, professional",
            "behavior_rules": """
- Be concise and action-oriented
- Remove hedging and unnecessary softness
"""
        }


def build_prompt(email_text, mode):

    config = get_mode_config(mode)
    features = heuristic_features(email_text)

    return f"""
You are an expert communication coach helping women write confidently in professional settings.

TASK:
1. Rewrite the message to be {config["tone"]}

CORE RULES:
- Preserve original meaning exactly
- Remove hedging (e.g., "just", "maybe", "I think")
- Remove unnecessary apologies
- Do NOT make the message aggressive, rude, or cold
- Always keep a professional tone
- Keep opener (hi/hello/hey) if present

MODE RULES:
{config["behavior_rules"]}

PRE-ANALYSIS (original message signals):
- hedge_count: {features["hedge_count"]}
- length: {features["length"]} words

SCORING INSTRUCTION (IMPORTANT):
You must compare ORIGINAL vs REWRITTEN message.

Score BOTH:

Before = original email quality
After = rewritten email quality

SCORING RUBRIC (strict):

Clarity:
- 1–3: unclear, multiple ideas, vague request
- 4–6: mostly clear but wordy
- 7–8: clear and structured
- 9–10: extremely clear, single unambiguous request

Assertiveness:
- 1–3: apologetic, passive, hedged
- 4–6: mixed confidence
- 7–8: confident with minor softening
- 9–10: fully confident, no hedging or apologies

Directness:
- 1–3: request buried or unclear
- 4–6: moderate delay before request
- 7–8: request appears early
- 9–10: immediate explicit request


ANCHOR SCORING EXAMPLES (VERY IMPORTANT):

Clarity:
1 = extremely unclear, no identifiable request
5 = understandable but slightly wordy or indirect
10 = extremely clear, single direct request stated immediately

Assertiveness:
1 = highly apologetic, uncertain, passive
5 = balanced tone, some confidence but still soft
10 = fully confident, directive, no hedging or apology

Directness:
1 = request hidden or missing
5 = request present but delayed or softened
10 = request appears immediately in first sentence


CRITICAL SCORING RULES:
- Use full 1–10 range (do NOT stay in the middle)
- Do NOT compress scores into 4–6 range
- High-quality rewritten emails should score 7–9
- Only weak writing should score below 5
- Scores must reflect real differences in writing strength
- Scores must be consistent and based on observable language
- Do NOT randomize
- Every score must include a reason tied to wording differences
- AFTER scores must ALWAYS be higher or equal to BEFORE scores

IMPORTANT:
Evaluate "before" scores ONLY using the original message.
Evaluate "after" scores ONLY using the rewritten message.

Do not let improvements in the rewritten message influence the "before" score.
Treat them as two separate independent evaluations.

Step 1: Analyze original message only.
Step 2: Score original message.
Step 3: Analyze rewritten message only.
Step 4: Score rewritten message.
Step 5: Compare.

Ensure sympathetic mode retains warmth and politeness cues that general mode should minimize.
Ensure general mode prioritizes directness over politeness.

RETURN ONLY VALID JSON:

{{
  "mode": "{mode}",

  "rewritten": "...",

  "scores": {{
    "clarity": {{
      "before": {{
        "value": 0,
        "reason": "..."
      }},
      "after": {{
        "value": 0,
        "reason": "..."
      }}
    }},

    "assertiveness": {{
      "before": {{
        "value": 0,
        "reason": "..."
      }},
      "after": {{
        "value": 0,
        "reason": "..."
      }}
    }},

    "directness": {{
      "before": {{
        "value": 0,
        "reason": "..."
      }},
      "after": {{
        "value": 0,
        "reason": "..."
      }}
    }}
  }},

  "explanations": [
    "Explain key improvements like removal of hedging, stronger verbs, clearer request structure"
  ]
}}

Message:
{email_text}
"""


def extract_json_payload(raw_text):
    """
    Gemini occasionally wraps JSON in markdown fences or adds prose.
    Pull out the first JSON object if direct parsing fails.
    """

    if not raw_text:
        raise ValueError("Empty model response")

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        pass

    fenced_match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", raw_text, re.DOTALL)
    if fenced_match:
        return json.loads(fenced_match.group(1))

    object_match = re.search(r"(\{.*\})", raw_text, re.DOTALL)
    if object_match:
        return json.loads(object_match.group(1))

    raise ValueError("No valid JSON object found in model response")


def safe_number(value, fallback=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def score_after_value(score_block):
    """
    Support both nested score objects and already-normalized numeric scores.
    """

    if isinstance(score_block, dict):
        if isinstance(score_block.get("after"), dict):
            return safe_number(score_block["after"].get("value"), 0)
        return safe_number(score_block.get("value"), 0)

    return safe_number(score_block, 0)


def normalize_response(data):
    """
    Convert model output into the exact frontend contract.
    """

    scores = data.get("scores", {}) if isinstance(data, dict) else {}

    normalized = {
        "rewritten": data.get("rewritten", "") if isinstance(data, dict) else "",
        "explanations": data.get("explanations", []) if isinstance(data, dict) else [],
        "scores": {
            "clarity": score_after_value(scores.get("clarity")),
            "directness": score_after_value(scores.get("directness")),
            "assertiveness": score_after_value(scores.get("assertiveness")),
        },
        "improved_phrases": data.get("improved_phrases", []) if isinstance(data, dict) else [],
    }

    if not isinstance(normalized["explanations"], list):
        normalized["explanations"] = [str(normalized["explanations"])]

    if not isinstance(normalized["improved_phrases"], list):
        normalized["improved_phrases"] = []

    return normalized


def fallback_rewrite(email_text, mode):
    """
    Deterministic fallback so the demo still works if Gemini fails.
    """

    rewritten = email_text.strip()
    replacements = [
        ("just", ""),
        ("maybe", ""),
        ("I think", ""),
        ("i think", ""),
        ("sorry", ""),
        ("perhaps", ""),
        ("when you get a chance", ""),
        ("wanted to check in", "am following up"),
    ]

    improved_phrases = []
    for old, new in replacements:
        if old in rewritten:
            improved_phrases.append(old)
            rewritten = rewritten.replace(old, new)

    rewritten = re.sub(r"\s+", " ", rewritten).strip(" ,")

    if mode == "sympathetic":
        if not rewritten.lower().startswith(("hi", "hello", "hey")):
            rewritten = f"Hi, {rewritten}"
        explanations = [
            "Kept the tone warm while removing hesitant phrasing.",
            "Made the request easier to understand and harder to overlook.",
            "Reduced filler language without making the message cold.",
        ]
        scores = {
            "clarity": 8,
            "directness": 7,
            "assertiveness": 7,
        }
    else:
        explanations = [
            "Removed hedging and filler language.",
            "Made the request more direct and action-oriented.",
            "Tightened the sentence structure for clearer delivery.",
        ]
        scores = {
            "clarity": 8,
            "directness": 8,
            "assertiveness": 8,
        }

    return {
        "rewritten": rewritten or email_text.strip(),
        "explanations": explanations,
        "scores": scores,
        "improved_phrases": improved_phrases,
    }


# ----------------------------
# Route
# ----------------------------

@aibot_bp.route('/api/v1.0/rewrite', methods=['POST'])
def rewrite_emails():

    try:
        user_data = request.json or {}

        email = user_data.get('email', '')
        mode = user_data.get('mode', 'general')

        if not email:
            return jsonify({"error": "No email provided"}), 400

        prompt = build_prompt(email, mode)

        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )

        try:
            data = extract_json_payload(response.text)
            normalized = normalize_response(data)
        except Exception as parse_error:
            print(f"JSON Parse Error: {parse_error}")
            print(f"Raw model response: {response.text}")
            return jsonify(fallback_rewrite(email, mode))

        return jsonify(normalized)

    except Exception as e:
        print(f"AI Error: {e}")
        return jsonify(fallback_rewrite(email, mode))
