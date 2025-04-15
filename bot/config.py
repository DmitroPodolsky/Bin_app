import json
from pathlib import Path
from typing import Optional

from pydantic import BaseModel
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


project_dir = Path(__file__).parent.parent
locale_dir = project_dir / "locales"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)
    
    BOT_TOKEN: Optional[str]

    POSTGRESS_DATABASE: str
    POSTGRESS_USER: str
    POSTGRESS_PASSWORD: str
    POSTGRESS_HOST: str
    POSTGRESS_PORT: int
    
    RU_LANG_JSON_PATH: Path = locale_dir/"ru.json"


settings = Settings()  # type: ignore

class BaseLocale(BaseModel):
    """
    BaseLocale class for storing localized strings used in the bot.
    """
    choose_curency: str
    choose_subscription_type: str
    welcome_message: str
    menu: str
    no_accounts: str
    your_accounts: str
    create_account: str
    enter_account_name: str
    send_cookies: str
    send_user_agent: str
    file_too_big: str
    no_file: str
    send_proxy_url: str
    send_text_spam: str
    send_count_spam: str
    send_name: str
    bad_format: str
    send_category_link: str
    send_geolocation: str
    no_account_fullfilled: str
    radius_not_found: str
    send_time_filter: str
    send_rate_limit: str
    not_fullfilled: str
    account_not_valid: str
    account_deleted: str
    no_subscription: str
    send_radius: str
    subscription_paid: str
    
    
settings = Settings() 

   
def load_bot_strings(json_path: Path) -> BaseLocale:
    """
    Load bot strings from a JSON file.

    Parameters:
        json_path (Path): Path to the JSON file containing the bot strings.

    Returns:
        BaseLocale: An instance of BaseLocale populated with the data from the JSON file.
    """
    with open(json_path, encoding="utf-8") as file:
        json_data: dict = json.load(file)
        return BaseLocale.model_validate(json_data)


RU_LANG = load_bot_strings(settings.RU_LANG_JSON_PATH)