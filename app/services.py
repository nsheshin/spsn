from langchain_community.document_loaders import Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_chroma import Chroma
from fastapi import UploadFile, File
from uuid import uuid4
import os
import asyncio
from db import files_collection, questions_collection
from config import chat_model, embeddings, chat_prompt


UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)


async def embed_file(file: UploadFile = File(...)):
    file_id = str(uuid4())
    file_path = os.path.join(UPLOAD_DIR, file_id)
    
    # сохранение файла
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Загрузка документа
    loader = Docx2txtLoader(file_path)
    docs = loader.load()

    # Разбивка на чанки
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=250,
        separators=[
            "\n\n",
            "\n",
            # "\\n",
            ])
    chunks = splitter.split_documents(docs)

    # создаём отдельную директорию под векторы этого файла
    vector_dir = os.path.join("./chroma_stores", file_id)
    os.makedirs(vector_dir, exist_ok=True)

    # создаём векторное хранилище
    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=vector_dir
    )

    # сохраняем в монгу айди\имя файла (не нужно, но раз завели монгу)
    await files_collection.insert_one({
        "file_id": file_id,
        "filename": file.filename
    })
    
    return {"file_id": file_id}


async def upload_question(file_id: str, question: str):
    question_id = str(uuid4())

    # Сохраняем запись о вопросе
    await questions_collection.insert_one({
        "question_id": question_id,
        "status": "processing",
        "answer": None
    })

    # Отправляем фоновую таску
    asyncio.create_task(process_question(question_id, file_id, question))

    return {"question_id": question_id, "status": "processing"}


async def process_question(question_id: str, file_id: str, question: str):
    """Фоновая задача, выполняющая сам invoke и обновляющая монгу"""

    try:
        # подтягиваем эмбединги
        vector_dir = os.path.join("./chroma_stores", file_id)
        vectorstore = Chroma(
            embedding_function=embeddings,
            persist_directory=vector_dir
        )

        # настраиваем ретривер
        retriever = vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 20, "fetch_k": 40, "lambda_mult": 0.3}
        )

        # формируем запрос
        qa = RetrievalQA.from_chain_type(
            llm=chat_model,
            retriever=retriever,
            chain_type_kwargs={"prompt": chat_prompt}
        )

        # Вызов модели
        result = qa.invoke(question)

        # запись в монго
        await questions_collection.update_one(
            {"question_id": question_id},
            {"$set": {"status": "done", "answer": result}}
        )

    except Exception as e:
        await questions_collection.update_one(
            {"question_id": question_id},
            {"$set": {"status": "error", "answer": str(e)}}
        )

async def load_answer(question_id):
    return await questions_collection.find_one({"question_id": question_id}, {"_id": 0})
