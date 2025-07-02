from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Car(Base):
    __tablename__ = 'cars'

    id = Column(Integer, primary_key=True)
    make = Column(String, nullable=False)
    model = Column(String)
    trim = Column(String)
    miles = Column(Integer)
    sell_price = Column(Integer)
    claimed_condition = Column(String)
    excellent_pred = Column(Integer)
    very_good_pred = Column(Integer)
    good_pred = Column(Integer)
    fair_pred = Column(Integer)
    link = Column(Text)
    explanation = Column(Text)
    mechanical_issues = Column(Boolean)
    posted_date  = Column(DateTime)

class Checked(Base):
    __tablename__ = 'checked'

    id = Column(Integer, primary_key=True)
    link = Column(Text)
