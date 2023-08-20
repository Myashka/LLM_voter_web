from fastapi import FastAPI, Request, BackgroundTasks, Form
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

logging.basicConfig(level=logging.INFO)


def timeout_checker():
    timeout = 10 * 60
    while True:
        with engine.connect() as connection:
            stmt = (
                update(questions_answers)
                .where((func.now() - questions_answers.c.last_accessed) > timeout)
                .where(questions_answers.c.status == "in_process")
                .values(status="waiting")
            )
            connection.execute(stmt)
        time.sleep(60)


app = FastAPI()

templates = Jinja2Templates(directory="templates")

static_folder = os.path.join(os.path.dirname(__file__), "static")
print(static_folder)
app.mount("/static", StaticFiles(directory=static_folder), name="static")


@app.on_event("startup")
async def startup_event():
    bg_tasks = BackgroundTasks()
    bg_tasks.add_task(timeout_checker)


@app.get("/", response_class=HTMLResponse)
async def display_question(request: Request):
    with engine.begin() as connection:
        # Получаем следующий вопрос со статусом "waiting"
        s = (
            select(questions_answers)
            .where(questions_answers.c.status == "waiting")
            .limit(1)
        )
        question_data = connection.execute(s).fetchone()

        if not question_data:
            logging.info("No questions with status 'waiting' found in the database.")
            return templates.TemplateResponse("no_questions.html", {"request": request})

        
        stmt = (
            update(questions_answers)
            .where(questions_answers.c.q_id == question_data.q_id)
            .values(status="in_process", last_accessed=func.now())
        )
        connection.execute(stmt)

        logging.info(
            f"Found question with ID {question_data.q_id} and title '{question_data.title}'."
        )

        s = select(generated_answers).where(
            generated_answers.c.qa_id == question_data.qa_id
        )
        generated_answers_data = connection.execute(s).fetchall()

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
        response.headers[
            "Cache-Control"
        ] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

        return response


@app.post("/", response_class=HTMLResponse)
async def handle_question(
    request: Request,
    q_id: int = Form(...),
    gen_id_1: int = Form(...),
    rating_1: int = Form(...),
    rights_1: bool = Form(...),
    gen_id_2: int = Form(...),
    rating_2: int = Form(...),
    rights_2: bool = Form(...),
    gen_id_3: int = Form(...),
    rating_3: int = Form(...),
    rights_3: bool = Form(...),
):
    logging.info(f"Received POST data: q_id={q_id}")
    with engine.begin() as connection:
        ratings = [
            {"gen_id": gen_id_1, "rating": rating_1, "rights": rights_1},
            {"gen_id": gen_id_2, "rating": rating_2, "rights": rights_2},
            {"gen_id": gen_id_3, "rating": rating_3, "rights": rights_3},
        ]
        for rating in ratings:
            stmt = insert(user_ratings_table).values(
                gen_id=rating["gen_id"],
                rating_value=rating["rating"],
                rights=rating["rights"],
            )
            connection.execute(stmt)

        stmt = (
            update(questions_answers)
            .where(questions_answers.c.q_id == q_id)
            .values(status="processed")
        )
        connection.execute(stmt)

        # Получаем следующий вопрос со статусом "waiting"
        s = (
            select(questions_answers)
            .where(questions_answers.c.status == "waiting")
            .limit(1)
        )
        next_question_data = connection.execute(s).fetchone()

        # Если следующий вопрос найден, меняем его статус на "in_process"
        if next_question_data:
            stmt = (
                update(questions_answers)
                .where(questions_answers.c.q_id == next_question_data.q_id)
                .values(status="in_process", last_accessed=func.now())
            )
            connection.execute(stmt)

            s = select(generated_answers).where(
                generated_answers.c.qa_id == next_question_data.qa_id
            )
            generated_answers_data = connection.execute(s).fetchall()

            logging.info(
                f"Found question with ID {next_question_data.q_id} and title '{next_question_data.title}'."
            )

            return templates.TemplateResponse(
                "question_template.html",
                {
                    "request": request,
                    "title": next_question_data.title,
                    "question": next_question_data.question,
                    "answer": next_question_data.answer,
                    "generated_answers": generated_answers_data,
                    "q_id": next_question_data.q_id,
                },
            )
        else:
            return templates.TemplateResponse("no_questions.html", {"request": request})

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
