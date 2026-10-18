# LAB08 — API REST con Django REST Framework

Repositorio del equipo: [leonel-m4/Desarrollo-de-Aplicaciones-Empresariales-LAB08](https://github.com/leonel-m4/Desarrollo-de-Aplicaciones-Empresariales-LAB08).

## Integrantes y reparto

| Integrante | Pasos | Trabajo |
| --- | --- | --- |
| Leonel Mathias Retamozo De la Cruz | 1–6 y 10 | Modelos, serializadores, `ModelViewSet`, enrutador, permisos, filtros, búsqueda, paginación y pruebas del backend ([docs/api-cuestionarios.md](../docs/api-cuestionarios.md)). |
| Karim Sovero | 7, 8, 9, 11, 12 y comprobación del 10 | Pruebas HTTP en la API navegable y con cliente externo, errores, filtros y paginación, tabla de la API, evidencias y verificación final. |

## Fecha y versión

- Ejecución: **18/10/2026**, entre las 14:05 y las 14:08 (hora de Perú).
- Versión del proyecto usada: commit `50eae7f` de la rama `main`.
- Entorno: Windows 11, Python 3.14.0, Django 6.1.2, Django REST Framework 3.18.3,
  drf-spectacular 0.30.0 y requests 2.34.2.
- Servidor real: `runserver 127.0.0.1:8000 --noreload`. Ninguna comprobación usa el ORM ni el `APIClient` de DRF.

## Preparación del entorno

Desde PowerShell, en la raíz del proyecto:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_quiz        # solo en una base de práctica: borra los exámenes
.\.venv\Scripts\python.exe manage.py changepassword profe
.\.venv\Scripts\python.exe manage.py drf_create_token profe
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000 --noreload
```

`seed_quiz` dejó 2 exámenes, 8 preguntas y 4 opciones por pregunta. Al usuario `profe` (`is_staff=True`) se le puso una contraseña local para iniciar sesión en el navegador. La contraseña y el token **no** se guardan en el repositorio ni aparecen en las capturas.

Para repetir las pruebas del cliente externo, en otra terminal:

```powershell
$env:QUIZ_BASE_URL = "http://127.0.0.1:8000"
$env:QUIZ_TOKEN = "<token de profe>"
.\.venv\Scripts\python.exe tools\lab08_http_client.py
```

El script [tools/lab08_http_client.py](../tools/lab08_http_client.py) usa `requests` con `Authorization: Token <token>` y JSON. Descubre los IDs a partir de las respuestas y solo borra lo que crea. Guarda las peticiones y respuestas, sin la cabecera del token, en `entregable/evidencias/lab08/cliente_http.json`. Termina con código 0 si todos los códigos coinciden con los esperados.

## Tabla de la API

Todas las rutas requieren autenticación (token o sesión). Los IDs de la tabla son los que devolvió el servidor en la ejecución del cliente externo. Las listas devuelven `count`, `next`, `previous` y `results`, con un máximo de 5 elementos.

### Exámenes

| Dirección | Método | Cuerpo de ejemplo | Código | Respuesta esperada |
| --- | --- | --- | --- | --- |
| `/api/exams/` | GET | — | 200 | Lista paginada: `{"count": 2, "next": null, "previous": null, "results": [{"id": 1, "title": "Django · ORM", "created_at": "...", "question_count": 4}, ...]}` |
| `/api/exams/` | POST | `{"title": "Examen cliente HTTP LAB08"}` | 201 | `{"id": 5, "title": "Examen cliente HTTP LAB08", "created_at": "...", "question_count": 0}` |
| `/api/exams/{id}/` | GET | — | 200 | El examen con `id`, `title`, `created_at` y `question_count` |
| `/api/exams/{id}/` | PUT | `{"title": "Examen cliente HTTP LAB08 (PUT)"}` | 200 | El examen con el título reemplazado |
| `/api/exams/{id}/` | PATCH | `{"title": "Examen cliente HTTP LAB08 (PATCH)"}` | 200 | El examen con el título modificado |
| `/api/exams/{id}/` | DELETE | — | 204 | Sin cuerpo. También borra sus preguntas y opciones (`CASCADE`); el GET posterior da 404 |

### Preguntas

| Dirección | Método | Cuerpo de ejemplo | Código | Respuesta esperada |
| --- | --- | --- | --- | --- |
| `/api/questions/` | GET | — | 200 | Lista paginada de preguntas con sus `choices` anidadas (`count: 8` con los datos iniciales) |
| `/api/questions/` | POST | `{"exam": 5, "text": "¿Qué código devuelve un POST que crea un recurso?", "choices": [{"text": "201 Created", "is_correct": true}, {"text": "404 Not Found", "is_correct": false}]}` | 201 | `{"id": 11, "exam": 5, "text": "...", "choices": [{"id": 45, "text": "201 Created", "is_correct": true}, {"id": 46, ...}], "created_at": "..."}` |
| `/api/questions/{id}/` | GET | — | 200 | La pregunta con `exam` como ID y sus opciones |
| `/api/questions/{id}/` | PUT | `{"exam": 5, "text": "¿Qué código devuelve un DELETE correcto?", "choices": [{"text": "204 No Content", "is_correct": true}, {"text": "200 OK con el objeto", "is_correct": false}, {"text": "500 Internal Server Error", "is_correct": false}]}` | 200 | La pregunta con el texto nuevo y las 3 opciones nuevas (IDs 47, 48 y 49: la lista se reemplaza) |
| `/api/questions/{id}/` | PATCH | `{"text": "¿Qué código devuelve un DELETE correcto? (PATCH)"}` | 200 | Texto cambiado; sin `choices` se conservan las 3 opciones |
| `/api/questions/{id}/` | DELETE | — | 204 | Sin cuerpo. También borra sus opciones; el GET posterior da 404 |

### Opciones

| Dirección | Método | Cuerpo de ejemplo | Código | Respuesta esperada |
| --- | --- | --- | --- | --- |
| `/api/choices/` | GET | — | 200 | Lista paginada de opciones con `id`, `question`, `text` e `is_correct` |
| `/api/choices/` | POST | `{"question": 11, "text": "302 Found", "is_correct": false}` | 201 | `{"id": 50, "question": 11, "text": "302 Found", "is_correct": false}` |
| `/api/choices/{id}/` | GET | — | 200 | La opción creada |
| `/api/choices/{id}/` | PUT | `{"question": 11, "text": "302 Found (PUT)", "is_correct": false}` | 200 | La opción reemplazada |
| `/api/choices/{id}/` | PATCH | `{"text": "302 Found (PATCH)"}` | 200 | La opción con el texto modificado |
| `/api/choices/{id}/` | DELETE | — | 204 | Sin cuerpo; el GET posterior da 404. Solo se borra un distractor: quitar la única correcta o dejar menos de 2 opciones devuelve 400 |

### Errores, filtros y paginación

| Dirección | Método | Cuerpo / parámetros | Código | Respuesta recibida |
| --- | --- | --- | --- | --- |
| `/api/questions/` | POST | Sin `text`: `{"exam": 5, "choices": [{"text": "A", "is_correct": true}, {"text": "B", "is_correct": false}]}` | 400 | `{"text": ["Este campo es requerido."]}` |
| `/api/questions/` | POST | `{"exam": "no-es-un-numero", "text": "Tipo incorrecto", "choices": [...]}` | 400 | `{"exam": ["Tipo incorrecto. Se esperaba valor de clave primaria y se recibió str."]}` |
| `/api/questions/` | POST | `choices` con 0 correctas (`A` y `B` en `false`) | 400 | `{"choices": ["Debe haber exactamente una opción correcta."]}` |
| `/api/questions/` | POST | `choices` con 2 correctas (`A` y `B` en `true`) | 400 | `{"choices": ["Debe haber exactamente una opción correcta."]}` |
| `/api/questions/?exam=1` | GET | Filtro por examen | 200 | Solo preguntas con `"exam": 1` |
| `/api/questions/?search=prefetch_related` | GET | Búsqueda en `text` | 200 | Preguntas cuyo texto contiene `prefetch_related` |
| `/api/questions/?exam=1&search=related` | GET | Filtro y búsqueda | 200 | Preguntas del examen 1 que contienen `related` |
| `/api/questions/?exam=5&page=1` | GET | Página 1 | 200 | `count: 6`, 5 resultados, `previous: null`, `next` a `page=2` |
| `/api/questions/?exam=5&page=2` | GET | Página 2 | 200 | 1 resultado, `next: null`, `previous` a la página 1 |
| `/api/questions/?exam=abc` | GET | `exam` mal formado | 400 | `{"exam": ["Introduzca un número entero válido."]}` |
| `/api/questions/?page=999` | GET | Página inexistente | 404 | `{"detail": "Página inválida."}` |

## Cómo funciona la API

- **Examen por ID:** en una pregunta, `exam` viaja como el ID entero del examen, no como un objeto. Un valor que no es un ID devuelve 400.
- **Opciones anidadas:** `QuestionSerializer` recibe y devuelve `choices` dentro de la pregunta, sin repetir `question`. Un POST crea la pregunta y sus opciones a la vez. En PUT o PATCH, enviar `choices` reemplaza la lista completa (los IDs cambian). Un PATCH sin `choices` las conserva. En `/api/choices/`, en cambio, `question` se envía como ID.
- **Campos de solo lectura:** `id` en los tres recursos. `created_at` y `question_count` en exámenes, y `created_at` en preguntas. Aparecen en las respuestas, pero el cliente no puede escribirlos.
- **Validación:** una pregunta necesita al menos 2 opciones y exactamente 1 correcta (`quiz/validators.py`). Lo mismo se comprueba al crear, editar o borrar una opción suelta. Una petición inválida devuelve 400 y no guarda nada.
- **Permisos:** `IsAuthenticated` y `AgentPermission`. Un usuario `is_staff` puede hacer todo. El grupo `agente` puede leer, crear y modificar, pero no eliminar. El resto de usuarios autenticados solo lee. Sin credenciales responde 401 (el registro del servidor muestra `GET /api/` → 401 antes de iniciar sesión) y sin permiso, 403. Los clientes externos usan token; la API navegable usa sesión con CSRF.
- **Filtros y búsqueda:** `?exam=<id>` filtra por examen y exige un entero positivo (si no, 400). `?search=<texto>` busca en `text` sin distinguir mayúsculas. Se pueden combinar.
- **Paginación:** `PageNumberPagination` con 5 elementos por página, ordenados por ID para que las páginas sean estables. Una página que no existe devuelve 404.

## Resultados

### Paso 7 — API navegable (comprobado)

Se inició sesión como `profe` en `/api-auth/login/` y se usaron los formularios **Raw data** con `application/json` en un Chrome con perfil temporal y sin traducción. El Chrome habitual traducía la página y cambiaba el texto, así que no se usó. Las 26 capturas están en [evidencias/lab08/navegador/](evidencias/lab08/navegador/) y el registro de cada petición en [navegador_registro.json](evidencias/lab08/navegador_registro.json).

| # | Método | URL | Código | Captura |
| --- | --- | --- | --- | --- |
| 1 | POST | `/api-auth/login/` | 302 (registro del servidor) | [01_login.png](evidencias/lab08/navegador/01_login.png) (contraseña oculta) |
| 2 | GET | `/api/` | 200 | [02_get.png](evidencias/lab08/navegador/02_get.png) |
| 3–8 | GET, POST, GET, PUT, PATCH | `/api/exams/` y `/api/exams/4/` | 200, 201, 200, 200, 200 | [03](evidencias/lab08/navegador/03_get.png), [04 (cuerpo)](evidencias/lab08/navegador/04_post_form.png), [05](evidencias/lab08/navegador/05_post.png), [06](evidencias/lab08/navegador/06_get.png), [07](evidencias/lab08/navegador/07_put.png), [08](evidencias/lab08/navegador/08_patch.png) |
| 9–14 | GET, POST, GET, PUT, PATCH | `/api/questions/` y `/api/questions/10/` | 200, 201, 200, 200, 200 | [09](evidencias/lab08/navegador/09_get.png), [10 (cuerpo)](evidencias/lab08/navegador/10_post_form.png), [11](evidencias/lab08/navegador/11_post.png), [12](evidencias/lab08/navegador/12_get.png), [13](evidencias/lab08/navegador/13_put.png), [14](evidencias/lab08/navegador/14_patch.png) |
| 15–20 | GET, POST, GET, PUT, PATCH | `/api/choices/` y `/api/choices/44/` | 200, 201, 200, 200, 200 | [15](evidencias/lab08/navegador/15_get.png), [16 (cuerpo)](evidencias/lab08/navegador/16_post_form.png), [17](evidencias/lab08/navegador/17_post.png), [18](evidencias/lab08/navegador/18_get.png), [19](evidencias/lab08/navegador/19_put.png), [20](evidencias/lab08/navegador/20_patch.png) |
| 21–22 | DELETE, GET | `/api/choices/44/` | 204 sin cuerpo, 404 | [21](evidencias/lab08/navegador/21_delete.png), [22](evidencias/lab08/navegador/22_get.png) |
| 23–24 | DELETE, GET | `/api/questions/10/` | 204 sin cuerpo, 404 | [23](evidencias/lab08/navegador/23_delete.png), [24](evidencias/lab08/navegador/24_get.png) |
| 25–26 | DELETE, GET | `/api/exams/4/` | 204 sin cuerpo, 404 | [25](evidencias/lab08/navegador/25_delete.png), [26](evidencias/lab08/navegador/26_get.png) |

El registro del servidor de esta pasada está en [servidor_runserver.log](evidencias/lab08/servidor_runserver.log). Hubo una pasada anterior que se descartó porque el script de capturas tenía mal la codificación de las tildes. Sus registros de prueba (examen 3, pregunta 9 y opción 38) se eliminaron en esa misma pasada.

### Paso 8 — Cliente HTTP externo (comprobado)

[tools/lab08_http_client.py](../tools/lab08_http_client.py) hizo **54 registros con 0 fallos**: [salida de consola](evidencias/lab08/cliente_http_salida.txt) y [peticiones y respuestas](evidencias/lab08/cliente_http.json).

- Exámenes: GET 200, POST 201 (id 5), GET 200, PUT 200, PATCH 200 y, al final, DELETE 204 sin cuerpo y GET 404.
- Preguntas: GET 200, POST 201 (id 11, con 2 opciones), GET 200, PUT 200 (3 opciones nuevas), PATCH 200 (conserva las 3), DELETE 204 sin cuerpo y GET 404.
- Opciones: GET 200, POST 201 de un distractor `is_correct: false` (id 50), GET 200, PUT 200, PATCH 200, DELETE 204 sin cuerpo y GET 404.

Ambas formas de acceso dan los mismos códigos. Con sesión (navegador) y con token (cliente externo), GET da 200, POST 201, PUT/PATCH 200, DELETE 204 sin cuerpo y el GET del objeto eliminado, 404. Solo se borraron los registros creados en las pruebas: los 2 exámenes y 8 preguntas iniciales siguen igual.

### Paso 9 — Errores (comprobado)

Los cuatro POST inválidos a `/api/questions/` devolvieron 400 con los mensajes de la tabla de errores. El examen de prueba tenía `count: 0` antes y después de los errores, así que ninguna petición inválida creó preguntas.

### Paso 10 — Filtros, búsqueda y paginación (comprobado)

Se crearon 6 preguntas temporales en el examen de prueba (id 5). Se comprobó lo siguiente:

- `?exam=1`: solo hay preguntas de ese examen.
- `?search=prefetch_related`: todas las preguntas contienen el texto.
- `?exam=1&search=related`: se cumplen ambas condiciones.
- `?exam=5&page=1`: `count` 6 y 5 resultados.
- `?exam=5&page=2`: 1 resultado.
- `next` y `previous` son correctos y no se repiten IDs entre páginas. Sin filtros, `?page=1` y `?page=2` también tienen como máximo 5 resultados sin repetir.
- `?exam=abc`: 400.
- `?page=999`: 404.

Al eliminar el examen de prueba, `?exam=5` devolvió una lista vacía: el borrado en cascada funcionó.

### Paso 12 — Verificación

- `python manage.py check`: sin problemas ([check.txt](evidencias/lab08/check.txt)).
- `python manage.py test quiz.tests.test_api quiz.tests.test_lab08 quiz.tests.test_permissions quiz.tests.test_agent`: **65 pruebas, OK** ([pruebas_backend.txt](evidencias/lab08/pruebas_backend.txt)).
- `git diff --check`: sin errores de espacios.
- En el commit no hay tokens, contraseñas, `db.sqlite3`, `.venv` ni archivos temporales.

## Pendiente

- Publicar en GitHub: Karim hará el push del commit.
- Pendiente: Karim debe subir entregable/LAB08.md (o el formato solicitado por el docente) al campus virtual.
