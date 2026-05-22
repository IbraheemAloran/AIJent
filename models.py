from sqlalchemy import Column, Integer, String, DateTime
from database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String)
    title = Column(String)
    company = Column(String)
    workplace_type = Column(String)
    apply_url = Column(String)
    location = Column(String)
    posted = Column(DateTime)
    full_description_plain = Column(String)
    status = Column(String)
    




    