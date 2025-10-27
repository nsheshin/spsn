from fastapi import FastAPI, UploadFile, File, HTTPException
from services import load_answer, upload_question, embed_file
from models import FileUploadResponse, QuestionResponse, AnswerResponse

app = FastAPI()


@app.post("/upload_file", response_model=FileUploadResponse, summary="Загрузить файл для создания эмбеддинга",)
async def upload_file(file: UploadFile = File(...)):
    """Загрузить файл для создания эмбеддинга, возвращает file_id"""

    try:
        return await embed_file(file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {str(e)}")


@app.post("/ask_question", response_model=QuestionResponse, summary="Задать вопрос по файлу")
async def ask_question(file_id: str, question: str):
    """Задать вопрос по file_id, возвращает question_id"""

    try:
        return await upload_question(file_id, question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {str(e)}")


@app.get("/get_answer", response_model=AnswerResponse, summary="Получить ответ на вопрос")
async def get_answer(question_id: str):
    """Получить статус и/или готовый ответ по question_id"""

    try:
        return await load_answer(question_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {str(e)}")
