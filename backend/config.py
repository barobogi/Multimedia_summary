import json
import os
from pathlib import Path


def load_settings() -> dict:
    env_path = Path(__file__).parent.parent / "config" / "settings.json"
    with open(env_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 환경변수로 오버라이드 (Railway 배포 시 사용)
    return {
        "anthropic_api_key": os.getenv("ANTHROPIC_API_KEY", data.get("anthropic_api_key", "")),
        "gmail": {
            "sender_email": os.getenv("GMAIL_SENDER", data["gmail"]["sender_email"]),
            "app_password": os.getenv("GMAIL_APP_PASSWORD", data["gmail"]["app_password"]),
            "recipient_email": os.getenv("GMAIL_RECIPIENT", data["gmail"]["recipient_email"]),
        },
        "github": {
            "token": os.getenv("GITHUB_TOKEN", data["github"]["token"]),
            "diary_repo_owner": data["github"]["diary_repo_owner"],
            "diary_repo_name": data["github"]["diary_repo_name"],
            "obsidian_repo_owner": data["github"]["obsidian_repo_owner"],
            "obsidian_repo_name": data["github"]["obsidian_repo_name"],
            "obsidian_folder": data["github"]["obsidian_folder"],
        },
        "server": data.get("server", {}),
        "secret_key": os.getenv("SECRET_KEY", data["server"].get("secret_key", "")),
    }


SETTINGS = load_settings()
