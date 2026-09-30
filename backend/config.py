from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    PROJECT_NAME: str = "BhuVistaar — 3D Cadastral Intelligence & Validation Platform (Prototype)"
    API_V1_PREFIX: str = "/api/v1"
    CANONICAL_STORAGE_SRID: int = Field(default=32643, description="Canonical internal projected SRID (UTM 43N)")
    CANONICAL_STORAGE_CRS: str = Field(default="EPSG:32643", description="Canonical internal projected CRS")
    
    # Database Settings
    DATABASE_URL: str = Field(
        default="postgresql+psycopg://postgres:postgrespassword@127.0.0.1:5432/bhuvistaar_cadastre",
        description="Authoritative PostGIS connection string"
    )
    
    # Numerical Tolerances
    ADJACENCY_TOLERANCE_M: float = Field(default=0.001, description="Vertical adjacency tolerance in metres (1mm)")
    OVERLAP_THRESHOLD_M: float = Field(default=0.001, description="Vertical overlap detection threshold in metres (1mm)")
    PLANAR_CONTAINMENT_TOLERANCE_M: float = Field(default=0.001, description="Planar boundary containment tolerance in metres")
    COORDINATE_PRECISION_DECIMALS: int = Field(default=3, description="Coordinate rounding precision (1mm)")
    
    # Authorization mode banner
    AUTHORIZATION_MODE: str = "SIMULATED_PROTOTYPE"

    # AI Intelligence Configuration (Slice 3)
    AI_ASSISTANCE_ENABLED: bool = Field(default=True, description="Feature flag for AI assistance and candidate generation")
    AI_CONFIDENCE_THRESHOLD_HIGH: float = Field(default=0.85, description="High confidence threshold policy")
    AI_CONFIDENCE_THRESHOLD_MEDIUM: float = Field(default=0.60, description="Medium confidence threshold policy")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
