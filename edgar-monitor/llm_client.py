#!/usr/bin/env python3
"""
LLM client for ENIS analysis using Jarvis API.
"""

import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

JARVIS_API = "https://staging.nodes.bio/api/jarvis/generate"
JARVIS_STATUS_API = "https://staging.nodes.bio/api/jarvis/status"
JARVIS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYTZmYjFmOTM4OTQ3ZjJhZCIsImVtYWlsIjoiam9obkBub2Rlcy5iaW8iLCJleHAiOjE3NzUzOTUwMTAsImlhdCI6MTc3MjgwMzAxMH0.Mfu8NmolJ02uTs80J9RAbzQvNwZTmgKfSVpVANhtrhc"

def call_llm(prompt, model="anthropic", timeout=30):
    """Call Jarvis API with prompt and wait for response."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {JARVIS_TOKEN}"
    }
    
    # Submit request
    payload = {
        "prompt": prompt,
        "models": [model]
    }
    
    response = requests.post(JARVIS_API, json=payload, headers=headers)
    response.raise_for_status()
    
    data = response.json()
    request_id = data['request_id']
    
    # Poll for completion
    start_time = time.time()
    while time.time() - start_time < timeout:
        status_response = requests.get(
            f"{JARVIS_STATUS_API}/{request_id}",
            headers=headers
        )
        status_response.raise_for_status()
        status_data = status_response.json()
        
        # Check if complete
        if status_data['status'] == 'completed':
            # Extract response from model
            print(f"DEBUG: Status data: {status_data}")
            if 'responses' in status_data and model in status_data['responses']:
                return status_data['responses'][model]['response']
            # Try alternate format
            if 'models' in status_data and model in status_data['models']:
                model_data = status_data['models'][model]
                if 'response' in model_data:
                    return model_data['response']
            raise ValueError(f"Could not find response for {model} in: {status_data}")
        
        # Check if failed
        if status_data['status'] == 'failed':
            raise ValueError(f"Jarvis request failed: {status_data}")
        
        # Wait before polling again
        time.sleep(1)
    
    raise TimeoutError(f"Jarvis request timed out after {timeout}s")

def call_llm_multi(prompt, models=["anthropic", "openai", "google_gemini"], timeout=30):
    """Call multiple models and return all responses."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {JARVIS_TOKEN}"
    }
    
    # Submit request
    payload = {
        "prompt": prompt,
        "models": models
    }
    
    response = requests.post(JARVIS_API, json=payload, headers=headers)
    response.raise_for_status()
    
    data = response.json()
    request_id = data['request_id']
    
    # Poll for completion
    start_time = time.time()
    while time.time() - start_time < timeout:
        status_response = requests.get(
            f"{JARVIS_STATUS_API}/{request_id}",
            headers=headers
        )
        status_response.raise_for_status()
        status_data = status_response.json()
        
        # Check if complete
        if status_data['status'] == 'completed':
            return status_data['responses']
        
        # Check if failed
        if status_data['status'] == 'failed':
            raise ValueError(f"Jarvis request failed: {status_data}")
        
        # Wait before polling again
        time.sleep(1)
    
    raise TimeoutError(f"Jarvis request timed out after {timeout}s")

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
    import re
    
    # Extract recommendation
    rec_match = re.search(r'\b(BUY|HOLD|AVOID)\b', response, re.IGNORECASE)
    recommendation = rec_match.group(1).upper() if rec_match else None
    
    # Extract conviction
    conv_match = re.search(r'\b(HIGH|MEDIUM|LOW)\b', response, re.IGNORECASE)
    conviction = conv_match.group(1).upper() if conv_match else None
    
    # Extract price target
    price_match = re.search(r'\$(\d+\.?\d*)', response)
    price_target = float(price_match.group(1)) if price_match else None
    
    return {
        'recommendation': recommendation,
        'conviction': conviction,
        'price_target': price_target,
        'full_text': response
    }

if __name__ == "__main__":
    # Quick test
    print("Testing LLM connection...")
    response = call_llm("Say 'OK' if you can hear me.")
    print(f"Response: {response}")
