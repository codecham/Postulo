from typing import Literal

from pydantic import BaseModel


class Token(BaseModel):
    """Returned after a successful login."""

    access_token: str
    token_type: Literal["bearer"] = "bearer"
