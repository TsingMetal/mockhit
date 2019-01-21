from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String


Base = declarative_base()
engine = create_engine('sqlite:///./db/user.db', echo=False)
session = sessionmaker(bind=engine)()


class User(Base):
    __tablename__ = 'users'

    account = Column(String, primary_key=True)
    passwd = Column(String)
    country = Column(String)

    def __repr__(self):
        return '<User(account=%s, country=%s)>' \
                    %(self.account, self.country)


if __name__ == '__main__':
    Base.metadata.create_all(engine)
