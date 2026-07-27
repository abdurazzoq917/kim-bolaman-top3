from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.data import CAREERS, DOMAINS, QUESTIONS


BASE_DIR = Path(__file__).resolve().parent.parent


app = FastAPI(
    title="Kim bo‘laman?",
    description=(
        "145 ta kasb orasidan "
        "Top 3 mos kasbni aniqlovchi test"
    ),
    version="5.0.0",
)


app.mount(
    "/static",
    StaticFiles(
        directory=BASE_DIR / "static",
    ),
    name="static",
)


templates = Jinja2Templates(
    directory=BASE_DIR / "templates",
)


@app.get(
    "/",
    response_class=HTMLResponse,
)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "career_count": len(CAREERS),
            "question_count": len(QUESTIONS),
        },
    )


@app.get(
    "/test",
    response_class=HTMLResponse,
)
def test_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="test.html",
        context={
            "questions": QUESTIONS,
            "error": None,
        },
    )


@app.post(
    "/result",
    response_class=HTMLResponse,
)
async def result_page(request: Request):
    form_data = await request.form()

    domain_scores = {
        domain_key: 0.0
        for domain_key in DOMAINS
    }

    trait_scores: dict[str, float] = {}

    for question_index, question in enumerate(
        QUESTIONS
    ):
        selected_values = form_data.getlist(
            f"q_{question_index}"
        )

        if (
            len(selected_values) < 1
            or len(selected_values) > 2
        ):
            return templates.TemplateResponse(
                request=request,
                name="test.html",
                context={
                    "questions": QUESTIONS,
                    "error": (
                        f"{question_index + 1}-savolda "
                        "kamida 1 ta, ko‘pi bilan "
                        "2 ta javob tanlang."
                    ),
                },
                status_code=400,
            )

        selection_weight = (
            0.85
            if len(selected_values) == 2
            else 1.0
        )

        for selected_value in selected_values:
            try:
                selected_index = int(
                    selected_value
                )

                selected_option = question[
                    "options"
                ][selected_index]

            except (ValueError, IndexError):
                continue

            for domain_key, point in selected_option[
                "weights"
            ].items():
                domain_scores[domain_key] += (
                    point * selection_weight
                )

            for trait in selected_option["traits"]:
                trait_scores[trait] = (
                    trait_scores.get(
                        trait,
                        0.0,
                    )
                    + selection_weight
                )

    ranked_careers = []

    for career_key, career in CAREERS.items():
        domain_score = domain_scores.get(
            career["domain"],
            0.0,
        )

        matching_trait_score = sum(
            trait_scores.get(
                trait,
                0.0,
            )
            for trait in career["traits"]
        )

        total_score = (
            domain_score * 3
            + matching_trait_score
        )

        ranked_careers.append(
            {
                "key": career_key,
                "score": round(
                    total_score,
                    1,
                ),
                **career,
            }
        )

    ranked_careers.sort(
        key=lambda career: (
            career["score"],
            career["title"],
        ),
        reverse=True,
    )

    top_three = []
    used_domains = set()

    for career in ranked_careers:
        if career["domain"] in used_domains:
            continue

        top_three.append(career)

        used_domains.add(
            career["domain"]
        )

        if len(top_three) == 3:
            break

    highest_score = (
        top_three[0]["score"]
        or 1
    )

    for position, career in enumerate(
        top_three,
        start=1,
    ):
        career["position"] = position

        career["percent"] = round(
            career["score"]
            / highest_score
            * 100
        )

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "top_three": top_three,
            "best": top_three[0],
            "career_count": len(CAREERS),
        },
    )


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "careers": len(CAREERS),
        "questions": len(QUESTIONS),
    }