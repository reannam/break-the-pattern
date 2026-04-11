from flask import Blueprint, request, jsonify
from google import genai
from google.genai import types
import json
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
            data = json.loads(response.text)
        except Exception:
            return jsonify({
                "error": "Model returned invalid JSON",
                "raw": response.text
            }), 500

        return jsonify(data)

    except Exception as e:
        print(f"AI Error: {e}")
        return jsonify({"error": "Internal server error"}), 500