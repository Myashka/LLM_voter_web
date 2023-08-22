from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Table,
    Boolean,
    DateTime,
    UniqueConstraint,
    func,
)
from models.database import metadata

questions_answers = Table(
    "questions_answers",
    metadata,
    Column("qa_id", Integer, primary_key=True, index=True),
    Column("q_id", Integer),
    Column("csv_id", Integer, nullable=True),
    Column("rating_count", Integer, default=0),
    Column("title", String),
    Column("question", String),
    Column("answer", String),
    Column("last_accessed", DateTime, default=func.now()),
    UniqueConstraint("q_id", "csv_id", name="uix_q_id_csv_id"),
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
    Column("session_id", String),
    Column("gen_id", Integer, ForeignKey("generated_answers.gen_id")),
    Column("rating_value", Integer),
    Column("relevance", Boolean),
    Column("correctness", Boolean),
    Column("usefulness", Boolean),
    Column("justification", Boolean),
)
