"""Lab 8, steps 8-10: exercise the quiz API from an external HTTP client.

It talks to the real server (runserver) with requests and token authentication.
The base URL and the token come from environment variables, never from the code:

    $env:QUIZ_BASE_URL = "http://127.0.0.1:8000"
    $env:QUIZ_TOKEN = "<token of profe from manage.py drf_create_token profe>"
    .\\.venv\\Scripts\\python.exe tools\\lab08_http_client.py

It only deletes the records it creates. The sanitized requests and responses
(without the Authorization header) are saved in entregable/evidencias/lab08/.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime

import requests

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "entregable" / "evidencias" / "lab08"
BASE = os.environ.get("QUIZ_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
TOKEN = os.environ.get("QUIZ_TOKEN")
if not TOKEN:
    sys.exit("Define QUIZ_TOKEN con el token de profe (drf_create_token profe).")

session = requests.Session()
session.headers.update({
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json",
})

log = []
failures = []


def call(section, description, method, path, body=None, expected=200):
    """Send one request, keep a sanitized record and compare the status code."""
    response = session.request(method, BASE + path, json=body)
    if response.content:
        data = response.json()
    else:
        data = "(sin cuerpo)"
    ok = response.status_code == expected
    log.append({
        "seccion": section,
        "descripcion": description,
        "metodo": method,
        "url": path,
        "cuerpo_enviado": body,
        "codigo_esperado": expected,
        "codigo_recibido": response.status_code,
        "correcto": ok,
        "respuesta": data,
    })
    mark = "OK " if ok else "ERR"
    print(f"{mark} {method:6} {path:45} {response.status_code} (esperado {expected})")
    if not ok:
        failures.append(f"{method} {path}: {response.status_code} != {expected}")
    return data


def check(description, condition):
    """Record a verification about the content of the responses."""
    log.append({"seccion": "verificacion", "descripcion": description,
                "correcto": bool(condition)})
    print(("OK " if condition else "ERR") + " " + description)
    if not condition:
        failures.append(description)


# 1. Exams: list, create, detail, PUT, PATCH (the DELETE runs at the end).
s = "examenes"
call(s, "Listar exámenes", "GET", "/api/exams/")
exam = call(s, "Crear examen de prueba", "POST", "/api/exams/",
            {"title": "Examen cliente HTTP LAB08"}, 201)
exam_id = exam["id"]
exam_url = f"/api/exams/{exam_id}/"
call(s, "Detalle del examen creado", "GET", exam_url)
call(s, "Reemplazar examen (PUT)", "PUT", exam_url,
     {"title": "Examen cliente HTTP LAB08 (PUT)"})
call(s, "Modificar examen (PATCH)", "PATCH", exam_url,
     {"title": "Examen cliente HTTP LAB08 (PATCH)"})

# 2. Questions: the exam travels as its ID and the choices travel nested.
s = "preguntas"
call(s, "Listar preguntas", "GET", "/api/questions/")
question = call(s, "Crear pregunta con dos opciones", "POST", "/api/questions/", {
    "exam": exam_id,
    "text": "¿Qué código devuelve un POST que crea un recurso?",
    "choices": [
        {"text": "201 Created", "is_correct": True},
        {"text": "404 Not Found", "is_correct": False},
    ],
}, 201)
question_id = question["id"]
question_url = f"/api/questions/{question_id}/"
call(s, "Detalle de la pregunta creada", "GET", question_url)
call(s, "Reemplazar pregunta y opciones (PUT)", "PUT", question_url, {
    "exam": exam_id,
    "text": "¿Qué código devuelve un DELETE correcto?",
    "choices": [
        {"text": "204 No Content", "is_correct": True},
        {"text": "200 OK con el objeto", "is_correct": False},
        {"text": "500 Internal Server Error", "is_correct": False},
    ],
})
patched = call(s, "Modificar solo el texto (PATCH)", "PATCH", question_url,
               {"text": "¿Qué código devuelve un DELETE correcto? (PATCH)"})
check("El PATCH sin choices conserva las 3 opciones", len(patched["choices"]) == 3)

# 3. Choices: an extra distractor that can be deleted with 204.
s = "opciones"
call(s, "Listar opciones", "GET", "/api/choices/")
choice = call(s, "Crear distractor", "POST", "/api/choices/",
              {"question": question_id, "text": "302 Found", "is_correct": False}, 201)
choice_url = f"/api/choices/{choice['id']}/"
call(s, "Detalle del distractor", "GET", choice_url)
call(s, "Reemplazar distractor (PUT)", "PUT", choice_url,
     {"question": question_id, "text": "302 Found (PUT)", "is_correct": False})
call(s, "Modificar distractor (PATCH)", "PATCH", choice_url,
     {"text": "302 Found (PATCH)"})
call(s, "Eliminar distractor", "DELETE", choice_url, expected=204)
call(s, "Detalle del distractor eliminado", "GET", choice_url, expected=404)

s = "preguntas"
call(s, "Eliminar la pregunta de prueba", "DELETE", question_url, expected=204)
call(s, "Detalle de la pregunta eliminada", "GET", question_url, expected=404)

# 4. Step 9: invalid POST /api/questions/ requests must return 400.
s = "errores"
before = call(s, "Preguntas del examen antes de los errores", "GET",
              f"/api/questions/?exam={exam_id}")["count"]
two_choices = [{"text": "A", "is_correct": True}, {"text": "B", "is_correct": False}]
call(s, "a) Falta text", "POST", "/api/questions/",
     {"exam": exam_id, "choices": two_choices}, 400)
call(s, "b) exam con tipo incorrecto", "POST", "/api/questions/",
     {"exam": "no-es-un-numero", "text": "Tipo incorrecto", "choices": two_choices}, 400)
call(s, "c) choices sin opción correcta", "POST", "/api/questions/", {
    "exam": exam_id, "text": "Cero correctas",
    "choices": [{"text": "A", "is_correct": False}, {"text": "B", "is_correct": False}],
}, 400)
call(s, "c) choices con dos opciones correctas", "POST", "/api/questions/", {
    "exam": exam_id, "text": "Dos correctas",
    "choices": [{"text": "A", "is_correct": True}, {"text": "B", "is_correct": True}],
}, 400)
after = call(s, "Preguntas del examen después de los errores", "GET",
             f"/api/questions/?exam={exam_id}")["count"]
check("Las peticiones inválidas no crearon preguntas", before == after == 0)

# 5. Step 10: filters, search and pagination.
s = "filtros"
for number in range(1, 7):
    call(s, f"Pregunta temporal {number}", "POST", "/api/questions/", {
        "exam": exam_id,
        "text": f"Pregunta temporal {number} sobre paginación",
        "choices": [{"text": "Sí", "is_correct": True}, {"text": "No", "is_correct": False}],
    }, 201)

exams = call(s, "Exámenes para descubrir IDs", "GET", "/api/exams/")["results"]
orm_id = next(e["id"] for e in exams if e["title"] == "Django · ORM")

by_exam = call(s, "Filtro por examen", "GET", f"/api/questions/?exam={orm_id}")
check("?exam devuelve solo preguntas de ese examen",
      by_exam["count"] > 0 and all(q["exam"] == orm_id for q in by_exam["results"]))

found = call(s, "Búsqueda por texto", "GET", "/api/questions/?search=prefetch_related")
check("?search devuelve preguntas que contienen el texto",
      found["count"] > 0
      and all("prefetch_related" in q["text"].lower() for q in found["results"]))

both = call(s, "Filtro y búsqueda combinados", "GET",
            f"/api/questions/?exam={orm_id}&search=related")
check("?exam + ?search cumple ambas condiciones",
      both["count"] > 0 and all(q["exam"] == orm_id and "related" in q["text"].lower()
                                for q in both["results"]))

page1 = call(s, "Página 1 del examen de prueba", "GET",
             f"/api/questions/?exam={exam_id}&page=1")
page2 = call(s, "Página 2 del examen de prueba", "GET",
             f"/api/questions/?exam={exam_id}&page=2")
ids1 = [q["id"] for q in page1["results"]]
ids2 = [q["id"] for q in page2["results"]]
check("count = 6, página 1 con 5 y página 2 con 1",
      page1["count"] == 6 and len(ids1) == 5 and len(ids2) == 1)
check("Página 1: previous null y next a la página 2",
      page1["previous"] is None and "page=2" in (page1["next"] or ""))
check("Página 2: next null y previous a la página 1",
      page2["next"] is None and page2["previous"] is not None)
check("Sin IDs repetidos entre páginas", not set(ids1) & set(ids2))

general1 = call(s, "Página 1 sin filtros", "GET", "/api/questions/?page=1")
general2 = call(s, "Página 2 sin filtros", "GET", "/api/questions/?page=2")
check("Sin filtros: máximo 5 por página y sin repetir IDs",
      len(general1["results"]) <= 5 and len(general2["results"]) <= 5
      and not {q["id"] for q in general1["results"]} & {q["id"] for q in general2["results"]})

call(s, "exam mal formado", "GET", "/api/questions/?exam=abc", expected=400)
call(s, "Página inexistente", "GET", "/api/questions/?page=999", expected=404)

# 6. Cleanup: deleting the test exam also deletes its questions (CASCADE).
s = "examenes"
call(s, "Eliminar examen de prueba", "DELETE", exam_url, expected=204)
call(s, "Detalle del examen eliminado", "GET", exam_url, expected=404)
call(s, "Preguntas del examen eliminado", "GET", f"/api/questions/?exam={exam_id}")

version = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                         capture_output=True, text=True).stdout.strip()
OUTPUT.mkdir(parents=True, exist_ok=True)
result = {
    "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "version_proyecto": version,
    "url_base": BASE,
    "autenticacion": "Authorization: Token <oculto>",
    "fallos": failures,
    "peticiones": log,
}
(OUTPUT / "cliente_http.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"\n{len(log)} registros, {len(failures)} fallos")
sys.exit(1 if failures else 0)
