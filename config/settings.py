import os
import streamlit as st
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Helper function to get settings safely with Streamlit secrets fallback
def get_settings():
    try:
        if "DATABASE_URL" in st.secrets:
            class DummySettings:
                DATABASE_URL = st.secrets["DATABASE_URL"]
                @property
                def DATABASE_URI(self):
                    return self.DATABASE_URL
            return DummySettings()
    except Exception:
        pass
    
    return Settings()

settings = get_settings()