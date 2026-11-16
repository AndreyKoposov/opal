from pydantic import BaseModel


class LoginRequest(BaseModel):
    id: str

class LoginResponse(BaseModel):
    success: bool
    redirect_url: str
    message: str
