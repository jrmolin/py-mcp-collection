#!/usr/bin/env python3

import re
import sys
from pathlib import Path


def main():
    if len(sys.argv) != 2:
        print("Usage: python bump_versions.py <version>")
        sys.exit(1)

    new_version = sys.argv[1]

    # Find all pyproject.toml files
    for pyproject in Path().rglob("pyproject.toml"):
        # Read the file
        content = pyproject.read_text()

        # Replace any version number pattern
        content = re.sub(r'version\s*=\s*"\d+\.\d+\.\d+"', f'version = "{new_version}"', content)

        # Write back
        pyproject.write_text(content)
        print(f"Updated {pyproject}")


if __name__ == "__main__":
    main()
