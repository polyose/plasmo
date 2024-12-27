from pathlib import Path

from pydantic import BaseModel

class NixPathInfo(BaseModel):
    deriver: Path
    narHash: str
    narSize: int
    path: Path
    references: list[Path]
    registrationTime: int
    signatures: list[str]
    valid: bool

    model_config = {
        "arbitrary_types_allowed": True,
        "json_encoders": {
            Path: str
        }
    }
