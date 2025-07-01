import subprocess
import json
import sys
from pathlib import Path
from communicate import communicate  # Assuming your email code is in communicate.py
from dotenv import load_dotenv
import base64
load_dotenv()
# === CONFIGURATION ===
SCAN_DIR = "elsai_model"
REPORT_FILE = "bandit_report.json"
SENDER_EMAIL = "abhinivesh.s@optisolbusiness.com"

# === Get Last Commit Author Email ===
def get_git_author_email():
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--pretty=format:%ae"],
            stdout=subprocess.PIPE,
            check=True,
            text=True
        )
        email = result.stdout.strip()
        print(f"📧 Commit Author Email: {email}")
        return email
    except subprocess.CalledProcessError:
        print("❗ Failed to get Git commit author email.")
        sys.exit(1)

# === Run Bandit ===
def run_bandit():
    print(f"🚨 Running Bandit scan on '{SCAN_DIR}'...")
    result = subprocess.run([
        "bandit", "-r", SCAN_DIR, "-f", "json", "-o", REPORT_FILE
    ])
    
    if result.returncode != 0:
        print("⚠️ Bandit found issues (expected). Continuing to email the report...")


# === Parse Bandit Report ===
def parse_issues():
    if not Path(REPORT_FILE).exists():
        print("❗ Report file not found.")
        sys.exit(1)
    with open(REPORT_FILE) as f:
        data = json.load(f)
    return data.get("results", [])

# === Format Body for Email ===
def format_email_body(issues):
    return (
        "⚠️ Build failed due to security issues found by Bandit.\n\n"
        "Please refer to the attached Bandit report (`bandit_report.json`) for details.\n"
        "Fix the issues and push the changes again.\n"
    )

# === Main Execution ===
if __name__ == "__main__":
    author_email = get_git_author_email()
    run_bandit()
    issues = parse_issues()
    print(author_email)

    print(f"🔍 Found {len(issues)} issues in Bandit report.")
    if issues:
        subject = "[Bandit] 🚨 Security Scan Failed"
        body = format_email_body(issues)

        # === Prepare attachment ===
        with open(REPORT_FILE, "rb") as f:
            file_bytes = f.read()
            encoded = base64.b64encode(file_bytes).decode('utf-8')

        attachments = [{
            "name": REPORT_FILE,
            "contentBytes": encoded
        }]

        communicate(
            subject=subject,
            sender_email=SENDER_EMAIL,
            recipient_email=author_email,
            body=body,
            attachments=attachments  # 👈 include attachment
        )

        sys.exit(1)
    else:
        print("✅ No security issues found by Bandit.")
        sys.exit(0)
