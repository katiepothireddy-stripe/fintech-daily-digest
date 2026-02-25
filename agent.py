import feedparser
import requests
import os
import json
from datetime import datetime, timedelta
from google import genai

# ============================================
# CONFIGURATION
# ============================================
YOUR_EMAIL = "katiepothireddy@gmail.com"  # Change to your email

NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
BREVO_API_KEY = os.environ.get("BREVO_API_KEY")

# ============================================
# STRIPE SESSION TRACKS
# ============================================
TRACKS = {
    "Advancing Developer Craft": {
        "description": (
            "How developers are designing and scaling applications that "
            "integrate payments, financial services, and emerging "
            "technologies into the fabric of their businesses."
        ),
        "keywords": [
            "developer", "API", "SDK", "integration", "infrastructure",
            "engineering", "open source", "developer tools", "fintech stack",
            "payments API", "embedded finance", "BaaS", "microservices",
            "developer experience", "low-code", "no-code", "serverless",
        ],
    },
    "Designing Adaptive Revenue Models": {
        "description": (
            "How to support complex revenue models, simplify compliance, "
            "and scale efficiently as your business grows."
        ),
        "keywords": [
            "subscription", "pricing", "revenue", "billing", "SaaS",
            "usage-based", "monetization", "recurring revenue", "compliance",
            "tax", "invoicing", "revenue recognition", "metered billing",
            "hybrid pricing", "PLG", "product-led growth",
        ],
    },
    "Charting the Future of Payments": {
        "description": (
            "Technology and trends from AI to regulatory shifts reshaping "
            "cross-border commerce and how to optimize payments performance "
            "on a global scale."
        ),
        "keywords": [
            "payments", "cross-border", "real-time payments",
            "instant payments", "payment processing", "acquiring",
            "issuing", "card network", "open banking", "A2A", "FedNow",
            "Pix", "UPI", "payment rails", "interchange",
            "payment optimization", "authorization rates",
            "3DS", "SCA", "PSD3", "ISO 20022",
        ],
    },
    "Optimizing the Economics of Risk": {
        "description": (
            "Strategies to address emerging fraud patterns, including using "
            "AI to make more efficient decisions about risk management."
        ),
        "keywords": [
            "fraud", "risk", "chargeback", "dispute",
            "identity verification", "KYC", "AML",
            "anti-money laundering", "authentication", "biometric",
            "scam", "deepfake", "synthetic identity",
            "transaction monitoring", "risk scoring",
            "machine learning fraud",
        ],
    },
    "Growing Platform Economies": {
        "description": (
            "Designing, scaling, and monetizing business models that "
            "facilitate transactions between buyers and sellers on a "
            "platform or marketplace."
        ),
        "keywords": [
            "marketplace", "platform", "gig economy", "two-sided",
            "multi-sided", "seller", "merchant onboarding", "payouts",
            "split payments", "escrow", "platform payments", "commerce",
            "e-commerce", "connected accounts", "vertical SaaS",
        ],
    },
    "Reaching Global Markets with Stablecoins and Crypto": {
        "description": (
            "Launching borderless financial services, reaching new "
            "customers, and reducing costs with comprehensive crypto "
            "infrastructure."
        ),
        "keywords": [
            "stablecoin", "crypto", "USDC", "USDT", "blockchain",
            "digital assets", "DeFi", "web3", "tokenization",
            "bridge", "on-ramp", "off-ramp", "wallet",
            "digital currency", "CBDC", "bitcoin", "ethereum",
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
    "https://thenewstack.io/feed/",
    "https://sdtimes.com/feed/",
]

SEARCH_TERMS = [
    "fintech",
    "digital payments",
    "payment processing",
    "neobank digital banking",
    "fintech fraud prevention",
    "marketplace platform payments",
    "stablecoin crypto payments",
    "fintech API developer",
    "Stripe payments",
    "subscription billing SaaS",
]

# ============================================
# COLLECT NEWS FROM RSS FEEDS
# ============================================
def collect_rss_news():
    print("Collecting from RSS feeds...")
    articles = []

    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:10]:
                articles.append({
                    "title": entry.get("title", "No title"),
                    "summary": entry.get("summary", "")[:500],
                    "source": feed.feed.get("title", "Unknown"),
                    "link": entry.get("link", ""),
                })
        except Exception as e:
            print(f"  Error with {feed_url}: {e}")

    print(f"  Found {len(articles)} articles from RSS")
    return articles

# ============================================
# COLLECT NEWS FROM NEWSAPI
# ============================================
def collect_newsapi_news():
    print("Collecting from NewsAPI...")
    articles = []
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    for term in SEARCH_TERMS:
        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": term,
                "from": yesterday,
                "sortBy": "relevancy",
                "language": "en",
                "pageSize": 10,
                "apiKey": NEWS_API_KEY,
            }
            response = requests.get(url, params=params)
            data = response.json()

            for article in data.get("articles", []):
                articles.append({
                    "title": article.get("title", "No title"),
                    "summary": (
                        article.get("description") or ""
                    )[:500],
                    "source": article.get(
                        "source", {}
                    ).get("name", "Unknown"),
                    "link": article.get("url", ""),
                })
        except Exception as e:
            print(f"  Error searching '{term}': {e}")

    print(f"  Found {len(articles)} articles from NewsAPI")
    return articles

# ============================================
# REMOVE DUPLICATE ARTICLES
# ============================================
def remove_duplicates(articles):
    seen = set()
    unique = []
    for article in articles:
        key = article["title"].lower().strip()[:60]
        if key not in seen and key != "no title":
            seen.add(key)
            unique.append(article)
    print(f"After removing duplicates: {len(unique)} articles")
    return unique

# ============================================
# BUILD TRACK INFO FOR THE AI
# ============================================
def build_track_descriptions():
    text = ""
    for track_name, track_info in TRACKS.items():
        text += f"\n**{track_name}**\n"
        text += f"  Focus: {track_info['description']}\n"
        text += (
            f"  Related topics: "
            f"{', '.join(track_info['keywords'][:10])}\n"
        )
    return text

# ============================================
# GENERATE THE SUMMARY WITH AI
# ============================================
def generate_summary(articles):
    print("Generating summary with Gemini...")

    articles_text = ""
    for i, a in enumerate(articles[:50], 1):
        articles_text += f"""
Article {i}:
Title: {a['title']}
Source: {a['source']}
Summary: {a['summary']}
Link: {a['link']}
---"""

    track_descriptions = build_track_descriptions()

    prompt = f"""You are a senior fintech analyst who also advises 
Stripe's content marketing team. You are writing a daily internal 
briefing for {datetime.now().strftime('%A, %B %d, %Y')}.

You have deep knowledge of:
- Stripe's products (Payments, Billing, Connect, Radar, Treasury, 
  Issuing, Atlas, Identity, Tax, Revenue Recognition, Bridge and 
  stablecoins)
- Stripe's position as payments infrastructure for the internet
- The competitive landscape (Adyen, PayPal/Braintree, Square/Block, 
  Checkout.com, Worldpay, Marqeta, Plaid, etc.)

Here are today's fintech articles:
{articles_text}

Here are the content tracks I need you to organize news around:
{track_descriptions}

Please create a daily digest with ALL of the following sections 
in this exact order:

============================================================
SECTION 1: TOP 3 STORIES
============================================================
The three most significant stories of the day. For each:
- Headline and source with link
- 3-4 sentence summary of what happened and why it matters
- "What this means for Stripe:" 2-3 sentences analyzing how 
  this news could affect Stripe's business, competitive position, 
  product strategy, or customers. Be specific about which Stripe 
  products or initiatives are relevant.
- "Content angle:" 1-3 sentences suggesting how Stripe's content 
  marketing team could respond. Think blog posts, case studies, 
  data reports, developer tutorials, thought leadership, social 
  posts, or event session topics. Be specific and actionable.

============================================================
SECTION 2: NEWS BY TRACK
============================================================
Organize the remaining notable stories under these six track 
headings. For each track, include:

**Track Name**
(Track description in italics)

Then for each story under that track:
- Story headline, source, and link
- 1-2 sentence summary
- "Stripe relevance:" One sentence on the connection to Stripe
- "Content angle:" One sentence content idea

If a track has no relevant news today, write "No major stories 
today" and suggest one proactive content idea related to the 
track theme.

The six tracks are:
1. Advancing Developer Craft
2. Designing Adaptive Revenue Models
3. Charting the Future of Payments
4. Optimizing the Economics of Risk
5. Growing Platform Economies
6. Reaching Global Markets with Stablecoins and Crypto

============================================================
SECTION 3: WHAT THIS MEANS FOR STRIPE — STRATEGIC OVERVIEW
============================================================
A 4-6 sentence paragraph that synthesizes ALL of today's news 
into a strategic view for Stripe. Consider:
- Competitive implications
- Product opportunities or threats
- Market shifts that affect Stripe's customers
- Regulatory changes that could impact Stripe's roadmap
Be candid, specific, and analytical. Reference specific Stripe 
products.

============================================================
SECTION 4: CONTENT MARKETING CHEAT SHEET
============================================================
A quick-reference list with:
- 3-5 concrete content ideas inspired by today's news
- For each: the format (blog, tutorial, data report, social 
  thread, video, case study, etc.), the target audience 
  (developers, founders, finance teams, etc.), the relevant 
  track, and a one-line pitch

============================================================
SECTION 5: TRENDS TO WATCH
============================================================
2-3 emerging patterns you notice across today's news that 
Stripe should be paying attention to over the coming weeks 
and months.

============================================================
SECTION 6: QUICK HITS
============================================================
Any remaining noteworthy stories in one line each with 
source links.

============================================================

FORMATTING RULES:
- Use clear headers and dividers between sections
- Use plain text with simple markers like * for bullets
- Keep it scannable — busy people will skim this
- Always attribute stories to their source
- Include links wherever possible
- Be opinionated and specific — generic insights are not useful
- If a story directly mentions Stripe, flag it prominently
"""

    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt,
    )

    return response.text

# ============================================
# SEND THE EMAIL
# ============================================
def send_email(summary):
    print("Sending email via Brevo...")

    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": BREVO_API_KEY,
    }

    today = datetime.now().strftime("%b %d, %Y")

    html_summary = summary.replace("\n", "<br>")
    html_summary = html_summary.replace(
        "============================================================",
        "<hr style='border:1px solid #635BFF;'>",
    )

    html_body = f"""
    <html>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 
    'Segoe UI', Roboto, sans-serif; max-width: 800px; 
    margin: 0 auto; padding: 20px; color: #333; 
    line-height: 1.6;">
        <div style="background: linear-gradient(135deg, #635BFF, 
        #7A73FF); padding: 30px; border-radius: 12px; 
        margin-bottom: 30px;">
            <h1 style="color: white; margin: 0; font-size: 24px;">
                Fintech Daily Digest
            </h1>
            <p style="color: rgba(255,255,255,0.85); 
            margin: 8px 0 0 0; font-size: 14px;">
                {datetime.now().strftime('%A, %B %d, %Y')} | 
                Stripe Strategic and Content Intelligence
            </p>
        </div>
        <div style="font-size: 14px;">
            {html_summary}
        </div>
        <div style="margin-top: 40px; padding-top: 20px; 
        border-top: 1px solid #eee; font-size: 12px; 
        color: #888;">
            Generated automatically by your Fintech News Agent.
        </div>
    </body>
    </html>
    """

    payload = {
        "sender": {
            "name": "Fintech News Agent",
            "email": "digest@fintech-agent.com",
        },
        "to": [{"email": YOUR_EMAIL}],
        "subject": (
            f"Fintech Daily Digest — {today} | "
            f"Stripe Strategy + Content Intel"
        ),
        "htmlContent": html_body,
        "textContent": summary,
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 201:
        print("  Email sent successfully!")
    else:
        print(
            f"  Email error: {response.status_code} "
            f"- {response.text}"
        )

# ============================================
# MAIN — RUN EVERYTHING
# ============================================
def main():
    print("=" * 60)
    print("FINTECH NEWS AGENT — STRIPE EDITION")
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    all_articles = []
    all_articles.extend(collect_rss_news())
    all_articles.extend(collect_newsapi_news())

    all_articles = remove_duplicates(all_articles)

    if not all_articles:
        print("No articles found today. Exiting.")
        return

    print(
        f"\nTotal unique articles to analyze: "
        f"{len(all_articles)}"
    )

    summary = generate_summary(all_articles)
    print("\n--- PREVIEW ---")
    print(summary[:500] + "...")

    send_email(summary)

    print("\nDone!")

if __name__ == "__main__":
    main()
