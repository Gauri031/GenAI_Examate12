"""Day 01 - while-loop menu for PoshanGuide."""

import os
from pathlib import Path

try:  # optional: read settings from the global .env at the repo root
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
except ImportError:
    pass

SUGAR_PER_TSP_G = float(os.getenv("SUGAR_PER_TSP_G", "4"))  # approx grams of sugar in 1 level teaspoon
SUGAR_LIMIT_G = float(os.getenv("SUGAR_LIMIT_G", "25"))     # upper end of the 20-25 g daily limit

SAMPLE_QUESTIONS = [
    "How much sugar per day is okay for an adult according to ICMR?",
    "Should I take protein supplements to build muscle?",
]


def about():
    print("\nPoshanGuide answers everyday eating questions from ICMR-NIN DGI 2024.")
    print("General information only - not medical advice.")


def sample_questions():
    print("\nSample questions:")
    for i, q in enumerate(SAMPLE_QUESTIONS, 1):
        print(f"  {i}) {q}")


def sugar_rule_check():
    try:
        cups = int(input("Cups of chai per day: "))
        spoons = float(input("Spoons of sugar per cup: "))
    except ValueError:
        print("Please enter numbers only.")
        return
    grams = cups * spoons * SUGAR_PER_TSP_G
    print(f"Approx. sugar from chai: {grams:.0f} g/day")
    if grams > SUGAR_LIMIT_G:
        print(f"Over the {SUGAR_LIMIT_G} g limit. Try fewer spoons per cup.")
    elif grams > 0.8 * SUGAR_LIMIT_G:
        print("Close to the limit. Watch other sugary foods.")
    else:
        print("Within the limit.")


while True:
    print("\n--- PoshanGuide Menu ---")
    print("1. About PoshanGuide")
    print("2. Sample questions")
    print("3. Sugar rule check (chai)")
    print("0. Exit")
    choice = input("Choose: ").strip()
    if choice == "1":
        about()
    elif choice == "2":
        sample_questions()
    elif choice == "3":
        sugar_rule_check()
    elif choice == "0":
        print("Goodbye!")
        break
    else:
        print("Invalid choice, try again.")
