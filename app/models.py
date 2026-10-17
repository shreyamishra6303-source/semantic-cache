from sqlalchemy import Column,String,Float,Integer,Text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from . database import base

class request_log(base):
    __tablename__="request_logs"
    id=Column(Integer,primary_key=True,index=True)
    prompt=Column(String,nullable=False)
    latency=Column(Float,nullable=False)
    created_at=Column(TIMESTAMP(timezone=True),server_default=func.now())

class cache_entries(base):
    __tablename__="cache_data"
    id=Column(Integer,primary_key=True,index=True)
    tenant_id=Column(String,nullable=False,index=True)
    model = Column(String, nullable=False, index=True)
    params_hash = Column(String, nullable=False)
    prompt=Column(Text,nullable=False)
    response=Column(String,nullable=False)
    embedding=Column(Vector(384),nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    expires_at = Column(TIMESTAMP(timezone=True), nullable=True)
    hit_count = Column(Integer, nullable=False, default=0)
