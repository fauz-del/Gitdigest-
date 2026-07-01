from pydantic import BaseModel

class ReportRequest(BaseModel):
    token: str
    repo: str
