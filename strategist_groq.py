import requests
import os

# Load your Groq API key from environment variable
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Sample portfolio
cash_balance = 35.35
portfolio = [
    {"ticker": "DFNG", "shares": 85, "price": 34.57},
    {"ticker": "NWG", "shares": 109, "price": 4.588},
    {"ticker": "VUSA", "shares": 69, "price": 82.5575},
    {"ticker": "VUKG", "shares": 149, "price": 44.295},
    {"ticker": "CABP", "shares": 1280, "price": 0.4445},
    {"ticker": "TR28", "shares": 50, "price": 1.0676},
    {"ticker": "CU31", "shares": 44, "price": 9331.50},
    {"ticker": "HSBCEM", "shares": 32.645, "price": 19.311}
]

# Market summary input
market_view = (
    "Tech stocks are volatile due to interest rate uncertainty. "
    "Healthcare and dividend-paying stocks are showing strength."
)

# Prompt to send to the AI
prompt = f"""
You are a portfolio strategist creating trade recommendations for a retail investor.

Your job is to:
- Analyze the current portfolio and market view
- Suggest simple, specific buy/sell trades
- Ensure the total cost of buys does not exceed £{cash_balance} plus any proceeds from sells

Portfolio:
{portfolio}

Market View:
{market_view}

Response format:

🔴 Sell [X] shares of [Name] ([TICKER]) at £[PRICE]  
🟢 Buy [X] shares of [Name] ([TICKER]) at £[PRICE]  
✅ Hold [X] shares of [Name] ([TICKER]) at £[PRICE]

At the end, include:
- 💰 Total value of sells
- 💸 Total cost of buys
- 🏦 Estimated cash left

Be concise and only include actions that are affordable and actionable now.
"""

# Prepare the API request
headers = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "model": "llama3-8b-8192",
    "temperature": 0.3,  # lower = more consistent
    "seed": 42,          # fixed output each time
    "messages": [
        {"role": "system", "content": "You are a portfolio strategist."},
        {"role": "user", "content": prompt}
    ]
}

# Send the request to Groq
response = requests.post(
    "https://api.groq.com/openai/v1/chat/completions",
    headers=headers,
    json=data
)

# Output the results
print("🔍 Raw response from Groq:")
print(response.status_code)
print(response.text)

# Try to parse the strategy if available
try:
    content = response.json()["choices"][0]["message"]["content"]
    print("\n🧠 Strategy Suggestions:\n")
    print(content)
except KeyError:
    print("\n❌ Error: 'choices' not found in response. Check the model name, API key, or request format.")
