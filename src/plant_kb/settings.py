import os
from dataclasses import dataclass
from dotenv import load_dotenv
load_dotenv()

@dataclass(frozen=True)
class Settings:
    plant_id: str = os.getenv("PLANT_KB_PLANT_ID", "UPL")
    unit_id: str = os.getenv("PLANT_KB_UNIT_ID", "UNIT_05")
    chunk_chars: int = int(os.getenv("PLANT_KB_DEFAULT_CHUNK_CHARS", "1800"))
    overlap: int = int(os.getenv("PLANT_KB_CHUNK_OVERLAP", "200"))

settings = Settings()
