from langchain_google_genai import GoogleGenerativeAIEmbeddings
import json
from dotenv import load_dotenv
from langchain_core.tools import tool
from typing import List
import numpy as np

load_dotenv()

embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview")

APPLY = 0.7

def cosine_similarity(vec_a: List[float], vec_b: List[List[float]]) -> List[float]:
    """Pure numpy cosine similarity. Returns 0.0 - 1.0."""
    scores = []
    a = np.array(vec_a)
    for b in vec_b:
        b = np.array(b)
        denom = np.linalg.norm(a) * np.linalg.norm(b)
        if denom == 0:
            scores.append(0.0)
        else:
            scores.append(float(np.dot(a, b) / denom))
    
    return scores


def embed_profile():
        """Embeds the resume profile and saves the embedding in a json file
        
        Args: None
        
        Returns:Vector embedding of Resume file"""

        with open("profile.json", "r") as f:
            data = json.load(f)

        # print(data)
        # print(data["all_bullet_points_and_summary"])
        vector = embeddings.embed_query(data["all_bullet_points_and_summary_and_skills"], output_dimensionality=1536)
        data["embedding"] = vector

        with open("profile.json", "w") as f:
            json.dump(data, f, indent=2)
        
        return vector


# def index_profile():
#     with open("profile.json", "r") as f:
#         data = json.load(f)

    
     


def embed_jobs(job: list[str]):
    """Embeds a job posting and calculates the similarity score between profile embedding and job embedding
     
     Args: str of job posting
     
     Returns: True if jobs is relevant to resume and False if job is not relevant to resume"""
    # job_embedding = embeddings.embed_documents(job)
    # with open("profile.json", "r") as f:
    #         data = json.load(f)
    # resume_embedding = data["embedding"]
    return embeddings.embed_documents(job, output_dimensionality=1536)


    
    
    # return cosine_similarity(resume_embedding, job_embedding)

   
# EMBEDDING_TOOLS = [embed_profile, similarity_score]









     
     

    
    

