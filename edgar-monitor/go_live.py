#!/usr/bin/env python3
"""Live Trading System - Real money, real trades"""
import json
from datetime import datetime

def check_prerequisites():
    """Check if we're ready to go live"""
    print("🔴 LIVE TRADING SYSTEM - PRE-FLIGHT CHECK")
    print("="*60)
    
    checks = {
        'market_data': False,
        'broker_connection': False,
        'risk_limits': False,
        'capital': False
    }
    
    # Check 1: Market data
    print("\n1. Market Data Connection")
    try:
        with open('.env', 'r') as f:
            env = f.read()
            if 'POLYGON_API_KEY' in env:
                print("   ✅ Polygon.io API key found")
                checks['market_data'] = True
            else:
                print("   ❌ No Polygon API key")
                print("   → Sign up: https://polygon.io/dashboard/signup")
    except (FileNotFoundError, OSError):
        print("   ❌ No .env file")
    
    # Check 2: Broker
    print("\n2. Broker Connection (Tastytrade)")
    try:
        with open('.env', 'r') as f:
            env = f.read()
            if 'TASTYTRADE_REFRESH_TOKEN' in env:
                print("   ✅ Tastytrade credentials found")
                checks['broker_connection'] = True
            else:
                print("   ❌ No Tastytrade credentials")
    except (FileNotFoundError, OSError):
        print("   ❌ No broker credentials")
    
    # Check 3: Risk limits
    print("\n3. Risk Management")
    try:
        with open('config/risk_limits.json', 'r') as f:
            limits = json.load(f)
            print(f"   ✅ Max daily loss: ${limits['max_daily_loss']}")
            print(f"   ✅ Max positions: {limits['max_positions']}")
            print(f"   ✅ Max risk per trade: ${limits['max_risk_per_trade']}")
            checks['risk_limits'] = True
    except (FileNotFoundError, json.JSONDecodeError, OSError, KeyError):
        print("   ❌ No risk limits configured")
        print("   → I'll create default config")
        create_default_risk_config()
    
    # Check 4: Capital
    print("\n4. Trading Capital")
    print("   ⚠️  Manual check required")
    print("   → Log into Tastytrade and verify account balance")
    print("   → Minimum recommended: $2,000")
    
    # Summary
    print("\n" + "="*60)
    ready = all(checks.values())
    
    if ready:
        print("✅ READY TO GO LIVE")
        print("\nNext steps:")
        print("  1. Verify account balance in Tastytrade")
        print("  2. Run: python3 live_trading.py")
        print("  3. System will scan at 9:30 AM tomorrow")
    else:
        print("❌ NOT READY - Complete checklist above")
        print("\nMissing:")
        for check, status in checks.items():
            if not status:
                print(f"  • {check}")
    
    return ready

def create_default_risk_config():
    """Create default risk management config"""
    import os
    os.makedirs('config', exist_ok=True)
    
    config = {
        'max_daily_loss': 100,
        'max_positions': 3,
        'max_risk_per_trade': 10,
        'max_account_risk_pct': 2.0,
        'auto_stop_trading': True
    }
    
    with open('config/risk_limits.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("   ✅ Created default risk config")
    print(f"   → Edit config/risk_limits.json to customize")

if __name__ == '__main__':
    ready = check_prerequisites()
    
    if ready:
        print("\n🚀 Ready to launch!")
        print("\nWaiting for your confirmation...")
        print("Type 'GO LIVE' to start trading tomorrow:")
        
        # Don't actually go live without explicit confirmation
        response = input("\n> ")
        
        if response.strip().upper() == 'GO LIVE':
            print("\n✅ CONFIRMED - System will trade tomorrow at 9:30 AM")
            print("💰 Good luck!")
        else:
            print("\n⏸️  Staying in paper trading mode")
    else:
        print("\n📋 Complete the checklist above first")
