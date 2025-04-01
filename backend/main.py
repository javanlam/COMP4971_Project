from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import utils.member_data as member_data
import utils.prompts as prompts
import utils.llm as llm

app = FastAPI()

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

@app.get("/api/members")
async def get_members():
    return member_data.members

@app.post("/api/LLM_query")
async def get_LLM_response_query(chat_content: ChatContent):
    """
    For simple query on main page
    """
    system_prompt = prompts.get_query_system_prompt(member=member_data.members_id[chat_content.member])
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
    system_prompt = prompts.get_content_generation_prompt()
    generated_webpage = llm.get_LLM_output(
        system_prompt=system_prompt,
        user_prompt=chat_content.prompt
    )
    return generated_webpage