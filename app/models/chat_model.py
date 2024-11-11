from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class Chat(Base):
    __tablename__ = 'chats'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    session_id = Column(String(255), nullable=False)
    content = Column(JSON, nullable=False)  # Using JSON data type
    user = relationship("User", back_populates="chats")

    def __repr__(self):
        return f"<Chat(id={self.id}, user_id={self.user_id}, session_id='{self.session_id}')>"
