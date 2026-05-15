from langchain_google_genai import GoogleGenerativeAIEmbeddings
import json
from dotenv import load_dotenv
from langchain_core.tools import tool
from typing import List
import numpy as np

load_dotenv()

embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2")

APPLY = 0.7

def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Pure numpy cosine similarity. Returns 0.0 - 1.0."""
    a = np.array(vec_a)
    b = np.array(vec_b)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def embed_profile():
        """Embeds the resume profile and saves the embedding in a json file
        
        Args: None
        
        Returns:Vector embedding of Resume file"""

        with open("profile.json", "r") as f:
            data = json.load(f)

        # print(data)
        # print(data["all_bullet_points_and_summary"])
        vector = embeddings.embed_query(data["all_bullet_points_and_summary_and_skills"])
        data["embedding"] = vector

        with open("profile.json", "w") as f:
            json.dump(data, f, indent=2)
        
        return data


def similarity_score(job: str):
    """Embeds a job posting and calculates the similarity score between profile embedding and job embedding
     
     Args: str of job posting
     
     Returns: True if jobs is relevant to resume and False if job is not relevant to resume"""
    job_embedding = embeddings.embed_query(job)
    with open("profile.json", "r") as f:
            data = json.load(f)
    resume_embedding = data["embedding"]
    
    
    return cosine_similarity(resume_embedding, job_embedding) >= APPLY

   
# EMBEDDING_TOOLS = [embed_profile, similarity_score]









     
     

    
    

