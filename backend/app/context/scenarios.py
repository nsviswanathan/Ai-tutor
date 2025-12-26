from __future__ import annotations

SCENARIOS = {
    "Airport": [
        "You are at the check-in counter. Your bag is overweight. Ask what you can do.",
        "You missed your connection. Talk to the airline staff to rebook.",
        "Security asks you to remove items from your bag. Ask what is allowed."
    ],
    "Restaurant": [
        "You want a table for two and have dietary restrictions. Make the request.",
        "Your order arrived wrong. Politely ask for a fix.",
        "Ask for recommendations and then order with modifications."
    ],
    "Classroom": [
        "You didn’t understand the assignment. Ask the professor for clarification.",
        "You want to form a study group. Invite a classmate.",
        "Ask for an extension with a valid reason."
    ],
    "Office": [
        "You need to give a status update to your manager.",
        "A teammate disagrees with your approach. Resolve it respectfully.",
        "You want to schedule a meeting across time zones."
    ],
    "Shopping": [
        "You want to return an item without a receipt. Explain your situation.",
        "Ask about discounts and warranties.",
        "The product is out of stock. Ask for alternatives."
    ],
}

def pick_scenario(context: str) -> str:
    arr = SCENARIOS.get(context) or SCENARIOS["Airport"]
    # simple deterministic-ish pick
    return arr[0]
