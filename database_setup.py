import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 
Base = declarative_base()

class BloodType(Base):
    __tablename__ = 'blood_type'
   
    id = Column(Integer, primary_key=True)
    name = Column(String(5), nullable=False)
    status = Column(String(250), nullable=False)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name'         : self.name,
           'id'           : self.id,
           'status'           : self.status,
       }
 
class Items(Base):
    __tablename__ = 'items'

    name =Column(String(5), nullable = False)
    id = Column(Integer, primary_key = True)
    description = Column(String(250))
    amount = Column(String(8))
    bloodType_id = Column(Integer,ForeignKey('blood_type.id'))
    blood_type = relationship(BloodType)



    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name'         : self.name,
           'id'         : self.id,
           'description'         : self.description, 
           'amount'         : self.amount,    
       }


engine = create_engine('sqlite:///bloodTypes.db')

Base.metadata.create_all(engine)