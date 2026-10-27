from pydantic_settings import BaseSettings

class Settings(BaseSettings):
        google_api_key: str
        gemini_model: str
        mcp_url: str
        mcp_token: str | None = None    
        vyzno_cookie: str
        vyzno_csrf_token: str
        vyzno_mailbox_id: str

        model_config = {"env_file": ".env"}



