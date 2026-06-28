import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import AstraDB
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate

from app.config import GOOGLE_API_KEY, ASTRA_DB_APPLICATION_TOKEN, ASTRA_DB_API_ENDPOINT
from app.services.memory import memory
from app.services.llm_provider import create_llm
from app.logger import get_logger

logger = get_logger("stockbot.rag")

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

PROMPT_TEMPLATE = """
Answer the question as detailed as possible from the provided context, make sure to provide all the details. If the answer is not available in the provided context just try to answer without context but keeping chat_history in mind. Try add two Logical follow up questions in next line that can be asked by the user at the end of generated answer with the heading "Want to know more?, ask these follow up questions :"

Current conversation:
{chat_history}
Context:
{context}
Question:
{human_input}

Answer:
"""

_embeddings = None
_vstore = None


def get_embeddings():
    global _embeddings
    if _embeddings is None:
        logger.info("Loading embedding model: hkunlp/instructor-large")
        _embeddings = HuggingFaceEmbeddings(model_name="hkunlp/instructor-large")
        logger.info("Embedding model loaded")
    return _embeddings


def get_vector_store():
    global _vstore
    if _vstore is None:
        logger.info("Connecting to AstraDB vector store")
        _vstore = AstraDB(
            embedding=get_embeddings(),
            collection_name="pdfdata",
            token=ASTRA_DB_APPLICATION_TOKEN,
            api_endpoint=ASTRA_DB_API_ENDPOINT,
        )
    return _vstore


def get_conversational_chain(llm=None):
    if llm is None:
        llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.8)
    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["chat_history", "context", "human_input"],
    )
    return load_qa_chain(llm, chain_type="stuff", memory=memory, prompt=prompt)


def get_answer(user_question: str, provider: str = None, model_name: str = None, api_key: str = None) -> str:
    logger.info(f"Searching vector store for: \"{user_question[:60]}\"")
    vstore = get_vector_store()
    relevant_docs = vstore.similarity_search(user_question, k=2)
    logger.info(f"Found {len(relevant_docs)} relevant documents")

    llm = None
    if provider and model_name and api_key:
        logger.info(f"Using custom LLM: {provider}/{model_name}")
        llm = create_llm(provider, model_name, api_key)
    else:
        logger.info("Using default LLM (Gemini Pro)")

    chain = get_conversational_chain(llm=llm)
    response = chain(
        {"input_documents": relevant_docs, "human_input": user_question},
        return_only_outputs=True,
    )
    logger.info("Answer generated successfully")
    return response["output_text"]
