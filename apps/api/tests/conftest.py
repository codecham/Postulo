import os

# Fake database settings so the app can be imported in tests without a real .env.
# setdefault keeps any value already defined in the environment.
os.environ.setdefault("POSTGRES_USER", "test")
os.environ.setdefault("POSTGRES_PASSWORD", "test")
os.environ.setdefault("POSTGRES_DB", "test")
