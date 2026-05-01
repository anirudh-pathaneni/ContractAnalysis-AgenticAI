import sys
import os
from pathlib import Path
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List
from dotenv import load_dotenv

load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

class ClauseExtracted(BaseModel):
    heading: str = Field(description="The heading or title of the clause")
    raw_text: str = Field(description="The exact raw text of the clause")

class ContractExtraction(BaseModel):
    """Extraction of all clauses from the contract"""
    clauses: List[ClauseExtracted] = Field(description="List of all extracted clauses")

import langchain_google_genai.chat_models

original_bind_tools = langchain_google_genai.chat_models.ChatGoogleGenerativeAI.bind_tools
def patched_bind_tools(self, tools, **kwargs):
    if kwargs.get("tool_choice") == "any":
        kwargs["tool_choice"] = "ANY"
    return original_bind_tools(self, tools, **kwargs)
langchain_google_genai.chat_models.ChatGoogleGenerativeAI.bind_tools = patched_bind_tools

def test():
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0)
    structured_llm = llm.with_structured_output(ContractExtraction)
    
    prompt = PromptTemplate.from_template("Extract clauses from: {raw_text}")
    
    try:
        res = structured_llm.invoke(prompt.format(raw_text="Clause 1: Hello. Clause 2: World."))
        print(res)
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test()
