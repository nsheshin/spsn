from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from dotenv import load_dotenv
import os
load_dotenv()


api_key = os.getenv("OPENAI_API_KEY")

# апи
chat_model = ChatOpenAI(
    api_key=api_key,
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
    model="qwen-plus",
    temperature=0.8
)

# эмбединг
embeddings = HuggingFaceEmbeddings(
    model_name="intfloat/multilingual-e5-base"
)

# промпт
system_prompt = SystemMessagePromptTemplate.from_template(
    """Дай точный фрагмент текста из документа, который отвечает на вопрос.
    Отвечай только дословно, без суммирования и обобщений.
    После ответа дай краткий контекст.
    Если ответа нет — напиши "Не найдено".
    """
)
human_prompt = HumanMessagePromptTemplate.from_template(
    "Контекст:\n{context}\n\nВопрос: {question}"
)
chat_prompt = ChatPromptTemplate.from_messages([system_prompt, human_prompt])
