import subprocess

portfolio = [
    {"ticker": "AAPL", "shares": 30, "price": 150},
    {"ticker": "TSLA", "shares": 10, "price": 700},
    {"ticker": "JNJ", "shares": 20, "price": 160}
]

market_summary = (
    "Tech stocks are experiencing volatility due to interest rate uncertainty. "
    "Healthcare and dividend-paying stocks are showing relative strength."
)

# Format input for the model
prompt = f"""
You are a portfolio strategist. Analyze the following portfolio and suggest a rebalancing or new trade ideas.
Portfolio:
{portfolio}

Current market view:
{market_summary}

Give clear suggestions in plain English with rationale.
"""

# Call Mistral locally via Ollama
def call_ollama(prompt):
    result = subprocess.run(
        ["ollama", "run", "mistral"],
        input=prompt,
        text=True,
        capture_output=True
    )
    return result.stdout

response = call_ollama(prompt)
print("\n🔍 Strategy Suggestions:\n")
print(response)
