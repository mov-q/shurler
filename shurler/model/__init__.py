"""The application's model objects"""
from shurler.model.meta import Session, Base
from shurler.model.user import User
from shurler.model.redir import Redir
from shurler.model.counter import Counter
from shurler.model.visitor import Visitor


def init_model(engine):
    """Call me before using any of the tables or classes in the model"""
    Session.configure(bind=engine)
