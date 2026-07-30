from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.data import CAREERS, DOMAINS, QUESTIONS


# Loyiha asosiy papkasini aniqlaydi.
# app/main.py -> app -> loyiha asosiy papkasi
BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"


app = FastAPI(
    title="Kim bo‘laman?",
    description="Kasb tanlash testi",
    version="1.0.0",
)


# Railway domeni oldindan noma’lum bo‘lgani uchun
# barcha hostlarga ruxsat beriladi.
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],
)


# static papkasini ulash
app.mount(
    "/static",
    StaticFiles(directory=str(STATIC_DIR)),
    name="static",
)


# templates papkasini ulash
templates = Jinja2Templates(
    directory=str(TEMPLATES_DIR)
)


@app.get(
    "/",
    response_class=HTMLResponse,
)
async def home(request: Request):
    """
    Saytning bosh sahifasi.
    """

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
async def test_page(request: Request):
    """
    Kasb testini ko‘rsatadi.
    """

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
    """
    Test javoblarini hisoblaydi va
    foydalanuvchiga eng mos uchta kasbni chiqaradi.
    """

    form_data = await request.form()

    # Har bir yo‘nalish uchun boshlang‘ich ball
    domain_scores = {
        domain_key: 0.0
        for domain_key in DOMAINS
    }

    # Xarakter xususiyatlari uchun ballar
    trait_scores: dict[str, float] = {}

    for question_index, question in enumerate(QUESTIONS):
        field_name = f"q_{question_index}"

        selected_values = form_data.getlist(
            field_name
        )

        # Har bir savolda kamida 1 ta,
        # ko‘pi bilan 2 ta javob bo‘lishi kerak.
        if not 1 <= len(selected_values) <= 2:
            return templates.TemplateResponse(
                request=request,
                name="test.html",
                context={
                    "questions": QUESTIONS,
                    "error": (
                        f"{question_index + 1}-savolda "
                        "kamida 1 ta va ko‘pi bilan "
                        "2 ta javob tanlang."
                    ),
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # 2 ta javob tanlansa, har birining
        # ta’siri biroz kamaytiriladi.
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
            except (TypeError, ValueError):
                return templates.TemplateResponse(
                    request=request,
                    name="test.html",
                    context={
                        "questions": QUESTIONS,
                        "error": (
                            f"{question_index + 1}-savolda "
                            "noto‘g‘ri javob yuborildi."
                        ),
                    },
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            options = question["options"]

            # Manfiy yoki mavjud bo‘lmagan indeksni
            # qabul qilmaslik.
            if not 0 <= selected_index < len(options):
                return templates.TemplateResponse(
                    request=request,
                    name="test.html",
                    context={
                        "questions": QUESTIONS,
                        "error": (
                            f"{question_index + 1}-savolda "
                            "noto‘g‘ri variant tanlandi."
                        ),
                    },
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            selected_option = options[
                selected_index
            ]

            # Yo‘nalish ballarini hisoblash
            for domain_key, point in selected_option[
                "weights"
            ].items():
                domain_scores[domain_key] += (
                    point * selection_weight
                )

            # Xarakter ballarini hisoblash
            for trait in selected_option["traits"]:
                trait_scores[trait] = (
                    trait_scores.get(trait, 0.0)
                    + selection_weight
                )

    ranked_careers = []

    # Har bir kasb uchun umumiy ball hisoblash
    for career_key, career in CAREERS.items():
        domain_score = domain_scores.get(
            career["domain"],
            0.0,
        )

        matching_trait_score = sum(
            trait_scores.get(trait, 0.0)
            for trait in career["traits"]
        )

        total_score = (
            domain_score * 3
            + matching_trait_score
        )

        ranked_careers.append(
            {
                "key": career_key,
                "score": round(total_score, 1),
                **career,
            }
        )

    # Eng yuqori ball birinchi chiqadi.
    # Ball teng bo‘lsa, nom bo‘yicha tartiblanadi.
    ranked_careers.sort(
        key=lambda career: (
            -career["score"],
            career["title"],
        )
    )

    top_three = []
    used_domains = set()

    # Bir xil yo‘nalishdan uchta kasb chiqib
    # qolmasligi uchun har xil yo‘nalish tanlanadi.
    for career in ranked_careers:
        domain_key = career["domain"]

        if domain_key in used_domains:
            continue

        top_three.append(career)
        used_domains.add(domain_key)

        if len(top_three) == 3:
            break

    # Himoya tekshiruvi
    if not top_three:
        return templates.TemplateResponse(
            request=request,
            name="test.html",
            context={
                "questions": QUESTIONS,
                "error": (
                    "Natijani hisoblab bo‘lmadi. "
                    "Testni qayta bajaring."
                ),
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    highest_score = max(
        top_three[0]["score"],
        1,
    )

    # O‘rin va foizni hisoblash
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

    # Natijani result.html sahifasiga yuborish
    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "top_three": top_three,
            "best": top_three[0],
            "career_count": len(CAREERS),
            "question_count": len(QUESTIONS),
        },
    )


@app.get("/health")
async def health_check():
    """
    Railway dastur ishlayotganini
    tekshirishi uchun health endpoint.
    """

