import os
from dotenv import load_dotenv

load_dotenv()

# Twitter API Configuration
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

# RSS Feed Sources
RSS_FEEDS = {
    "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "The Block": "https://www.theblock.co/rss.xml",
    "Decrypt": "https://decrypt.co/feed",
    "Cointelegraph": "https://cointelegraph.com/rss",
    "DeFi Pulse": "https://defipulse.com/blog/rss.xml",
    "a16z Crypto": "https://a16zcrypto.com/feed/",
    "Fintech Takes": "https://www.fintechgtm.substack.com/feed",
    "Andreessen Horowitz": "https://a16z.com/feed/",
    "CB Insights": "https://www.cbinsights.com/feed",
    "TechCrunch Fintech": "https://techcrunch.com/category/fintech/feed/"
}

# Twitter Accounts to Monitor (fintech/crypto influencers)
TWITTER_ACCOUNTS = [
    "naval",
    "balajis", 
    "VitalikButerin",
    "satoshilite",
    "APompliano",
    "CremeDeLaCrypto",
    "WuBlockchain",
    "DegenSpartan",
    "stani",
    "hasufl",
    "ryan_s_adams",
    "sassal0x",
    "BanklessHQ",
    "SimonDixonTwitt",
    "RyanSAdams",
    "cburniske"
]

# Keywords for filtering
FINTECH_KEYWORDS = [
    "fintech", "defi", "crypto", "blockchain", "bitcoin", "ethereum", 
    "web3", "nft", "dao", "yield", "staking", "lending", "trading",
    "payments", "banking", "dex", "cefi", "tvl", "protocol", "token",
    "startup", "funding", "vc", "investment", "regulation", "cbdc"
]

# Database configuration
DB_PATH = "fintech_news.db"