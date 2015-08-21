from sqlalchemy import Column, UniqueConstraint, ForeignKey, Index
from sqlalchemy import schema as saschema
from sqlalchemy.types import Unicode, Integer, UnicodeText, DateTime

from shurler.model.meta import Base
from shurler.model.redir import Redir

class Visitor(Base):
    __tablename__ = 'visitor'

    id = Column(Integer, primary_key=True)
    short_id = Column(ForeignKey('redir.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    ipaddr = Column(Unicode(56), nullable=False)
    dt = Column(DateTime, nullable=False)
    agent = Column(Unicode(128), nullable=True)

    __table_args__ = (
            {
            "mysql_engine":"InnoDB",
            "mysql_charset":"utf8"
            } )

    def __init__(self, s, i, t, a = None):
        if (s != None) and (i != None) and (t != None):
            self.short_id = s
            self.ipaddr = i
            self.dt = t
            self.agent = a
            print 'creo l\'oggetto visitor'

