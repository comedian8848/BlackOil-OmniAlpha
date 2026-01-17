from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Literal
import json
import os
from pathlib import Path

router = APIRouter()

# --- Constants & Paths ---
# Save settings in the data directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SETTINGS_FILE = DATA_DIR / "settings.json"

# --- Models ---
class AISettings(BaseModel):
    provider: Literal["openai", "anthropic", "local", "custom", "gemini", "deepseek", "groq", "mistral"] = "local"
    api_key: Optional[str] = ""
    base_url: Optional[str] = ""
    model_name: str = "llama3-8b"
    temperature: float = 0.7
    permission_level: Literal["consultant", "coding", "copilot"] = "consultant"

class TradingSettings(BaseModel):
    initial_capital: float = 1000000.0
    commission_rate: float = 0.0003
    tax_rate: float = 0.001
    risk_free_rate: float = 0.02

class SystemSettings(BaseModel):
    theme: Literal["light", "dark", "system"] = "system"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    auto_update_data: bool = False

class AppSettings(BaseModel):
    ai: AISettings = Field(default_factory=AISettings)
    trading: TradingSettings = Field(default_factory=TradingSettings)
    system: SystemSettings = Field(default_factory=SystemSettings)

# --- Service Logic ---
def get_default_settings() -> AppSettings:
    return AppSettings()

def load_settings_from_file() -> AppSettings:
    if not SETTINGS_FILE.exists():
        return get_default_settings()
    
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return AppSettings(**data)
    except Exception as e:
        print(f"Error loading settings: {e}")
        return get_default_settings()

def save_settings_to_file(settings: AppSettings):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        f.write(settings.model_dump_json(indent=2))

# --- Endpoints ---

@router.get("/", response_model=AppSettings)
async def get_settings():
    """Get current application settings"""
    return load_settings_from_file()

@router.put("/", response_model=AppSettings)
async def update_settings(settings: AppSettings):
    """Update application settings"""
    try:
        save_settings_to_file(settings)
        return settings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset", response_model=AppSettings)
async def reset_settings():
    """Reset settings to default"""
    defaults = get_default_settings()
    save_settings_to_file(defaults)
    return defaults
