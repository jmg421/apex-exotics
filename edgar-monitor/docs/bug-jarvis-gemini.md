# Bug: Gemini silently fails on complex prompts in Jarvis

## Environment
- Endpoint: `https://staging.nodes.bio/api/jarvis/generate`
- Model: `google_gemini`
- Date: March 16, 2026

## Problem
Gemini returns `status: "error"` with an empty error string, 0 tokens, and 0 duration when given multi-part prompts. The error is not captured or surfaced — it fails silently.

## Reproduction

**Works** (simple prompt, Gemini-only):
```bash
curl -X POST "https://staging.nodes.bio/api/jarvis/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Say hello", "models": ["google_gemini"]}'
# Result: 220 tokens, 646ms, success
```

**Works** (medium prompt, Gemini-only):
```bash
curl -X POST "https://staging.nodes.bio/api/jarvis/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "I am building a systematic MES futures trading system. MES is at 6735 with 80-100 point daily ranges and VIX at 26. My stops are 5 points which is too tight. How should I calibrate stops to ATR? Give me a formula with specific numbers.", "models": ["google_gemini"]}'
# Result: 2815 tokens, complete, success
```

**Fails** (long multi-part prompt, Gemini-only):
```bash
curl -X POST "https://staging.nodes.bio/api/jarvis/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "...5-question prompt about MES trading system, ~250 words...", "models": ["google_gemini"]}'
# Result: status=error, error="", tokens=0, duration_ms=0
```

The same long prompt succeeds on `openai_gpt` (10.2s), `anthropic_claude` (12.4s), `perplexity` (4.8s), and `xai_grok` (~30s).

## Error response
```json
{
  "status": "error",
  "response": null,
  "error": "",
  "metadata": {
    "tokens": 0,
    "cost": 0.0,
    "duration_ms": 0
  }
}
```

## Likely causes (in order of probability)

1. **Unhandled exception in Gemini API call** — The empty error string and 0 duration suggest the call fails before timing starts. The exception is being caught but the error message isn't being captured (probably `except Exception as e:` where `str(e)` is empty, or a bare `except:`).

2. **Gemini safety filter** — Gemini's content filter may block the prompt (financial advice + specific dollar amounts + "risk of ruin"). When Gemini blocks content, it returns a response with `finish_reason: SAFETY` and no text. If the backend only checks for `response.text` and doesn't check `finish_reason`, it would see an empty response and fail silently.

3. **Backend timeout too short for Gemini** — Gemini took longer than the other models. If the per-model timeout in `process_request_simple()` is ~15-20s, Gemini may exceed it on complex prompts while other models finish in time.

## Suggested fix
In the Gemini handler within `BYOKLLMGateway.generate()` (or wherever the per-model call happens):
- Capture and store the actual exception message in the error field
- Check for `finish_reason` / `block_reason` in the Gemini response
- Log the raw Gemini response on failure for debugging
