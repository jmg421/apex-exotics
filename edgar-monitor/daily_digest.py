#!/usr/bin/env python3
"""
Daily Digest Generator for ENIS + LLM Analysis
Generates markdown reports from batch analysis results.
"""

import json
from datetime import datetime
from pathlib import Path

def load_reports():
    """Load all LLM analysis reports."""
    reports_file = Path(__file__).parent / 'data' / 'llm_reports.json'
    if not reports_file.exists():
        return []
    
    with open(reports_file) as f:
        data = json.load(f)
        # Convert dict to list
        if isinstance(data, dict):
            return list(data.values())
        return data.get('reports', [])

def categorize_recommendations(reports):
    """Categorize reports into longs, shorts, and passes."""
    longs = []
    shorts = []
    passes = []
    
    for r in reports:
        rec = r.get('recommendation', '').upper()
        risk = r.get('risk_score', 0)
        conviction = r.get('conviction', '').upper()
        
        if rec == 'BUY' and conviction in ['HIGH', 'MEDIUM']:
            longs.append(r)
        elif rec == 'SHORT' or (rec == 'AVOID' and conviction == 'HIGH') or risk >= 7:
            shorts.append(r)
        else:
            passes.append(r)
    
    return longs, shorts, passes

def format_company_section(report):
    """Format a single company recommendation."""
    ticker = report.get('ticker', 'N/A')
    cik = report.get('cik', 'N/A')
    rec = report.get('recommendation', 'N/A')
    conviction = report.get('conviction', 'N/A')
    
    lines = [f"### {ticker} ({cik})"]
    lines.append(f"**Recommendation:** {rec}")
    
    if conviction != 'N/A':
        lines.append(f"**Conviction:** {conviction}")
    
    if 'price_target' in report and report['price_target']:
        lines.append(f"**Price Target:** ${report['price_target']}")
    
    if 'risk_score' in report and report['risk_score']:
        lines.append(f"**Risk Score:** {report['risk_score']}/10")
    
    if 'financial_health' in report and report['financial_health']:
        lines.append(f"**Financial Health:** {report['financial_health']}/10")
    
    if 'enis_score' in report:
        lines.append(f"**ENIS Score:** {report['enis_score']}/100")
    
    # Add key points
    if 'key_risks' in report and report['key_risks']:
        lines.append("\n**Key Risks:**")
        for risk in report['key_risks'][:3]:  # Top 3
            lines.append(f"- {risk}")
    
    if 'key_opportunities' in report and report['key_opportunities']:
        lines.append("\n**Key Opportunities:**")
        for opp in report['key_opportunities'][:3]:  # Top 3
            lines.append(f"- {opp}")
    
    return '\n'.join(lines)

def generate_digest():
    """Generate daily digest markdown report."""
    reports = load_reports()
    longs, shorts, passes = categorize_recommendations(reports)
    
    # Header
    lines = [
        "# ENIS Daily Digest",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Model:** Jarvis (Anthropic Claude)",
        "",
        "---",
        ""
    ]
    
    # Summary statistics
    lines.extend([
        "## Summary",
        f"- **Total Analyzed:** {len(reports)}",
        f"- **Actionable:** {len(longs) + len(shorts)}",
        f"  - Longs: {len(longs)}",
        f"  - Shorts: {len(shorts)}",
        f"- **Passes:** {len(passes)}",
        "",
        "---",
        ""
    ])
    
    # Longs section
    if longs:
        lines.append("## 🟢 Long Opportunities")
        lines.append("")
        for report in longs:
            lines.append(format_company_section(report))
            lines.append("")
    
    # Shorts section
    if shorts:
        lines.append("## 🔴 Short Opportunities")
        lines.append("")
        for report in shorts:
            lines.append(format_company_section(report))
            lines.append("")
    
    # Passes section (summary only)
    if passes:
        lines.append("## ⚪ Passes")
        lines.append("")
        for report in passes:
            ticker = report.get('ticker', 'N/A')
            rec = report.get('recommendation', 'N/A')
            lines.append(f"- **{ticker}**: {rec}")
        lines.append("")
    
    return '\n'.join(lines)

def save_digest(content, filename=None):
    """Save digest to markdown file."""
    if filename is None:
        filename = f"digest_{datetime.now().strftime('%Y%m%d')}.md"
    
    output_dir = Path(__file__).parent / 'data'
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / filename
    with open(output_file, 'w') as f:
        f.write(content)
    
    return output_file

if __name__ == '__main__':
    print("Generating daily digest...")
    digest = generate_digest()
    output_file = save_digest(digest)
    print(f"\n✓ Digest saved to: {output_file}")
    print("\n" + "="*60)
    print(digest)
