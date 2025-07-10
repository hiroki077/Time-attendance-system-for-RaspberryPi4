#!/usr/bin/env python3
import subprocess
import sys
import os
from pathlib import Path
from getpass import getpass

BASE_DIR = Path(__file__).resolve().parent

def git_commit_push() -> None:
    """Stage everything, commit (if needed), then push."""
    # 1) git add
    try:
        subprocess.run(
            ["git", "-C", str(BASE_DIR), "add", "."],
            check=True
        )
        print("✅ git add . completed")
    except subprocess.CalledProcessError as e:
        print("❌ git add failed:", e)
        return

    # 2) git commit（変更なしならスキップ）
    commit = subprocess.run(
        ["git", "-C", str(BASE_DIR), "commit", "-m", input("📝 Enter commit message: ").strip()],
        capture_output=True,
        text=True
    )
    if commit.returncode != 0:
        stderr = commit.stderr.lower()
        if "nothing to commit" in stderr:
            print("⚠️ No changes to commit, skipping commit.")
        else:
            print("❌ git commit failed:")
            print(commit.stderr.strip())
            return
    else:
        print("✅ git commit completed")

    # 3) git push
    try:
        remote_url = subprocess.check_output(
            ["git", "-C", str(BASE_DIR), "remote", "get-url", "origin"]
        ).decode().strip()
        if remote_url.startswith("https://"):
            username = input("👤 GitHub username: ").strip()
            password = getpass("🔑 Personal access token / password: ")
            auth_url = remote_url.replace("https://", f"https://{username}:{password}@")
            subprocess.run(
                ["git", "-C", str(BASE_DIR), "push", auth_url, "HEAD"],
                check=True
            )
        else:
            subprocess.run(
                ["git", "-C", str(BASE_DIR), "push"],
                check=True
            )
        print("✅ git push completed")
    except subprocess.CalledProcessError as e:
        print("❌ git push failed:", e)

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

def run_main():
    """Run main.py using virtualenv if it exists"""
    venv_python = BASE_DIR / "venv" / "bin" / "python"
    main_py = BASE_DIR / "main.py"

    if not main_py.exists():
        print("❌ main.py not found at", main_py)
        return

    print(f"🔍 BASE_DIR = {BASE_DIR}")
    print(f"🔍 venv_python exists: {venv_python.exists()} ({venv_python})")

    try:
        if venv_python.exists():
            print("🚀 Launching with virtualenv Python:", venv_python)
            subprocess.run(
                [str(venv_python), str(main_py)],
                cwd=str(BASE_DIR),
                check=True
            )
        else:
            print("⚠️ venv not found. Launching with system Python.")
            subprocess.run(
                ["python3", str(main_py)],
                cwd=str(BASE_DIR),
                check=True
            )
    except subprocess.CalledProcessError as e:
        print("❌ Failed to run main.py:", e)
    except KeyboardInterrupt:
        print("\n🔴 main.py execution interrupted by user (Ctrl+C)")

def kill_main():
    subprocess.run(["pkill", "-f", "main.py"])
    print("✅ main.py stopped")

def show_menu() -> str:
    menu = """
===================== Attendance Manager =====================
 1) Launch main.py
 2) git add ➜ commit ➜ push (manual credentials)
 3) Kill all Flask processes
 4) Kill all Python processes
 5) Restart (kill Flask & Python)
 6) Stop main.py process
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
            git_commit_push()
        elif choice == "3":
            kill_flask()
        elif choice == "4":
            kill_python()
        elif choice == "5":
            kill_flask()
            kill_python()
        elif choice == "6":
            kill_main()
        elif choice == "7":
            print("Good-bye!")
            sys.exit(0)
        else:
            print("⚠️ Please enter a number from 1 to 7.")

if __name__ == "__main__":
    main()
