import subprocess
import sys


def main():
    print(">>> black", flush=True)
    black = subprocess.run(["poetry", "run", "black", "--check", "."])

    print(">>> ruff", flush=True)
    ruff = subprocess.run(["poetry", "run", "ruff", "check", "."])

    sys.exit(black.returncode or ruff.returncode)


if __name__ == "__main__":
    main()
