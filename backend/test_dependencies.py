"""
Simple script to test if all dependencies can be imported without errors.
"""
import importlib
import sys

# List of packages to test
packages = [
    "fastapi",
    "uvicorn",
    "sqlalchemy",
    "psycopg2",
    "alembic",
    "pydantic",
    "jose",
    "passlib",
    "multipart",
    "dotenv",
    "httpx",
    "pytest",
    "pytest_asyncio",
    "aiohttp",
    "PIL",  # for pillow
    "pyotp",
    "qrcode",
    "emails",
    "jinja2",
    "pydantic_settings"
]

# Try to import each package
failed_imports = []
for package in packages:
    try:
        importlib.import_module(package)
        print(f"✓ Successfully imported {package}")
    except ImportError as e:
        failed_imports.append((package, str(e)))
        print(f"✗ Failed to import {package}: {e}")

# Show summary
print("\n--- SUMMARY ---")
if failed_imports:
    print(f"Failed to import {len(failed_imports)} packages:")
    for package, error in failed_imports:
        print(f"  - {package}: {error}")
    sys.exit(1)
else:
    print("All packages imported successfully!")
    sys.exit(0)
