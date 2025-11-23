#!/usr/bin/env python3
import shutil
import subprocess
import sys
import argparse
from typing import List


class CargoToolError(Exception):
    """Custom exception for cargo tool failures."""
    pass


def run_command(cmd: List[str]) -> None:
    """
    Run a command with full error handling.
    If the command fails or is missing, raise CargoToolError.
    """
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,  # 自前でコードチェックする
        )
    except FileNotFoundError:
        raise CargoToolError(f"Command not found: {cmd[0]}")
    except OSError as e:
        raise CargoToolError(f"OS error while executing {cmd}: {e}")

    if result.returncode != 0:
        raise CargoToolError(
            f"Command failed: {' '.join(cmd)}\n"
            f"Exit code: {result.returncode}\n\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )


def ensure_rust_env() -> None:
    """
    Ensure cargo exists.
    Raise CargoToolError if not found.
    """
    if shutil.which("cargo") is None:
        raise CargoToolError(
            "Cargo not found. Rust environment is not configured properly."
        )

def cargo_check() -> None:
    print("🔍 Running cargo check...")
    run_command(["cargo", "check", "--quiet"])
    print("✅ Cargo check passed")


def cargo_clippy() -> None:
    print("🔧 Running cargo clippy...")
    run_command(["cargo", "clippy", "--quiet", "--", "-D", "warnings"])
    print("✅ Clippy checks passed")


def cargo_fmt() -> None:
    print("🎨 Checking Rust formatting...")
    try:
        run_command(["cargo", "fmt", "--check", "--quiet"])
        print("✅ Code formatting is correct")
    except CargoToolError as e:
        print("❌ Code formatting issues found")
        print("💡 Run 'cargo fmt' to fix formatting")
        raise


def main():
    parser = argparse.ArgumentParser(description="Unified cargo check tools")
    parser.add_argument("--check", action="store_true", help="Run cargo check only")
    parser.add_argument("--clippy", action="store_true", help="Run cargo clippy only")
    parser.add_argument("--fmt", action="store_true", help="Run cargo fmt --check only")

    args = parser.parse_args()

    try:
        ensure_rust_env()

        # 個別実行
        if args.check:
            cargo_check()
            return
        if args.clippy:
            cargo_clippy()
            return
        if args.fmt:
            cargo_fmt()
            return

        # 全部実行
        cargo_check()
        cargo_clippy()
        cargo_fmt()

    except CargoToolError as e:
        print(f"\n❌ ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        # 想定外の例外をキャッチしてログ出力
        print(f"\n🔥 Unexpected error occurred:\n{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
