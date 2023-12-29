from .database import Base
from sqlalchemy import  TIMESTAMP, Column, Integer, String, Boolean, text, ForeignKey, ARRAY
from sqlalchemy.orm import relationship

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, server_default="True", nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    owner_id = Column(Integer, ForeignKey("users.id",ondelete="CASCADE"), nullable=False)
    
    owner = relationship("User")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False, unique=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    
class Vote(Base):
    __tablename__ = "votes"
    
    user_id = Column(Integer, ForeignKey("users.id" , ondelete="CASCADE"), primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id" , ondelete="CASCADE"), primary_key=True)

class Test(Base):
    __tablename__ = "test"
    
    user_id = Column(Integer, nullable=False, primary_key=True)
    seen_posts = Column(Integer ,nullable=False, primary_key=True)

class Comment(Base):
    __tablename__ = "comments"
    
    comment_id = Column(Integer, primary_key=True, nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id" , ondelete="CASCADE"))
    commenter_id = Column(Integer, nullable=False)
    comment = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))