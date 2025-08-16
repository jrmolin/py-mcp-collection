from pathlib import Path

from aiofiles import open as aopen


# Helper function to create test files
async def create_test_file(path: Path, content: str) -> None:
    async with aopen(path, "w") as f:
        _ = await f.write(content)


# Helper function to create test directory structure
async def create_test_structure(root: Path) -> None:
    # Create some text files
    await create_test_file(root / "test_with_hello_world.txt", "Hello, World!")
    await create_test_file(root / "code_with_hello_world.py", "def hello():\n    print('Hello, World!')")
    await create_test_file(root / "data.json", '{"key": "value"}')
    await create_test_file(root / "should_be_ignored.env", "secret_key=1234567890")
    await create_test_file(root / "CaSeSenSiTiVe.txt", "a Case Sensitive File")

    # Create a subdirectory with files
    subdir = root / "subdir"
    subdir.mkdir()
    await create_test_file(subdir / "nested.txt", "Nested content")
    await create_test_file(subdir / "script_with_hello.sh", "#!/bin/bash\necho 'Hello'")
    await create_test_file(subdir / "should_be_ignored.env", "secret_key=1234567890")

    # Create a hidden file
    await create_test_file(root / ".hidden", "Hidden content")

    # create a gitignore file
    gitdir = root / ".git"
    gitdir.mkdir()
    await create_test_file(root / ".gitignore", "*.env\n**/*.env")
