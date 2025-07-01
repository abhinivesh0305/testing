# import os

# def print_tree(start_path='.', prefix=''):
#     files = sorted(os.listdir(start_path))
#     files = [f for f in files if not f.startswith('.')]  # skip hidden files

#     for index, name in enumerate(files):
#         path = os.path.join(start_path, name)
#         connector = '└── ' if index == len(files) - 1 else '├── '
#         print(prefix + connector + name)
#         if os.path.isdir(path):
#             extension = '    ' if index == len(files) - 1 else '│   '
#             print_tree(path, prefix + extension)

# if __name__ == "__main__":
#     print("📁 Project Structure:")
#     print_tree('.')  # Replace '.' with any subfolder if needed

import subprocess
import json
import sys
from pathlib import Path
from communicate import communicate  # Assuming your email code is in communicate.py
from dotenv import load_dotenv
import base64
import os
import requests
import time

load_dotenv()

# === CONFIGURATION ===
# Add this at the beginning of main
if len(sys.argv) > 1:
    SCAN_DIR = sys.argv[1]
else:
    SCAN_DIR = "elsai-model"  # fallback
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
        print("⚠️ Bandit found issues (expected). Continuing to check the report...")
    
    return result.returncode == 0

# === Run SonarCloud Scan ===
def run_sonarcloud_scan(scan_dir="elsai_model"):
    print(f"🚀 Running SonarCloud scan on '{scan_dir}' using pysonar...")

    sonar_token = os.getenv("SONAR_TOKEN")
    sonar_project_key = os.getenv("SONAR_PROJECT_KEY")
    sonar_org = os.getenv("SONAR_ORG")

    # Check for missing variables
    missing = []
    if not sonar_token: missing.append("SONAR_TOKEN")
    if not sonar_project_key: missing.append("SONAR_PROJECT_KEY")
    if not sonar_org: missing.append("SONAR_ORG")

    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        return False, "Missing environment variables"

    try:
        # Use the correct pysonar parameters
        coverage_path = os.path.join(scan_dir, "coverage.xml")
        result = subprocess.run([
            "pysonar",
            "--token", sonar_token,
            "--sonar-project-key", sonar_project_key,
            "--sonar-organization", sonar_org,
            "--sonar-sources", scan_dir,
            "--define sonar.python.coverage.reportPaths", coverage_path,
            "--sonar-host-url", "https://sonarcloud.io"
        ], capture_output=True, text=True)

        print(result.stdout)
        if result.returncode != 0:
            print("❌ SonarCloud scan failed:\n", result.stderr)
            
            # Check for specific automatic analysis error
            if "manual analysis while Automatic Analysis is enabled" in result.stderr:
                print("\n💡 Solution: Go to your SonarCloud project → Administration → Analysis Method")
                print("   and disable 'Automatic Analysis' to use manual scanning.")
            
            return False, result.stderr

        print("✅ SonarCloud scan completed successfully.")
        
        # Check SonarCloud quality gate status
        return check_sonarcloud_quality_gate(sonar_token, sonar_project_key)
        
    except FileNotFoundError:
        error_msg = "'pysonar' is not installed. Run: pip install pysonar"
        print(f"❌ {error_msg}")
        return False, error_msg

# === Check SonarCloud Quality Gate ===
def check_sonarcloud_quality_gate(token, project_key):
    """Check if the SonarCloud quality gate passed"""
    try:
        # Wait a bit for SonarCloud to process the results
        time.sleep(10)
        
        url = f"https://sonarcloud.io/api/qualitygates/project_status"
        params = {"projectKey": project_key}
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            status = data.get("projectStatus", {}).get("status", "UNKNOWN")
            
            if status == "OK":
                print("✅ SonarCloud Quality Gate: PASSED")
                return True, "Quality Gate passed"
            else:
                print(f"❌ SonarCloud Quality Gate: FAILED ({status})")
                conditions = data.get("projectStatus", {}).get("conditions", [])
                failed_conditions = [c for c in conditions if c.get("status") != "OK"]
                
                error_details = f"Quality Gate failed with status: {status}\n"
                if failed_conditions:
                    error_details += "Failed conditions:\n"
                    for condition in failed_conditions:
                        metric = condition.get("metricKey", "Unknown")
                        actual = condition.get("actualValue", "N/A")
                        threshold = condition.get("errorThreshold", "N/A")
                        error_details += f"  - {metric}: {actual} (threshold: {threshold})\n"
                
                return False, error_details
        else:
            error_msg = f"Failed to check quality gate status: HTTP {response.status_code}"
            print(f"⚠️ {error_msg}")
            return True, error_msg  # Don't fail the build if we can't check the status
            
    except Exception as e:
        error_msg = f"Error checking SonarCloud quality gate: {str(e)}"
        print(f"⚠️ {error_msg}")
        return True, error_msg  # Don't fail the build if we can't check the status

# === Parse Bandit Report ===
def parse_bandit_issues():
    if not Path(REPORT_FILE).exists():
        print("❗ Bandit report file not found.")
        return []
    
    try:
        with open(REPORT_FILE) as f:
            data = json.load(f)
        return data.get("results", [])
    except json.JSONDecodeError:
        print("❗ Failed to parse Bandit report JSON.")
        return []

# === Format Email Body ===
def format_email_body(bandit_issues, sonar_failed, sonar_error):
    body = "⚠️ Build failed due to security/quality issues found during scanning.\n\n"
    
    if bandit_issues:
        body += f"🚨 Bandit found {len(bandit_issues)} security issues:\n"
        body += "Please refer to the attached Bandit report (`bandit_report.json`) for details.\n\n"
    
    if sonar_failed:
        body += "🔍 SonarCloud Quality Gate failed:\n"
        body += f"{sonar_error}\n\n"
        body += f"View detailed results at: https://sonarcloud.io/project/overview?id={os.getenv('SONAR_PROJECT_KEY')}\n\n"
    
    body += "Please fix the issues and push the changes again.\n"
    return body

# === Main Execution ===
if __name__ == "__main__":
    author_email = get_git_author_email()
    
    # Run both scans
    bandit_success = run_bandit()
    sonar_success, sonar_error = run_sonarcloud_scan(SCAN_DIR)
    
    # Parse results
    bandit_issues = parse_bandit_issues()
    
    print(f"🔍 Bandit found {len(bandit_issues)} issues.")
    print(f"🔍 SonarCloud scan {'passed' if sonar_success else 'failed'}.")
    
    # Determine if we need to send an email
    has_bandit_issues = len(bandit_issues) > 0
    has_sonar_issues = not sonar_success
    
    if has_bandit_issues or has_sonar_issues:
        # Prepare email details
        issues_found = []
        if has_bandit_issues:
            issues_found.append("Bandit")
        if has_sonar_issues:
            issues_found.append("SonarCloud")
        
        subject = f"[Security Scan] 🚨 {' & '.join(issues_found)} Issues Found"
        body = format_email_body(bandit_issues, has_sonar_issues, sonar_error)
        
        # Prepare attachments
        attachments = []
        if has_bandit_issues and Path(REPORT_FILE).exists():
            with open(REPORT_FILE, "rb") as f:
                file_bytes = f.read()
                encoded = base64.b64encode(file_bytes).decode('utf-8')
            
            attachments.append({
                "name": REPORT_FILE,
                "contentBytes": encoded
            })
        
        # Send email
        communicate(
            subject=subject,
            sender_email=SENDER_EMAIL,
            recipient_email=author_email,
            body=body,
            attachments=attachments
        )
        
        print(f"📧 Email sent to {author_email} about security/quality issues.")
        sys.exit(1)
    else:
        print("✅ No security/quality issues found. Build successful!")
        sys.exit(0)