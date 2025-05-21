import argparse
import os
import re
import shutil
from pathlib import Path


def kebab_to_snake(name):
    return name.replace("-", "_")


def kebab_to_title(name):
    return " ".join(word.capitalize() for word in name.split("-"))


def replace_in_file(file_path, replacements):
    with Path(file_path).open(encoding="utf-8") as f:
        content = f.read()
    for old, new in replacements.items():
        content = re.sub(old, new, content)
    with Path(file_path).open("w", encoding="utf-8") as f:
        f.write(content)


def copy_and_replace(template_dir, dest_dir, server_name):
    snake_name = kebab_to_snake(server_name)
    title_name = kebab_to_title(server_name)
    # Copy the template directory
    shutil.copytree(template_dir, dest_dir)

    # Rename src/template to src/{snake_name}
    src_dir = Path(dest_dir) / "src" / "template"
    new_src_dir = Path(dest_dir) / "src" / snake_name
    if src_dir.exists():
        src_dir.rename(new_src_dir)

    # Walk through all files and replace occurrences
    for root, _, files in os.walk(dest_dir):
        for file in files:
            file_path = Path(root) / file
            # Only process text files
            if file_path.suffix in {".py", ".md", ".toml", ".txt", ".json"}:
                replace_in_file(
                    file_path,
                    {
                        r"\btemplate\b": snake_name,  # import paths, package name
                        r"Template": title_name,  # display name
                        r"template": server_name,  # CLI name, lower-case
                        r"Local Template": title_name,  # display string in code
                    },
                )
            # Rename test imports if needed
            if file == "test_main.py":
                replace_in_file(file_path, {"from template.main import cli": f"from {snake_name}.main import cli"})

    # Update pyproject.toml script entry
    pyproject_path = Path(dest_dir) / "pyproject.toml"
    if pyproject_path.exists():
        replace_in_file(
            pyproject_path,
            {
                r'name = "template"': f'name = "{server_name}"',
                r'"template"': f'"{snake_name}"',
                r"template.main:run_mcp": f"{snake_name}.main:run_mcp",
                r"template = ": f"{server_name} = ",
            },
        )

    # Update README.md usage examples
    readme_path = Path(dest_dir) / "README.md"
    if readme_path.exists():
        replace_in_file(
            readme_path,
            {
                r"template": server_name,
                r"Template": title_name,
            },
        )


def main():
    parser = argparse.ArgumentParser(description="Create a new MCP server from the template.")
    parser.add_argument("--name", required=True, help="The new server name (kebab-case, e.g., fetch-mcp)")
    parser.add_argument("--template", default="./template", help="Path to the template directory")
    parser.add_argument("--output", default=None, help="Output directory (defaults to --name)")
    args = parser.parse_args()

    server_name = args.name
    template_dir = args.template
    dest_dir = args.output or server_name

    if Path(dest_dir).exists():
        print(f"Error: Destination directory '{dest_dir}' already exists.")
        return

    copy_and_replace(template_dir, dest_dir, server_name)
    print(f"Created new MCP server at '{dest_dir}'!")


if __name__ == "__main__":
    main()
