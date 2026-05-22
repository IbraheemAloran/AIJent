from fastapi import FastAPI, UploadFile, File
import uvicorn
from contextlib import asynccontextmanager
from Resume_parser.parser_mcp_server import ResumeParser
# from Embedder.embedding_mcp_server import Embedder
from database import engine, SessionLocal
from models import Base, Job




@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    
    yield




app = FastAPI(lifespan=lifespan)


@app.get("/")
async def health():
    return {"message": "PostgreSQL connected"}


@app.post("/upload-resume")
async def upload_resume(resume: UploadFile=File(...)):
    with open("Resume_parser/"+resume.filename, "wb") as f:
        f.write(await resume.read())

    print("Saved Resume to " + "Resume_parser/"+resume.filename)

    response = ResumeParser().parse("Resume_parser/"+resume.filename)



    return {"Result": response}


@app.post("/create-jobs")
async def create_job():
    db = SessionLocal()
    job = Job(
        title="ML Engineer",
        company="OpenAI"
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return {
        "id": job.id,
        "title": job.title
    }


@app.get("/jobs")
def get_jobs():
    db = SessionLocal()
    jobs = db.query(Job).all()

    db.close()

    return jobs




if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)



    


    

