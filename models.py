from sqlalchemy import (
    Column, BigInteger, String, Text, Date,
    ForeignKey, Integer, DECIMAL, TIMESTAMP,
    create_engine
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

DATABASE_URL = "mysql+pymysql://root:mysql@localhost:3306/practice"

engine = create_engine(
    DATABASE_URL,
    echo=True,           # логирование SQL
    pool_pre_ping=True,  # проверка соединения
    pool_recycle=3600    # важно для MySQL
)

class Conf(Base):
    __tablename__ = "Conf"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(String(255))
    short_title = Column(String(255))
    date = Column(Date)
    redactor = Column(String(255), default="Углев В.А.", nullable=False)
    bibliographic_data = Column(Text)
    status_rinc = Column(String(255))
    level = Column(String(255))
    book_link_in_pdf = Column(String(2048))

    created_at = Column(TIMESTAMP, default=func.now())
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now())

    sections = relationship("Section", back_populates="conf", cascade="all, delete")

class Section(Base):
    __tablename__ = "Section"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    section_title = Column(String(255))
    short_title = Column(String(255))
    id_conf = Column(BigInteger, ForeignKey("Conf.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    count = Column(String(255))

    created_at = Column(TIMESTAMP, default=func.now())
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now())

    conf = relationship("Conf", back_populates="sections")
    articles = relationship("RaiArticleDetail", back_populates="section", cascade="all, delete")

class Rid(Base):
    __tablename__ = "Rid"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(String(255))
    id_ridtype = Column(BigInteger, ForeignKey("Rid_type.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    year = Column(Integer)  # Year в MySQL лучше хранить как Integer
    key_words_rus = Column(Text)
    key_words_eng = Column(Text)
    annotation_rus = Column(Text)
    annotation_eng = Column(Text)

    created_at = Column(TIMESTAMP, default=func.now())
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now())

    article_details = relationship("RaiArticleDetail", back_populates="rid", cascade="all, delete")
    kaf_details = relationship("KafRidDetail", back_populates="rid", cascade="all, delete")

class RaiArticleDetail(Base):
    __tablename__ = "Rai_article_detail"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    id_rid = Column(BigInteger, ForeignKey("Rid.id", ondelete="CASCADE", onupdate="CASCADE"))
    date = Column(Date)
    pages = Column(String(255))
    act = Column(String(255))
    payment = Column(String(255))
    summ = Column(DECIMAL(11, 2))
    stage = Column(String(255))
    comment = Column(String(255))
    category = Column(String(255))
    id_section = Column(BigInteger, ForeignKey("Section.id", ondelete="CASCADE", onupdate="CASCADE"))
    input_file = Column(String(255))
    result_file = Column(String(255))
    pages_in_book = Column(Integer)
    udk = Column(String(255))
    language = Column(String(255))
    indexation = Column(String(255))

    created_at = Column(TIMESTAMP, default=func.now())
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now())

    rid = relationship("Rid", back_populates="article_details")
    section = relationship("Section", back_populates="articles")

class KafRidDetail(Base):
    __tablename__ = "Kaf_rid_detail"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    id_rid = Column(BigInteger, ForeignKey("Rid.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    language = Column(String(255))
    pages = Column(Integer)
    bibliographic_data = Column(Text)
    indexation = Column(String(255))
    patent_type = Column(String(255))
    patent_holder = Column(String(255))
    patent_comment = Column(String(255))
    patent_status = Column(String(255))
    patent_date = Column(Date)
    dissertation_speciality = Column(String(255))
    dissertation_status = Column(String(255))
    dissertation_comment = Column(String(255))
    affiliation_degree = Column(String(255))
    specialization_book = Column(String(255))
    result_file = Column(String(255))
    internal_link = Column(Text)
    level = Column(String(255))
    additional_info = Column(String(255))

    created_at = Column(TIMESTAMP, default=func.now())
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now())

    rid = relationship("Rid", back_populates="kaf_details")
