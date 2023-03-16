import subprocess
import sys


def main():
    print(">>> black", flush=True)
    black = subprocess.run(["poetry", "run", "black", "."])

    print(">>> ruff", flush=True)
    ruff = subprocess.run(["poetry", "run", "ruff", "."])

    sys.exit(black.returncode or ruff.returncode)


if __name__ == "__main__":
    main()
