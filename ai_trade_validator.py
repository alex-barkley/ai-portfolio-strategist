# ai_trade_validator.py (FT + Bloomberg RSS + daily email with strategic suggestions)
import requests
import os
import re
import csv
import feedparser
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load portfolio and cash balance from CSV
def load_portfolio_from_csv(path):
    portfolio = []
    cash_balance = 0
    with open(path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row["ticker"].upper() == "CASH":
                cash_balance = float(row["price"])
            else:
                portfolio.append({
                    "ticker": row["ticker"],
                    "name": row["name"],
                    "shares": float(row["shares"]),
                    "price": float(row["price"])
                })
    return portfolio, cash_balance

# Load from CSV
portfolio, cash_balance = load_portfolio_from_csv("portfolio.csv")

# === Pull headlines from FT and Bloomberg RSS feeds ===
feeds = [
    "https://www.ft.com/?format=rss",
    "https://www.ft.com/world?format=rss",
    "https://www.bloomberg.com/feed/podcast/etf-report.xml",
    "https://www.bloomberg.com/feeds/politics.xml"
]

headlines = []
for url in feeds:
    feed = feedparser.parse(url)
    headlines += [entry.title for entry in feed.entries[:3]]  # limit per feed

headline_text = "\n".join([f"- {title}" for title in headlines])
summary_prompt = f"""
Summarize the following headlines into a short market view with 2-3 sentences, touching on trends in tech, bonds, UK stocks, and dividend income if possible:
{headline_text}
"""

# === Summarize market view using Groq ===
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
headers = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "model": "llama3-8b-8192",
    "messages": [
        {"role": "system", "content": "You are a financial market analyst."},
        {"role": "user", "content": summary_prompt}
    ]
}

summary_response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
market_view = summary_response.json()["choices"][0]["message"]["content"]

# === Build strategy prompt ===
def format_portfolio(portfolio):
    return "\n".join([
        f"{p['shares']} shares of {p['name']} ({p['ticker']}) at £{p['price']:.2f}" for p in portfolio
    ])

prompt = f"""
You are a portfolio strategist.

Here is the portfolio:
{format_portfolio(portfolio)}

Available cash: £{cash_balance:.2f}

Market View:
{market_view}

Provide high-level strategy guidance only. Avoid numeric recommendations. Example:
- 🔄 Consider trimming [TICKER] if overexposed to tech
- 📈 Explore adding more defensive or income-generating assets
- 🛑 Avoid large reallocations unless strong conviction
"""

data = {
    "model": "llama3-8b-8192",
    "messages": [
        {"role": "system", "content": "You are a financial portfolio strategist."},
        {"role": "user", "content": prompt}
    ]
}

response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
strategy_output = response.json()["choices"][0]["message"]["content"]

print("\n🧠 Market View:\n")
print(market_view)
print("\n📈 Strategy Suggestions:\n")
print(strategy_output)

# === Send results by email ===
email_content = f"""
🧠 Market View:
{market_view}

📈 Strategy Suggestions:
{strategy_output}
"""

email_user = os.getenv("EMAIL_USER")
email_pass = os.getenv("EMAIL_PASS")
email_to = os.getenv("EMAIL_TO")

msg = MIMEMultipart()
msg["From"] = email_user
msg["To"] = email_to
msg["Subject"] = "🧠 Daily AI Portfolio Strategy Update"
msg.attach(MIMEText(email_content, "plain"))

try:
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(email_user, email_pass)
    server.sendmail(email_user, email_to, msg.as_string())
    server.quit()
    print("📧 Email sent successfully.")
except Exception as e:
    print(f"❌ Email failed: {e}")
