# 🛡️ Phishing Simulator - Cyber Awareness Trainer

**A free, interactive Python tool to train yourself (or others) to spot phishing emails using real-world examples from a Kaggle dataset.**

Built as part of my post-BICT project portfolio in Mbombela, Mpumalanga.

## Features
- Real phishing & legitimate emails from 70k+ Kaggle dataset
- Interactive 8-question quiz with instant feedback
- Red-flag explanations (urgent language, fake links, etc.)
- Score history saved automatically
- Clean coloured terminal interface
- Menu-driven (quiz or single example)

## How to Run
1. Clone the repo
2. `conda activate base` (or your env)
3. `pip install -r requirements.txt`
4. `python src/main.py`

## Project Structure

            phishing-simulator-trainer/
            ├── data/                  # Kaggle CSVs (CEAS_08.csv, Enron.csv, etc.)
            ├── src/
            │   └── main.py            # All code (menu + quiz + logging)
            ├── requirements.txt
            ├── score_history.csv      # Auto-created after first quiz
            └── README.md


## Future Scalability Ideas (v2+)
- Add AI-generated phishing emails (Hugging Face)
- Web dashboard with Streamlit (deploy free on Streamlit Cloud)
- User accounts & progress tracking
- Mobile version (convert to .apk with BeeWare)
- Export training certificates
- Add South African-specific scams (SARS, FNB, Capitec, etc.)

## License
MIT License — feel free to use, modify, and share.

Made by Tumiso | February 2026 | Ready for BICT honours or job applications!