from pydantic import BaseModel
from typing import Optional

class UserUpdate(BaseModel):
    name: Optional[str] = None
    picture: Optional[str] = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str