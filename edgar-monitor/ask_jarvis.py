#!/usr/bin/env python3
"""Ask Jarvis to analyze pattern detection results"""
import json
import requests

JARVIS_URL = "https://staging.nodes.bio/api/jarvis/generate"
JARVIS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYTZmYjFmOTM4OTQ3ZjJhZCIsImVtYWlsIjoiam9obkBub2Rlcy5iaW8iLCJleHAiOjE3NzU0OTg4MjYsImlhdCI6MTc3MjkwNjgyNn0.8NVXoJByiRCHhOaptfTdbIkcjMpOkMQtCqbKPPIwL2w"

def ask_jarvis(prompt, models=["anthropic", "openai"]):
    """Query Jarvis API"""
    headers = {
        "Authorization": f"Bearer {JARVIS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "prompt": prompt,
        "models": models
    }
    
    # Submit request
    resp = requests.post(JARVIS_URL, headers=headers, json=data, timeout=30)
    result = resp.json()
    
    if resp.status_code != 200:
        return result
    
    # Poll for results
    poll_url = f"https://staging.nodes.bio{result['poll_url']}"
    request_id = result['request_id']
    
    print(f"Request ID: {request_id}")
    print("Waiting for responses...", end='', flush=True)
    
    import time
    for _ in range(30):  # Poll for up to 30 seconds
        time.sleep(1)
        print('.', end='', flush=True)
        
        poll_resp = requests.get(poll_url, headers=headers, timeout=10)
        poll_data = poll_resp.json()
        
        if poll_data['status'] == 'completed':
            print(" Done!")
            return poll_data['models']
    
    print(" Timeout!")
    return result

if __name__ == '__main__':
    # Load pattern detection results
    with open('data/pattern_detection.json', 'r') as f:
        results = json.load(f)
    
    # Build prompt
    prompt = f"""Analyze these market open patterns from {results['total_stocks']} micro-cap stocks:

ANOMALIES ({len(results['anomalies'])} stocks):
"""
    for a in results['anomalies'][:5]:
        prompt += f"- {a['symbol']}: {a['change_percent']:+.2f}% on {a['volume']:,} volume\n"
    
    prompt += f"\nCLUSTERS ({len(results['clusters'])} patterns):\n"
    for cluster_id, members in results['clusters'].items():
        avg_change = sum(m['change_percent'] for m in members) / len(members)
        avg_volume = sum(m['volume'] for m in members) / len(members)
        symbols = [m['symbol'] for m in members]
        prompt += f"- Cluster {cluster_id}: {len(members)} stocks, {avg_change:+.2f}% avg, {int(avg_volume):,} vol\n"
        prompt += f"  Members: {', '.join(symbols[:5])}\n"
    
    prompt += """
Questions:
1. Which anomalies are most interesting for further investigation?
2. What trading strategies fit each cluster pattern?
3. Any red flags or risks to watch?

Keep it concise and actionable."""
    
    print("🤖 Asking Jarvis...")
    print("="*60)
    
    response = ask_jarvis(prompt)
    
    # Display responses
    for model, result in response.items():
        print(f"\n📊 {model.upper()}")
        print("-"*60)
        if isinstance(result, dict):
            print(result.get('response', result.get('error', 'No response')))
        else:
            print(result)
    
    # Save
    with open('data/jarvis_analysis.json', 'w') as f:
        json.dump(response, f, indent=2)
    
    print("\n" + "="*60)
    print("💾 Saved to data/jarvis_analysis.json")
