./#!/bin/bash

# Find all directories containing pyproject.toml
for dir in $(find . -name "pyproject.toml" -exec dirname {} \;); do
    echo "Processing $dir..."
    cd "$dir"
    
    # Activate virtual environment if it exists
    if [ -d ".venv" ]; then
        source .venv/bin/activate
    else
        echo "No .venv found in $dir, skipping..."
        cd - > /dev/null
        continue
    fi
    
    # Run the commands
    echo "Running ruff format..."
    ruff format .
    
    echo "Running ruff check --fix..."
    ruff check --fix .
    
    echo "Running uv sync..."
    uv sync
    
    # Deactivate virtual environment
    deactivate
    
    # Go back to original directory
    cd - > /dev/null
    echo "----------------------------------------"
done 