from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from pgvector.sqlalchemy import Vector
from database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String)
    title = Column(String)
    company = Column(String)
    workplace_type = Column(ARRAY(String))
    apply_url = Column(String)
    location = Column(String)
    posted = Column(DateTime)
    full_description_plain = Column(String)
    status = Column(String)


class Profile(Base):
    __tablename__ = "profile"

    id = Column(Integer, primary_key=True, index=True)
    profile = Column(JSONB)
    embedding = Column(Vector(3072))




    