from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String


Base = declarative_base()
engine = create_engine('sqlite:///./db/proxy.db', echo=False)
session = sessionmaker(bind=engine)()


class Proxy(Base):
    __tablename__ = 'proxy'

    ip = Column(String, primary_key=True)
    port = Column(Integer)
    country = Column(String)
    is_valid = Column(Integer)
    update_date = Column(String)

    def __repr__(self):
        return '<Proxy(ip="%s", port=%s, country="%s")>' \
                    % (self.ip, self.port, self.country)


if __name__ == '__main__':
    Base.metadata.create_all(engine)
