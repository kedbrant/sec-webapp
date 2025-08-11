from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    cik = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    ticker = Column(String, index=True)
    sector = Column(String)
    industry = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    filings = relationship("Filing", back_populates="company")

class Filing(Base):
    __tablename__ = "filings"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    form_type = Column(String, index=True)  # 13D, 13G, etc.
    filing_date = Column(DateTime, index=True)
    accession_number = Column(String, unique=True, index=True)
    url = Column(String)
    
    # Ownership details
    owner_name = Column(String)
    owner_cik = Column(String)
    shares_owned = Column(Integer)
    ownership_percent = Column(Float)
    
    # Filing content
    raw_text = Column(Text)
    purpose = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    company = relationship("Company", back_populates="filings")