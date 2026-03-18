#!/usr/bin/env python3
"""
LLM client for ENIS analysis using Jarvis API.
Now backed by shared.jarvis_client with synthesis support.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.jarvis_client import jarvis_ask

# Model name mapping: old names → new Jarvis model names
_MODEL_MAP = {
    "anthropic": "anthropic_claude",
    "openai": "openai_gpt",
    "google_gemini": "google_gemini",
    "perplexity": "perplexity",
    "grok": "xai_grok",
}


def call_llm(prompt, model="anthropic", timeout=90):
    """Call Jarvis API with prompt and wait for response. Returns response text."""
    mapped = _MODEL_MAP.get(model, model)
    result = jarvis_ask(prompt, models=[mapped], timeout=timeout)
    # Prefer synthesis, fall back to raw model response
    if result.get("synthesis"):
        return result["synthesis"].get("unified_answer", "")
    for m in result.get("models", {}).values():
        if isinstance(m, dict) and m.get("response"):
            return m["response"]
    raise TimeoutError(f"Jarvis request timed out after {timeout}s")


def call_llm_multi(prompt, models=["anthropic", "openai", "google_gemini"], timeout=90):
    """Call multiple models and return all responses + synthesis."""
    mapped = [_MODEL_MAP.get(m, m) for m in models]
    return jarvis_ask(prompt, models=mapped, timeout=timeout)


def format_goldman_prompt(company_data):
    """Format Goldman Sachs analysis prompt."""
    return f"""You are a senior equity research analyst at Goldman Sachs.

Analyze this micro-cap company:

Ticker: {company_data['ticker']}
Market Cap: ${company_data['market_cap']:,.0f}
Revenue: ${company_data.get('revenue', 0):,.0f}
Net Margin: {company_data.get('net_margin', 0):.1f}%

Provide:
1. Business model assessment
2. Financial health rating (1-10)
3. Risk factors
4. Recommendation: BUY, HOLD, or AVOID
5. Conviction: HIGH, MEDIUM, or LOW
6. 12-month price target

Format as brief research note."""


def parse_recommendation(response):
    """Extract structured data from LLM response."""
    rec_match = re.search(r'\b(BUY|HOLD|AVOID)\b', response, re.IGNORECASE)
    recommendation = rec_match.group(1).upper() if rec_match else None

    conv_match = re.search(r'\b(HIGH|MEDIUM|LOW)\b', response, re.IGNORECASE)
    conviction = conv_match.group(1).upper() if conv_match else None

    price_match = re.search(r'\$(\d+\.?\d*)', response)
    price_target = float(price_match.group(1)) if price_match else None

    return {
        'recommendation': recommendation,
        'conviction': conviction,
        'price_target': price_target,
        'full_text': response
    }


if __name__ == "__main__":
    print("Testing LLM connection...")
    response = call_llm("Say 'OK' if you can hear me.")
    print(f"Response: {response}")
