from sqlalchemy import Column, UniqueConstraint, ForeignKey
from sqlalchemy import schema as saschema
from sqlalchemy.types import Unicode, Integer, UnicodeText, DateTime

from shurler.model.meta import Base

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(Unicode(64), nullable=False)
    password = Column(Unicode(4096), nullable=False)
    created = Column(DateTime, nullable=False)
    cat_q = Column(UnicodeText(256), nullable=True)
    cat_a = Column(Unicode(256), nullable=True)

    __table_args__ = ((UniqueConstraint(username)),
            {
            "mysql_engine":"InnoDB",
            "mysql_charset":"utf8"
            } )
    
    def __init__(self):
        pass
