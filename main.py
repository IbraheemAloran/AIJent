from fastapi import FastAPI, UploadFile, File
import uvicorn
from contextlib import asynccontextmanager
from parser_mcp_server import ResumeParser
import embedding_mcp_server as emb
from database import engine, SessionLocal
from models import Base, Job, Profile
from job_search_agent import job_scrape_mcp
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import select, func
import json


class JobResponse(BaseModel):
    id: int
    job_id: str
    title: str
    company: str | None = None
    workplace_type: list[str]
    apply_url: str
    location: str
    posted: datetime
    full_description_plain: str
    status: str
    embedding: list[float]


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    yield




app = FastAPI(lifespan=lifespan)


@app.get("/")
async def health():
    return {"message": "PostgreSQL connected"}


@app.post("/upload")
async def upload_resume(resume: UploadFile=File(...)):
    with open(resume.filename, "wb") as f:
        f.write(await resume.read())

    print("Saved Resume to " +resume.filename)

    response = ResumeParser().parse(resume.filename)

    db = SessionLocal()
    profile = Profile(
        profile=response,
        embedding=emb.embed_profile()
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    db.close()

    return {"Result": response}

@app.get("/profile")
async def get_profile():
    db = SessionLocal()
    profiles = db.query(
        Profile.profile["first_name"].astext,
        Profile.profile["file_path"].astext,
        Profile.embedding,
    ).all()

    print(profiles[0][2])

    return {"name": profiles[0][0],
            "path": profiles[0][1],
            "embedding": list(map(float, profiles[0][2]))}




@app.post("/search-jobs")
def search_jobs():
    jobs = job_scrape_mcp.scrape_jobs(10)
    db = SessionLocal()
    db.bulk_insert_mappings(Job, jobs)
    db.commit()
    db.close()
    return jobs[0]


@app.post("/relevant")
def relevant_jobs(k: int = 5):
    db = SessionLocal()
    with open("profile.json", "r") as f:
            data = json.load(f)

    ts_query = func.websearch_to_tsquery("english", data["all_bullet_points_and_summary_and_skills"])
    query_embedding = data["embedding"]

    keyword_score = func.coalesce(
            func.ts_rank_cd(
                Job.search_vector,
                ts_query
            ),
            0
        )

    vector_score = (
            1 - Job.embedding.cosine_distance(query_embedding)
    )

    hybrid_score = (
            keyword_score * 0.4
            +
            vector_score * 0.6
    )

    stmt = (
            select(
                Job,
                keyword_score.label("keyword_score"),
                vector_score.label("vector_score"),
                hybrid_score.label("hybrid_score")
            )
            .order_by(hybrid_score.desc())
            .limit(k)
    )

    results = db.execute(stmt).all()
    print(results)
    db.close()
    job, keyword_score, vector_score, hybrid_score = results[0]
    return {
        "job_id": job.job_id,
        "title": job.title,
        "company": job.company,
        "keyword_score": keyword_score,
        "vector_score": vector_score,  
        "hybrid_score": hybrid_score,
    }

    # return [
    #         {
    #             "job": row.Job,
    #             "keyword_score": row.keyword_score,
    #             "vector_score": row.vector_score,
    #             "hybrid_score": row.hybrid_score,
    #         }
    #         for row in results
    #     ]


@app.get("/jobs", response_model=list[JobResponse])
def get_jobs():
    db = SessionLocal()
    jobs = db.query(Job).all()

    db.close()
    print(jobs)

    return jobs


@app.get("/test")
def get_jobs():
    db = SessionLocal()
    job = db.query(Job).first()

    print(job.title)
    print(job.search_vector)

    count = db.query(func.count(Job.id))\
          .filter(Job.search_vector != None)\
          .scalar()

    print(count)




if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)



    


    

