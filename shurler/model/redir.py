from sqlalchemy import Column, UniqueConstraint, ForeignKey, Index
from sqlalchemy import schema as saschema
from sqlalchemy.types import Unicode, Integer, UnicodeText, DateTime
from sqlalchemy.dialects.mysql import VARCHAR

from shurler.model.meta import Base
from shurler.model.user import User

class Redir(Base):
    __tablename__ = 'redir'

    id = Column(Integer, primary_key=True)
    short = Column(VARCHAR(18, collation='utf8_bin'), nullable=False)
    long = Column(Unicode(4096), nullable=False)
    ipaddr = Column(Unicode(56), nullable=False)
    created = Column(DateTime, nullable=False)
    created_by = Column(ForeignKey('user.id', ondelete='SET NULL', onupdate='CASCADE'), nullable=True)

    __table_args__ = ((UniqueConstraint(short)),
            {
            "mysql_engine":"InnoDB",
            "mysql_charset":"utf8",
            "mysql_collate": "utf8_bin"
            } )

    def __init__(self, s, l, c, i, cby = None):
        if (s != None) and (l != None) and (c != None):
            self.short = s
            self.long = l
            self.created = c
            self.ipaddr = i
            self.created_by = cby
            print 'creo l\'oggetto'

