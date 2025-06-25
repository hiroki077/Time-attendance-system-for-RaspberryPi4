#!/usr/bin/env python3
import subprocess
import sys
import os
from pathlib import Path
from getpass import getpass

BASE_DIR = Path(__file__).resolve().parent


def git_commit_push() -> None:
    """Stage everything, commit with a user-entered message, then push."""
    try:
        # Stage changes
        subprocess.run(["git", "-C", str(BASE_DIR), "add", "."], check=True)
        print("✅ git add . completed")

        # Commit message
        msg = input("📝 Enter commit message: ").strip()
        if not msg:
            print("⚠️ Commit message cannot be empty.")
            return

        subprocess.run(["git", "-C", str(BASE_DIR), "commit", "-m", msg], check=True)
        print("✅ git commit completed")

        # Push (supports HTTPS with username / PAT, or SSH)
        remote_url = subprocess.check_output(
            ["git", "-C", str(BASE_DIR), "remote", "get-url", "origin"]
        ).decode().strip()

        if remote_url.startswith("https://"):
            username = input("👤 GitHub username: ").strip()
            password = getpass("🔑 Personal access token / password: ")
            auth_url = remote_url.replace("https://", f"https://{username}:{password}@")
            subprocess.run(["git", "-C", str(BASE_DIR), "push", auth_url, "HEAD"], check=True)
        else:
            subprocess.run(["git", "-C", str(BASE_DIR), "push"], check=True)

        print("✅ git push completed")

    except subprocess.CalledProcessError as e:
        print("❌ Git operation failed:", e)


def git_pull() -> None:
    try:
        subprocess.run(["git", "-C", str(BASE_DIR), "pull"], check=True)
        print("✅ git pull completed")
    except subprocess.CalledProcessError as e:
        print("❌ git pull failed:", e)


def kill_flask() -> None:
    subprocess.run(["pkill", "-f", "flask"])
    print("✅ Flask processes terminated")


def kill_python() -> None:
    subprocess.run(["pkill", "-f", "python"])
    print("✅ All Python processes terminated")


def run_main() -> None:
    """Start main.py in the background (prefers the venv’s interpreter)."""
    venv_python = BASE_DIR / "venv" / "bin" / "python"
    main_py = BASE_DIR / "main.py"

    if venv_python.exists():
        subprocess.Popen([str(venv_python), str(main_py)])
    else:
        subprocess.Popen(["python3", str(main_py)])

    print("✅ main.py launched in background")


def show_menu() -> str:
    menu = """
===================== Attendance Manager =====================
 1) Lanch main.py
 2) git pull
 3) git add ➜ commit ➜ push (manual credentials)
 4) Kill all Flask processes
 5) Kill all Python processes
 6) Restart (3 ➜ 4)
 7) Exit
================================================================
Enter choice (1-7): """
    return input(menu).strip()


def main() -> None:
    while True:
        choice = show_menu()

        if choice == "1":
            run_main()
        elif choice == "2":
            git_pull()
        elif choice == "3":
            git_commit_push()
        elif choice == "4":
            kill_flask()
        elif choice == "5":
            kill_python()
        elif choice == "6":
            kill_flask()
            kill_python()
        elif choice == "7":
            print("Good-bye!")
            sys.exit(0)
        else:
            print("⚠️ Please enter a number from 1 to 7.")


if __name__ == "__main__":
    main()
