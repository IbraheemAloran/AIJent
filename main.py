from fastapi import FastAPI, UploadFile, File
import uvicorn
from contextlib import asynccontextmanager
from parser_mcp_server import ResumeParser
import embedding_mcp_server as emb
from database import engine, SessionLocal
from models import Base, Job, Profile




@asynccontextmanager
async def lifespan(app: FastAPI):
    # Base.metadata.drop_all(bind=engine)
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



@app.post("/create-jobs")
async def create_job():
    db = SessionLocal()
    job = Job(
        # title="ML Engineer",
        # company="OpenAI"
        job_id="idbrassring___25037_5010___848949",
        title="AI Machine Learning Engineer Staff",
        company="Lockheed Martin",
        workplace_type=["Remote"],
        apply_url="https://sjobs.brassring.com/TGnewUI/Search/home/HomeWithPreLoad?partnerid=25037&siteid=5010&PageType=JobDetails&jobid=848949",
        location="Aguadilla or Bethesda or Denver or Grand Prairie or Orlando or Shelton",
        posted="2026-03-17T00:00:00.000Z",
        full_description_plain="Security Clearance\nNone\nShift\nFirst \nDirect/Indirect\nIndirect \nBusiness Area\nEnterprise Operations \nDepartment\n50168:Data & AI Enablement \nRelocation/Housing Stipend Available\nNo\nJob Code/Title\nE9854:A/AI Mch Learn Engnr Stf \nJob Class\nArtificial Intelligence  \nJob Category\nExperienced Professional\nProgram\n1LMX AI Acceleration\nReq Type\nFull-Time\nJob Description\nJoin Lockheed Martin’s digital transformation journey as we accelerate the OneLM Mission-Driven Transformation through our 1LMX program. This strategic priority is reshaping our operations and business processes to better serve our customers in terms of cost, quality, and capabilities, while delivering the speed, agility, and insights necessary to stay ahead of rapidly-evolving threats.\nThe Advanced Solutions team within the 1LMX data workstream is hiring an A/AI machine Learning Engineer Staff to help develop our Generative AI products. The SEMPL solution is a groundbreaking effort to revolutionize Lockheed Martin's Software Engineering and Management Process (SEMP) and Systems Development Life Cycle (SDLC) using Generative AI and Data Science with application to the 1LMX deliverables. We are committed to fostering a culture of innovation, and we're looking for an individual who shares our passion for using technology to drive positive change and acceleration.\nWhat You Will Be Doing:\nIn this role, you will play a critical role in transforming the way Lockheed Martin employees work by infusing Artificial Intelligence (AI) solutions into existing business processes. \nYou will contribute to the development of the 1LMX AI Acceleration Products that drive acceleration, inform data-driven decision making, and help the organization stay ahead of the curve. Some of the products for this role include working on ABAP coding agents for ERP.  This role will provide you with a unique opportunity to learn and grow yourself while also mentoring and leading others in this exciting and constantly evolving space while making meaningful contributions to the team's efforts. You will be a part of the adoption process and iterate with continuous development, incorporating user feedback quickly and delivering for the fast-paced 1LMX scope.\nWho You Are:\nYou are a motivated and enthusiastic engineer/full-stack developer with a strong foundation in software engineering, systems development, ABAP/UI5 and AI technologies.   With a start-up mentality and a growth mindset, you thrive in fast-paced environments, navigate ambiguity with ease, and are self-motivated to work independently.\nFurther Information About This Opportunity:\nThis role is fully remote but will require travel ~2x/quarter. US citizenship is required due to system access.\n#EBDT\nBasic Qualifications\n• Experience in software development, with a focus on full-stack engineering\n• Proficiency in Python or Node.js development  \n• Experience with Large Language Models (LLMs) and/or Generative AI (GenAI)\n• Understanding of the Software Development Lifecycle\n• Experience with creating stories and working in Jira \n• US Citizenship is required due to program requirements and system access\nFurther Information About This Opportunity:\nThis role is fully remote but will require travel ~2x/quarter. US citizenship is required due to system access.\nDesired skills\n• Experience developing in the SAP ecosystem (UI5, ABAP, BTP)\n• Experience with Agile and utilizing Jira for PI planning, Sprints, stories etc.\n• Experience developing with GenAI Coding Assistants (Spec driven development) & MCP\n• Proven experience designing, developing, and integrating RESTFUL APIs with FastAPI and Pydantic data modeling\n• Hands-on experience with eFOSS system\n• Experience with the OData standard\n• Working knowledge with Temporal workflow orchestration\n• Working knowledge of OpenSearch or Elasticsearch (index management, query DSLs, hybrid search)\n• Proficiency in asynchronous Python (asyncio, async/await patterns)\n• Demonstrated experience building or leveraging knowledge graph based solutions (e.g., graph databases, ontologies, SPARQL)\n• Experience with cloud-based platforms and containerization (e.g., Docker, Kubernetes)\n• Experience with GitLab pipelines, OpenShift, and other related technologies\n• Proficiency in additional programming languages, such as Java, C++, Rust, Go\n• Comfort with version control systems (e.g., Github & Gitlab, SAP CTS)\n• Bachelor's or Master's degree in Computer Science, Information Technology, Engineering, AI/ML or related field\nState\nColorado, Connecticut, Florida, Maryland, Puerto Rico, Texas\nVirtual\nyes\nCity\nAguadilla, Bethesda, Denver, Grand Prairie, Orlando, Shelton\nZip\n00603, 06484, 20817, 32819, 32825, 75051, 80221\nEEO\nLockheed Martin is an equal opportunity employer. Qualified candidates will be considered without regard to legally protected characteristics.\nThe application window will close in 90 days; applicants are encouraged to apply within 5 - 30 days of the requisition posting date in order to receive optimal consideration.\n*\nAt Lockheed Martin, we use our passion for purposeful innovation to help keep people safe and solve the world's most complex challenges. Our people are some of the greatest minds in the industry and truly make Lockheed Martin a great place to work. \n\nWith our employees as our priority, we provide diverse career opportunities designed to propel, develop, and boost agility. Our flexible schedules, competitive pay, and comprehensive benefits enable our employees to live a healthy, fulfilling life at and outside of work. We place an emphasis on empowering our employees by fostering an inclusive environment built upon integrity and corporate responsibility.\nIf this sounds like a culture you connect with, you’re invited to apply for this role. Or, if you are unsure whether your experience aligns with the requirements of this position, we encourage you to search on \nLockheed Martin Jobs\n, and apply for roles that align with your qualifications.\nCity, State\nAguadilla-PR, Bethesda-MD, Denver-CO, Grand Prairie-TX, Orlando-FL, Shelton-CT\nAbility to Telecommute\nFull time telecommuter\nOther Important Information\nBy applying to this job, you are expressing interest in this position and could be considered for other career opportunities where similar skills and requirements have been identified as a match.  Should this match be identified you may be contacted for this and future openings.\nAbility to work remotely\nFull-time Remote Telework: The employee selected for this position will work remotely full time at a location other than a Lockheed Martin designated office/job site. Employees may travel to a Lockheed Martin office for periodic meetings.\nWork Schedule Information\nLockheed Martin supports a variety of alternate work schedules that provide additional flexibility to our employees.  Schedules range from standard 40 hours over a five day work week while others may be condensed.  These condensed schedules provide employees with additional time away from the office and are in addition to our Paid Time off benefits.\nWork Schedule\n4x10 hour day, 3 days off per week \nSelect the Telework classification for this position\nEmployee that will telework full-time \nNational Pay Statement\nPay Rate:\n The annual base salary range for this position in California, Massachusetts, and New York (excluding most major metropolitan areas), Colorado, Hawaii, Illinois, Maryland, Minnesota, New Jersey, Vermont, Washington or Washington DC is $132,900  - $234,370. For states not referenced above, the salary range for this position will reflect the candidate’s final work location. Please note that the salary information is a general guideline only. Lockheed Martin considers factors such as (but not limited to) scope and responsibilities of the position, candidate's work experience, education/ training, key skills as well as market and business considerations when extending an offer.\nBenefits offered:\n Medical, Dental, Vision, Life Insurance, Short-Term Disability, Long-Term Disability, 401(k) match, Flexible Spending Accounts, EAP, Education Assistance, Parental Leave, Paid time off, and Holidays. \n(Washington state applicants only) Non-represented full-time employees: accrue at least 10 hours per month of Paid Time Off (PTO) to be used for incidental absences and other reasons; receive at least 90 hours for holidays. Represented full time employees accrue 6.67 hours of Vacation per month; accrue up to 52 hours of sick leave annually; receive at least 96 hours for holidays. PTO, Vacation, sick leave, and holiday hours are prorated based on start date during the calendar year.\nThis position is incentive plan eligible.\nPremium Pay Statement\nPay Rate:\n The annual base salary range for this position in most major metropolitan areas in California, Massachusetts, and New York is $152,900  - $264,960. For states not referenced above, the salary range for this position will reflect the candidate’s final work location. Please note that the salary information is a general guideline only. Lockheed Martin considers factors such as (but not limited to) scope and responsibilities of the position, candidate's work experience, education/ training, key skills as well as market and business considerations when extending an offer.\nBenefits offered:\n Medical, Dental, Vision, Life Insurance, Short-Term Disability, Long-Term Disability, 401(k) match, Flexible Spending Accounts, EAP, Education Assistance, Parental Leave, Paid time off, and Holidays.\nThis position is incentive plan eligible."
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



    


    

