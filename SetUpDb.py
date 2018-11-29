#!/usr/bin/env python3
import os
import sys
from sqlalchemy import \
    Column, ForeignKey, Boolean, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class User(Base):
    __tablename__ = 'User'

    ID = Column(Integer, primary_key=True)
    User_Name = Column(String(25), nullable=False)
    Password = Column(String(25), nullable=False)
    First = Column(String(25), nullable=False)
    Last = Column(String(25), nullable=False)
    Email = Column(String(25), nullable=False)
    Profile_Pic = Column(String(25), nullable=True)
    Google_ID = Column(String(25), nullable=True)
    Logged_In = Column(Boolean, default=False)

    @property
    def serialize(self):
        return {'User_Name': self.User_Name, }


class Item(Base):
    __tablename__ = 'Item'

    ID = Column(Integer, primary_key=True)
    Owner_ID = Column(Integer, ForeignKey('User.ID'))
    Owner = relationship(User)
    Name = Column(String(25), nullable=False)
    Category = Column(String(25), nullable=False)
    Description = Column(String(300), nullable=True)
    Image = Column(String(100), nullable=True)

    @property
    def serialize(self):
        # returns the data in a serialized format
        return {
            'ID': self.ID,
            'Owner_ID': self.Owner_ID,
            'Owner': self.Owner.serialize,
            'Name': self.Name,
            'Category': self.Category,
            'Description': self.Description,
            'Image': self.Image,
        }


def Create_Data_Base():
    Engine = create_engine('sqlite:///Catalog.db')
    Base.metadata.create_all(Engine)


if __name__ == '__main__':
    Create_Data_Base()
