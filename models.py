from sqlalchemy import Column, Integer, String, DateTime, Index, Computed
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, TSVECTOR
from pgvector.sqlalchemy import Vector
from database import Base

class Job(Base):
    __tablename__ = "job"

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
    embedding = Column(Vector(1536))
    # search_vector = Column(TSVECTOR)
    search_vector = Column(
    TSVECTOR,
        Computed(
            """
            setweight(to_tsvector('english', coalesce(full_description_plain, '')), 'A')
            """,
            persisted=True
        )
    )

    __table_args__ = (

        # Full text index
        Index(
            "ix_job_search_vector",
            search_vector,
            postgresql_using="gin",
        ),

        # Vector index
        Index(
            "ix_job_embedding",
            "embedding",
            postgresql_using="hnsw",
            postgresql_ops={
                "embedding": "vector_cosine_ops"
            }
        ),
    )



class Profile(Base):
    __tablename__ = "profile"

    id = Column(Integer, primary_key=True, index=True)
    profile = Column(JSONB)
    embedding = Column(Vector(1536))




    