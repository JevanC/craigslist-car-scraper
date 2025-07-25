from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, func
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
    year = Column(Integer)
    claimed_condition = Column(String)
    excellent_pred = Column(Integer)
    very_good_pred = Column(Integer)
    good_pred = Column(Integer)
    fair_pred = Column(Integer)
    link = Column(Text)
    explanation = Column(Text)
    mechanical_issues = Column(Boolean)
    posted_date  = Column(DateTime)
    added_date = Column(DateTime, default=func.now())

    def to_dict(self):
        return {
            "make": self.make,
            "model": self.model,
            "trim": self.trim,
            "miles": self.miles,
            "sell_price": self.sell_price,
            "year":self.year,
            "claimed_condition": self.claimed_condition,
            'excellent_pred' : self.excellent_pred,
            'very_good_pred' : self.very_good_pred,
            'good_pred' : self.good_pred,
            'fair_pred' : self.fair_pred,
            "link": self.link,
            'explanation' : self.explanation,
            'mechanical_issues' : self.mechanical_issues
        }

class Checked(Base):
    __tablename__ = 'checked'

    id = Column(Integer, primary_key=True)
    link = Column(Text)
