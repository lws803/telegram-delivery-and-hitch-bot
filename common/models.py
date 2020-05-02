from sqlalchemy import (BigInteger, Column, DateTime, Enum, Float, Integer,
                        String, func)
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.ext.declarative import declarative_base

from common.constants import RoleType, StateType


class MyBase(object):
    """Custom base class with default __repr__ method."""
    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self.id)


Base = declarative_base(cls=MyBase)


class Request(Base):
    __tablename__ = 'requests'

    id = Column(BigInteger, primary_key=True)
    role = Column(Enum(RoleType), nullable=False)
    chat_id = Column(BigInteger, nullable=False)
    location_pickup = Column(JSON, nullable=True)
    location_dropoffs = Column(JSON, nullable=True)
    time = Column(DateTime, nullable=True)
    price = Column(Float, nullable=True)
    package_type = Column(String(250), nullable=True)
    first_name = Column(String(250), nullable=True)
    last_name = Column(String(250), nullable=True)
    state = Column(Enum(StateType), nullable=False)
    additional_info = Column(String(250), nullable=True)
    last_updated = Column(DateTime, onupdate=func.now(), nullable=False, server_default=func.now())
    telegram_handle = Column(String(250), nullable=False)


class Blacklist(Base):
    __tablename__ = 'blacklist'
    id = Column(BigInteger, primary_key=True)
    chat_id = Column(BigInteger, nullable=False)


class Report(Base):
    __tablename__ = 'reports'
    id = Column(BigInteger, primary_key=True)
    chat_id = Column(BigInteger, nullable=False)
    report_count = Column(Integer, nullable=False)


requests = Request.__table__
blacklist = Blacklist.__table__
reports = Report.__table__
