#!/usr/bin/env python3
"""
Script to create a new Alembic migration.
Usage: python scripts/create_migration.py "Add new feature"
"""
import sys
import subprocess
from pathlib import Path

def create_migration(message: str) -> None:
    """Create a new Alembic migration with the given message."""
    if not message:
        print("Error: Migration message is required")
        sys.exit(1)
    
    # Change to the project root directory
    project_root = Path(__file__).parent.parent
    
    # Run alembic revision command
    try:
        result = subprocess.run(
            ["alembic", "revision", "--autogenerate", "-m", message],
            cwd=project_root,
            check=True,
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        
        if result.stderr:
            print(f"Warnings:\n{result.stderr}")
            
        print("Migration created successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error creating migration: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/create_migration.py \"Migration message\"")
        sys.exit(1)
    
    create_migration(sys.argv[1])