import feedparser
import requests
import os
from datetime import datetime, timedelta
from google import genai

# ============================================
# CONFIGURATION
# ============================================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO_NAME = os.environ.get("GITHUB_REPOSITORY")

# ============================================
# STRIPE SESSION TRACKS
# ============================================
TRACKS = {
    "Advancing Developer Craft": {
        "description": (
            "How developers are designing and scaling "
            "applications that integrate payments, financial "
            "services, and emerging technologies into the "
            "fabric of their businesses."
        ),
        "keywords": [
            "developer", "API", "SDK", "integration",
            "infrastructure", "engineering", "open source",
            "developer tools", "fintech stack", "payments API",
            "embedded finance", "BaaS", "microservices",
            "developer experience", "low-code", "no-code",
            "serverless",
        ],
    },
    "Designing Adaptive Revenue Models": {
        "description": (
            "How to support complex revenue models, simplify "
            "compliance, and scale efficiently as your "
            "business grows."
        ),
        "keywords": [
            "subscription", "pricing", "revenue", "billing",
            "SaaS", "usage-based", "monetization",
            "recurring revenue", "compliance", "tax",
            "invoicing", "revenue recognition",
            "metered billing", "hybrid pricing", "PLG",
            "product-led growth",
        ],
    },
    "Charting the Future of Payments": {
        "description": (
            "Technology and trends from AI to regulatory "
            "shifts reshaping cross-border commerce and how "
            "to optimize payments performance on a global "
            "scale."
        ),
        "keywords": [
            "payments", "cross-border", "real-time payments",
            "instant payments", "payment processing",
            "acquiring", "issuing", "card network",
            "open banking", "A2A", "FedNow", "Pix", "UPI",
            "payment rails", "interchange",
            "payment optimization", "authorization rates",
            "3DS", "SCA", "PSD3", "ISO 20022",
        ],
    },
    "Optimizing the Economics of Risk": {
        "description": (
            "Strategies to address emerging fraud patterns, "
            "including using AI to make more efficient "
            "decisions about risk management."
        ),
        "keywords": [
            "fraud", "risk", "chargeback", "dispute",
            "identity verification", "KYC", "AML",
            "anti-money laundering", "authentication",
            "biometric", "scam", "deepfake",
            "synthetic identity", "transaction monitoring",
            "risk scoring", "machine learning fraud",
        ],
    },
    "Growing Platform Economies": {
        "description": (
            "Designing, scaling, and monetizing business "
            "models that facilitate transactions between "
            "buyers and sellers on a platform or marketplace."
        ),
        "keywords": [
            "marketplace", "platform", "gig economy",
            "two-sided", "multi-sided", "seller",
            "merchant onboarding", "payouts",
            "split payments", "escrow",
            "platform payments", "commerce", "e-commerce",
            "connected accounts", "vertical SaaS",
        ],
    },
    "Reaching Global Markets with Stablecoins and Crypto": {
        "description": (
            "Launching borderless financial services, "
            "reaching new customers, and reducing costs "
            "with comprehensive crypto infrastructure."
        ),
        "keywords": [
            "stablecoin", "crypto", "USDC", "USDT",
            "blockchain", "digital assets", "DeFi", "web3",
            "tokenization", "bridge", "on-ramp", "off-ramp",
            "wallet", "digital currency", "CBDC", "bitcoin",
            "ethereum",
        ],
    },
}

# ============================================
# NEWS SOURCES
# ============================================
RSS_FEEDS = [
    "https://techcrunch.com/category/fintech/feed/",
    "https://www.finextra.com/rss/headlines.aspx",
    "https://www.pymnts.com/feed/",
    "https://finovate.com/feed/",
    "https://bankingjournal.aba.com/feed/",
    "https://www.paymentsdive.com/feeds/news/",
    "https://thepaypers.com/feed",
    "https://cointelegraph.com/rss",
    "https://www.theblock.co/rss.xml",
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://t
