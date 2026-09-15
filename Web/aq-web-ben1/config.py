import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration class"""

    # Flask Configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"

    # Database Configuration
    db_path = os.getenv("DATABASE_URL", "sqlite:///instance/project_hub.db")
    # Handle absolute vs relative paths
    if db_path.startswith("sqlite:///") and not db_path.startswith("sqlite:////"):
        # Relative path - ensure instance directory exists
        instance_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "instance"
        )
        os.makedirs(instance_dir, exist_ok=True)
    SQLALCHEMY_DATABASE_URI = db_path
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = DEBUG  # Log SQL queries in debug mode

    # Jira Configuration
    JIRA_URL = os.getenv("JIRA_URL")
    JIRA_EMAIL = os.getenv("JIRA_EMAIL")
    JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

    @staticmethod
    def validate():
        """Validate that all required configuration is present"""
        required_vars = ["JIRA_URL", "JIRA_EMAIL", "JIRA_API_TOKEN"]
        missing_vars = []

        for var in required_vars:
            env_value = os.getenv(var)
            if env_value is None or env_value == "":
                missing_vars.append(var)

        if len(missing_vars) > 0:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}\n"
                "Please create a .env file based on .env.example and fill in your Jira credentials."
            )

        return True
