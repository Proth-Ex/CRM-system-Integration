import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
load_dotenv()


class Settings:
    PROJECT_NAME: str = "WooCommerce CRM Integration Engine"
    API_V1_STR: str = "/api"
    
    # WooCommerce Configuration
    WOOCOMMERCE_BASE_URL: str = os.getenv("WOOCOMMERCE_BASE_URL", "http://127.0.0.1:8000/wp-json/wc/v3")
    WOOCOMMERCE_CONSUMER_KEY: str = os.getenv("WOOCOMMERCE_CONSUMER_KEY", "ck_demo_kilowott_hackathon")
    WOOCOMMERCE_CONSUMER_SECRET: str = os.getenv("WOOCOMMERCE_CONSUMER_SECRET", "cs_demo_kilowott_hackathon")
    USE_SANDBOX: bool = os.getenv("USE_SANDBOX", "true").lower() in ("true", "1", "yes")

    # Workflow auto-trigger toggle
    AUTO_WORKFLOWS_ENABLED: bool = True

    # Live Google Gemini Configuration (read safely from environment)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")


settings = Settings()

