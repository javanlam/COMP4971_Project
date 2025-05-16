from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from llama_index.core import StorageContext
from contextlib import asynccontextmanager

import utils.member_data as member_data
import utils.prompts as prompts
import utils.llm as llm
import utils.rag as rag


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        rag.storage_context = StorageContext.from_defaults(persist_dir="rag/storage")
    except:
        rag.persist_data()
        rag.storage_context = StorageContext.from_defaults(persist_dir="rag/storage")
    
    print("Starting app")
    yield
    print("Closing app")

app = FastAPI(lifespan=lifespan)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatContent(BaseModel):
    member: int
    prompt: str

class GenerationChat(BaseModel):
    prompt: str

class ReGenerationChat(BaseModel):
    prompt: str
    webpage: str

@app.get("/api/members")
async def get_members():
    return member_data.members

@app.post("/api/LLM_query")
async def get_LLM_response_query(chat_content: ChatContent):
    """
    For simple query on main page
    """
    rag_retrieved = rag.get_nodes(chat_content.prompt, storage=rag.storage_context)

    system_prompt = prompts.get_query_system_prompt(member=member_data.members_id[chat_content.member], rag_info=rag_retrieved)
    response = llm.get_LLM_output(
        system_prompt=system_prompt,
        user_prompt=chat_content.prompt
    )
    return response

@app.get("/api/to-compile-example")
async def get_page_to_compile():
    """
    Static HTML/JavaScript Code retrieval from existing file
    For testing purposes only
    """
    webpage_content = """"""
    try:
        f = open("../frontend/src/webpage.txt", "r")
        webpage_content = f.read()
    except:
        pass
    return webpage_content

@app.post("/api/webpage-generation")
async def get_LLM_webpage_generation(chat_content: GenerationChat):
    """
    Gets LLM-generated webpage code and returns to frontend for display
    """
    rag_retrieved = rag.get_nodes(chat_content.prompt, storage=rag.storage_context)

    system_prompt = prompts.get_content_generation_prompt(rag_info=rag_retrieved)
    generated_webpage = llm.get_LLM_output(
        system_prompt=system_prompt,
        user_prompt=chat_content.prompt
    )
    return generated_webpage

@app.post("/api/webpage-regeneration")
async def get_LLM_webpage_regeneration(chat_content: ReGenerationChat):
    """
    Re-generates webpage code according to further instructions and returns to frontend for display
    """
    rag_retrieved = rag.get_nodes(chat_content.prompt, storage=rag.storage_context)
    
    system_prompt = prompts.get_content_regeneration_prompt(past_webpage=chat_content.webpage, rag_info=rag_retrieved)
    user_prompt = f"""
        The user has the following request.
        ```
        {chat_content.prompt}
        ```
        Based on the webpage you were provided with, fulfill the user's request.
    """

    generated_webpage = llm.get_LLM_output(
        system_prompt=system_prompt,
        user_prompt=user_prompt
    )
    return generated_webpage