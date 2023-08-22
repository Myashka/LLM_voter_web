from fastapi import FastAPI, Request, Form
from models.database import engine
from models.questions import questions_answers, generated_answers, user_ratings_table
from sqlalchemy.sql import select, update, insert
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func
import time
import os
import logging
import uuid

logging.basicConfig(level=logging.INFO)

app = FastAPI()

templates = Jinja2Templates(directory="templates")

static_folder = os.path.join(os.path.dirname(__file__), "static")
print(static_folder)
app.mount("/static", StaticFiles(directory=static_folder), name="static")


async def get_next_question():
    with engine.begin() as connection:
        s = (
            select(
                questions_answers.c.qa_id,
                questions_answers.c.q_id,
                questions_answers.c.title,
                questions_answers.c.question,
                questions_answers.c.answer,
            )
            .join(generated_answers, questions_answers.c.qa_id == generated_answers.c.qa_id)
            .group_by(questions_answers.c.q_id, questions_answers.c.qa_id)
            .order_by(questions_answers.c.rating_count.asc())
            .limit(1)
        )
        question_data = connection.execute(s).fetchone()

        if not question_data:
            return None

        s = select(generated_answers).where(
            generated_answers.c.qa_id == question_data.qa_id
        )
        generated_answers_data = connection.execute(s).fetchall()

        return question_data, generated_answers_data


@app.get("/", response_class=HTMLResponse)
async def display_question(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())

    question_data, generated_answers_data = await get_next_question()
    logging.info(f"GET data: q_id={question_data.q_id} and session_id={session_id}")

    if not question_data:
        logging.info("No questions found in the database.")
        return templates.TemplateResponse("no_questions.html", {"request": request})

    content = templates.TemplateResponse(
        "question_template.html",
        {
            "request": request,
            "title": question_data.title,
            "question": question_data.question,
            "answer": question_data.answer,
            "generated_answers": generated_answers_data,
            "q_id": question_data.q_id,
        },
    )

    response = Response(content.body, media_type="text/html")
    response.set_cookie(key="session_id", value=session_id)
    response.headers[
        "Cache-Control"
    ] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response


@app.post("/", response_class=HTMLResponse)
async def handle_question(request: Request, q_id: int = Form(...)):
    form_data = await request.form()
    session_id = request.cookies.get("session_id")
    logging.info(f"Received POST data: q_id={q_id} and session_id={session_id}")
    with engine.begin() as connection:
        for key, value in form_data.items():
            if key.startswith("gen_id_"):
                gen_id = int(value)
                rating = form_data.get(f"rating_{gen_id}")
                relevance = bool(form_data.get(f"relevance_{gen_id}"))
                correctness = bool(form_data.get(f"correctness_{gen_id}"))
                usefulness = bool(form_data.get(f"usefulness_{gen_id}"))
                justification = bool(form_data.get(f"justification_{gen_id}"))

                # Insert the rating for the generated answer
                stmt = insert(user_ratings_table).values(
                    session_id=session_id,
                    gen_id=gen_id,
                    rating_value=rating,
                    relevance=relevance,
                    correctness=correctness,
                    usefulness=usefulness,
                    justification=justification,
                )
                connection.execute(stmt)

                # Get the related qa_id for the gen_id
                s = select(generated_answers.c.qa_id).where(
                    generated_answers.c.gen_id == gen_id
                )
                related_qa_id = connection.execute(s).scalar()

                # Update the rating count for the question in questions_answers
                update_stmt = (
                    update(questions_answers)
                    .where(questions_answers.c.qa_id == related_qa_id)
                    .values(rating_count=questions_answers.c.rating_count + 1)
                )
                connection.execute(update_stmt)

    question_data, generated_answers_data = await get_next_question()

    if question_data:
        return templates.TemplateResponse(
            "question_template.html",
            {
                "request": request,
                "title": question_data.title,
                "question": question_data.question,
                "answer": question_data.answer,
                "generated_answers": generated_answers_data,
                "q_id": question_data.q_id,
            },
        )
    else:
        return templates.TemplateResponse("no_questions.html", {"request": request})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
