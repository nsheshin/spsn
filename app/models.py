from pydantic import BaseModel
from typing import Optional


class FileUploadResponse(BaseModel):
    file_id: str


class QuestionResponse(BaseModel):
    question_id: str
    status: str


class AnswerContent(BaseModel):
    query: str
    result: str


class AnswerResponse(BaseModel):
    question_id: str
    status: str
    answer: Optional[AnswerContent] = None
