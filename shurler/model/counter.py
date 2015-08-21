from sqlalchemy import Column, UniqueConstraint, ForeignKey, Index
from sqlalchemy import schema as saschema
from sqlalchemy.types import Unicode, Integer, UnicodeText, DateTime

from shurler.model.meta import Base
from shurler.model.redir import Redir

class Counter(Base):
    __tablename__ = 'counter'

    id = Column(Integer, primary_key=True)
    short_id = Column(ForeignKey('redir.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    counter = Column(Integer, nullable=False)

    __table_args__ = ((UniqueConstraint(short_id)),
            {
            "mysql_engine":"InnoDB",
            "mysql_charset":"utf8"
            } )

    def __init__(self, s):
        if (s != None):
            self.short_id = s
            self.counter = 0
            print 'creo l\'oggetto counter'

