from fastapi import FastAPI, UploadFile, File
import uvicorn
from contextlib import asynccontextmanager
from Resume_parser.parser_mcp_server import ResumeParser
# from Embedder.embedding_mcp_server import Embedder


@asynccontextmanager
async def lifespan(app: FastAPI):

    yield




app = FastAPI(lifespan=lifespan)


@app.get("/")
async def health():
    return {"Status": "200 OK"}


@app.post("/upload-resume")
async def upload_resume(resume: UploadFile=File(...)):
    with open("Resume_parser/"+resume.filename, "wb") as f:
        f.write(await resume.read())

    print("Saved Resume to " + "Resume_parser/"+resume.filename)

    response = ResumeParser().parse("Resume_parser/"+resume.filename)



    return {"Result": response}





if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)



    


    

