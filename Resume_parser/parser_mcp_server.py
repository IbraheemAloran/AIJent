from pydantic import BaseModel
from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from langchain.messages import HumanMessage
from pprint import pprint
from typing import List, Dict
import json
from google import genai
from pydantic import BaseModel, Field
from typing import List, Optional
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
import fitz

load_dotenv()

class Experience(BaseModel):
    Title: str
    Location: str
    Start_Date: str
    End_Date: str
    Description: str

class Education(BaseModel):
    Degree: str
    Major: str
    Instituion: str
    Location: str
    Start_Date: str
    End_Date: str
    
class Projects(BaseModel):
    Title: str
    Tools: str
    Description: str

class Profile(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    email: str
    linkedin: str
    github: str
    summary: str
    skills: List[str]
    years_of_exp: int
    experience: List[Experience]
    projects: List[Projects]
    education: List[Education]
    all_bullet_points_and_summary_and_skills: str

class ResumeParser:
    def __init__(self):
        self.model = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")
        self.structured_model = self.model.with_structured_output(
            schema=Profile.model_json_schema(), method="json_schema"
        )

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a resume parser agent that takes in a resume and extracts info from it. Do not summarize any info from the resume. Extract the text exactly as it is and return structured feedback."),
            ("human", "{input}")
        ])

        self.chain = self.prompt | self.structured_model

    def parse(self, file_path):
        doc = fitz.open(file_path)
        text = doc[0].get_text()
        result = self.chain.invoke({"input": text})

        with open("profile.json", "w") as f:
            json.dump(result, f, indent=2)

        return result

