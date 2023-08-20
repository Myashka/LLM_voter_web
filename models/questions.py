from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Table,
    Enum,
    Boolean,
    DateTime,
    func,
)
from models.database import metadata

questions_answers = Table(
    "questions_answers",
    metadata,
    Column("qa_id", Integer, primary_key=True, index=True),
    Column("q_id", Integer, unique=True),
    Column("title", String),
    Column("question", String),
    Column("answer", String),
    Column("status", Enum("waiting", "in_process", "processed"), default="waiting"),
    Column("last_accessed", DateTime, default=func.now()),
)

generated_answers = Table(
    "generated_answers",
    metadata,
    Column("gen_id", Integer, primary_key=True, index=True),
    Column("qa_id", Integer, ForeignKey("questions_answers.qa_id")),
    Column("generated_answer", String),
    Column("csv_gen_id", Integer),
)

user_ratings_table = Table(
    "user_ratings",
    metadata,
    Column("rating_id", Integer, primary_key=True, index=True),
    Column("gen_id", Integer, ForeignKey("generated_answers.gen_id")),
    Column("rating_value", Integer),
    Column("rights", Boolean),
)
