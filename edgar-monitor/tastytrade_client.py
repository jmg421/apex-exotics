"""Tastytrade API client using official SDK."""
import os
from dotenv import load_dotenv
from tastytrade import Session, Account, DXLinkStreamer
from tastytrade.dxfeed import Quote

load_dotenv()

async def get_session():
    """Get authenticated Tastytrade session."""
    return Session(
        os.getenv("TASTYTRADE_CLIENT_SECRET"),
        os.getenv("TASTYTRADE_REFRESH_TOKEN"),
        is_test=True
    )

async def get_quote(session, symbol):
    """Get real-time quote for a symbol."""
    async with DXLinkStreamer(session) as streamer:
        await streamer.subscribe(Quote, [symbol])
        quote = await streamer.get_event(Quote)
        return quote

if __name__ == "__main__":
    import asyncio
    
    async def main():
        session = await get_session()
        accounts = await Account.get(session)
        print(f"Accounts: {len(accounts)}")
        
        # Test quote
        quote = await get_quote(session, "AAPL")
        print(f"AAPL: ${quote.bid_price} / ${quote.ask_price}")
    
    asyncio.run(main())
