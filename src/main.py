import random
import textwrap
import pandas as pd
from colorama import Fore, Style, init
import csv
from datetime import datetime    

init(autoreset=True)

# ====================== CONFIG ======================
DATA_FOLDER = "data"
CSV_FILES = [
    f"{DATA_FOLDER}/CEAS_08.csv",
    f"{DATA_FOLDER}/Enron.csv"
]

# Load datasets once
phishing_examples = []
legit_examples = []

print(Fore.CYAN + "🔄 Loading Phishing Email Dataset...")
for file in CSV_FILES:
    try:
        df = pd.read_csv(file, encoding='latin1', on_bad_lines='skip')
        print(Fore.GREEN + f"✅ Loaded {file} — {len(df):,} rows")

        label_col = 'label'
        if label_col in df.columns:
            # Standardise phishing vs legit
            phishing_mask = df[label_col].astype(str).str.contains('1|phishing|spam', case=False, na=False)
            phishing_examples.extend(df[phishing_mask][['subject', 'body']].to_dict('records'))
            legit_examples.extend(df[~phishing_mask][['subject', 'body']].to_dict('records'))
    except Exception as e:
        print(Fore.RED + f"Error with {file}: {e}")

print(Fore.CYAN + f"📊 Total: {len(phishing_examples):,} phishing | {len(legit_examples):,} legit examples\n")

# ====================== HELPER FUNCTIONS ======================
def generate_example(is_phishing: bool):
    if is_phishing and phishing_examples:
        ex = random.choice(phishing_examples)
    elif not is_phishing and legit_examples:
        ex = random.choice(legit_examples)
    else:
        ex = {"subject": "Test Email", "body": "This is a fallback test."}
    return ex["subject"], ex.get("body", "")[:550]   # Truncate for readability

def get_red_flags(subject: str, body: str):
    """Simple keyword-based red flags for training"""
    text = (subject + " " + body).lower()
    flags = []
    if any(word in text for word in ["urgent", "immediately", "suspended", "account locked", "verify now"]):
        flags.append("🚨 Urgent / threatening language")
    if any(word in text for word in ["click here", "update your", "confirm your", "login"]):
        flags.append("🔗 Suspicious call-to-action (links or buttons)")
    if any(word in text for word in ["password", "bank details", "card number", "personal info"]):
        flags.append("💰 Asking for sensitive information")
    if "winner" in text or "prize" in text or "refund" in text:
        flags.append("🎁 Too-good-to-be-true offer")
    if len(flags) == 0:
        flags.append("No obvious red flags in this sample")
    return flags

def show_example(subject, body, is_phishing):
    print(Fore.YELLOW + "\n" + "="*70)
    print(Fore.YELLOW + "📧 EMAIL EXAMPLE")
    print("="*70 + Style.RESET_ALL)
    print(f"Subject: {subject}")
    print("\nBody:")
    print(textwrap.fill(body, width=70))
    print("-"*70)

# ====================== QUIZ FUNCTION ======================
def run_quiz(num_questions=8):
    score = 0
    print(Fore.CYAN + f"\n🎯 Starting {num_questions}-question Phishing Awareness Quiz...\n")

    for q in range(1, num_questions + 1):
        is_phishing = random.choice([True, False])
        subject, body = generate_example(is_phishing)

        show_example(subject, body, is_phishing)

        while True:
            answer = input(Fore.WHITE + "Is this a phishing email? (y/n): ").strip().lower()
            if answer in ['y', 'n']:
                break
            print(Fore.RED + "Please type y or n")

        correct = (answer == 'y' and is_phishing) or (answer == 'n' and not is_phishing)

        if correct:
            score += 1
            print(Fore.GREEN + "✅ Correct!\n")
        else:
            print(Fore.RED + "❌ Wrong!\n")

        # Explanation
        print(Fore.MAGENTA + "📌 Explanation:")
        if is_phishing:
            print(Fore.RED + "   This WAS a phishing email.")
            for flag in get_red_flags(subject, body):
                print(Fore.RED + f"   • {flag}")
        else:
            print(Fore.GREEN + "   This was a legitimate email.")
            print("   • No major red flags — looks normal and safe.")

        input(Fore.WHITE + "\nPress Enter for next question...")

    # Final score
    percentage = (score / num_questions) * 100
    print(Fore.CYAN + "\n" + "="*60)
    print(Fore.CYAN + f"🏆 QUIZ COMPLETE! Your score: {score}/{num_questions} ({percentage:.0f}%)")
    print("="*60 + Style.RESET_ALL)

    save_score(score, num_questions)

    if percentage >= 90:
        print(Fore.GREEN + "🌟 Excellent! You're very phishing-aware.")
    elif percentage >= 70:
        print(Fore.YELLOW + "👍 Good job — just a few more to master.")
    else:
        print(Fore.RED + "💡 Keep practising — phishing tactics evolve quickly!")

def save_score(score: int, total: int):
    """Save quiz result to history.csv"""
    try:
        with open('score_history.csv', 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M"), score, total, round((score/total)*100, 1)])
        print(Fore.GREEN + f"💾 Score saved to score_history.csv")
    except:
        pass  # Silent fail if file locked

# ====================== MAIN MENU ======================
def main_menu():
    while True:
        print(Fore.CYAN + "\n" + "="*50)
        print("   🛡️  PHISHING SIMULATOR - Cyber Awareness Trainer")
        print("="*50 + Style.RESET_ALL)
        print("1. Start Training Quiz (8 questions)")
        print("2. Generate Single Random Example")
        print("3. Exit")
        choice = input(Fore.WHITE + "\nEnter your choice (1-3): ").strip()

        if choice == "1":
            run_quiz(8)
        elif choice == "2":
            is_phish = random.choice([True, False])
            subject, body = generate_example(is_phish)
            show_example(subject, body, is_phish)
            print(Fore.MAGENTA + "\nThis was " + ("PHISHING" if is_phish else "LEGIT"))
        elif choice == "3":
            print(Fore.GREEN + "\nThanks for training! Stay safe online. 👋")
            break
        else:
            print(Fore.RED + "Invalid choice. Please enter 1, 2 or 3.")

# ====================== RUN ======================
if __name__ == "__main__":
    main_menu()