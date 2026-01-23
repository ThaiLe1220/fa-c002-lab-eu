"""
Configuration for AI Agent.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / ".secret" / ".env"
load_dotenv(dotenv_path=env_path)

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0"))
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))

# Snowflake Configuration (uses existing RSA key auth)
SNOWFLAKE_SCHEMA = "ANALYTICS"

# Validate
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .secret/.env")
