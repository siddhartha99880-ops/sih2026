import os


os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://test:test@localhost:5432/land_intelligence")
os.environ.setdefault("SECRET_KEY", "test-only-secret")