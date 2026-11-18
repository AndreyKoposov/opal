from pydantic import BaseModel


class LoginRequest(BaseModel):
    id: str

class LoginResponse(BaseModel):
    success: bool
    redirect_url: str
    message: str

class ProcessRequest(BaseModel):
    id: int
    name: str
    user: int

class ProcessResponse(BaseModel):
    processes: list

class ProcessIDResponse(BaseModel):
    pid: int

class MessageRequest(BaseModel):
    content: str
    pid: int
    mode: str
    sender: str

class MessageResponse(BaseModel):
    msgs: list

class PDFResponse(BaseModel):
    files: list

class PDFDelete(BaseModel):
    name: str
