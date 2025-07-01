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

import os
import subprocess
from dotenv import load_dotenv

load_dotenv()

def run_sonarcloud_scan(scan_dir="elsai-model"):
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
        return False

    try:
        # Use the correct pysonar parameters (not --organization, but --sonar-organization)
        result = subprocess.run([
            "pysonar",
            "--token", sonar_token,
            "--sonar-project-key", sonar_project_key,
            "--sonar-organization", sonar_org,
            "--sonar-sources", scan_dir,
            "--sonar-host-url", "https://sonarcloud.io"
        ], capture_output=True, text=True)

        print(result.stdout)
        if result.returncode != 0:
            print("❌ SonarCloud scan failed:\n", result.stderr)
            
            # Check for specific automatic analysis error
            if "manual analysis while Automatic Analysis is enabled" in result.stderr:
                print("\n💡 Solution: Go to your SonarCloud project → Administration → Analysis Method")
                print("   and disable 'Automatic Analysis' to use manual scanning.")
            
            return False

        print("✅ SonarCloud scan completed successfully.")
        return True
    except FileNotFoundError:
        print("❌ 'pysonar' is not installed. Run: pip install pysonar")
        return False

if __name__ == "__main__":
    if run_sonarcloud_scan("elsai-model"):
        print("🎉 SonarCloud scan completed successfully!")
    else:
        print("⚠️ SonarCloud scan encountered issues. Please check the logs above.")