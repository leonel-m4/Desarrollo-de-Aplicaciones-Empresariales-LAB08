# Lab 8: implementación de la API de cuestionarios

Este documento describe los pasos **1–6 y 10**, correspondientes a la implementación.
Las pruebas manuales por HTTP, sus evidencias y la tabla de entrega corresponden
al segundo integrante y deben registrarse en `entregable/LAB08.md`.

## Preparación

Desde PowerShell, en la raíz del proyecto:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_quiz
.\.venv\Scripts\python.exe manage.py changepassword profe
.\.venv\Scripts\python.exe manage.py runserver
```

**Atención:** `seed_quiz` reconstruye los datos de cuestionarios: elimina los
exámenes anteriores y carga dos exámenes con ocho preguntas y cuatro opciones por
pregunta. Úsalo solo en la base de práctica o cuando quieras reiniciarla. No es
necesario repetirlo para arrancar el servidor ni para recuperar un token.

El usuario `profe` se crea sin contraseña utilizable. `changepassword profe`
permite elegir una contraseña local para entrar desde el navegador, sin guardar
credenciales en el código. Si ya tiene contraseña, no necesitas cambiarla.

## Configuración y autenticación

- `rest_framework` y `quiz` están en `INSTALLED_APPS`.
- `PageNumberPagination` entrega cinco resultados por página en los tres recursos.
- Los permisos de partida son `IsAuthenticated` y `AgentPermission`.
- El usuario con `is_staff=True` puede realizar todas las operaciones estándar.
- El grupo `agente` puede leer, crear y modificar, pero no eliminar.
- Los demás usuarios autenticados solo pueden leer.
- Sin autenticación se devuelve `401`; una operación sin permiso devuelve `403`.

Para la API navegable abre <http://127.0.0.1:8000/api/> e inicia sesión mediante
el enlace **Log in**. Las sesiones usan protección CSRF. En las preguntas puedes
utilizar la pestaña **Raw data** con `application/json` para enviar las opciones
anidadas.

Los clientes externos conservan la autenticación por token:

```http
Authorization: Token <token-del-usuario>
Content-Type: application/json
Accept: application/json
```

Puedes consultar o crear el token de `profe` sin reiniciar los datos:

```powershell
.\.venv\Scripts\python.exe manage.py drf_create_token profe
```

No incluyas tokens, contraseñas ni el archivo `db.sqlite3` en Git o en las capturas.

## Recursos y serializadores

`DefaultRouter` registra tres `ModelViewSet`, incluidos desde `config/urls.py`:

- Exámenes: `/api/exams/` y `/api/exams/{id}/`.
- Preguntas: `/api/questions/` y `/api/questions/{id}/`.
- Opciones: `/api/choices/` y `/api/choices/{id}/`.

Cada colección admite `GET` y `POST`; cada detalle admite `GET`, `PUT`, `PATCH`
y `DELETE`. Los serializadores públicos derivan de `ModelSerializer`:

- `ExamSerializer`: `id`, `title`, `created_at`, `question_count`.
  Solo lectura: `id`, `created_at` y `question_count`.
- `QuestionSerializer`: `id`, `exam`, `text`, `choices`, `created_at`.
  Solo lectura: `id` y `created_at`.
- `ChoiceSerializer`: `id`, `question`, `text`, `is_correct`.
  Solo lectura: `id`.

### Decisión sobre las relaciones

El examen de una pregunta viaja como identificador entero (`exam`), no como un
objeto de examen. Las opciones viajan anidadas con `NestedChoiceSerializer`, sin
repetir `question` dentro de cada opción. Así, una sola petición crea la pregunta
y sus opciones de forma atómica:

```json
{
  "exam": 1,
  "text": "¿Qué es una API REST?",
  "choices": [
    {"text": "Un estilo de arquitectura sobre HTTP", "is_correct": true},
    {"text": "Un lenguaje de programación", "is_correct": false}
  ]
}
```

Sustituye `exam: 1` por un ID obtenido de `/api/exams/`: los identificadores pueden
cambiar si reinicias los datos.

En `/api/choices/`, la relación `question` sí se envía explícitamente como ID:

```json
{
  "question": 1,
  "text": "Otro distractor",
  "is_correct": false
}
```

### Validación y modificaciones

- Una pregunta necesita al menos dos opciones y **exactamente una correcta**.
  En caso contrario, la petición devuelve `400` con el motivo en `choices`.
- Un `PATCH` sin `choices` mantiene las opciones existentes.
- Si se envía `choices`, se reemplaza **toda** la lista, también en `PATCH`.
  Cada opción debe incluir `text`; los IDs de las opciones reemplazadas cambian.
- Las opciones omitidas no se conservan ni se combinan con la lista nueva.
- Crear, editar, mover o eliminar una opción independiente tampoco puede dejar
  a ninguna pregunta con menos de dos opciones o sin exactamente una correcta.
  Una modificación inválida devuelve `400` y no se guarda.
- Para cambiar cuál es la respuesta correcta, utiliza un `PATCH` de la pregunta
  con la lista completa de opciones válida. Así no hay un estado intermedio
  con cero o dos respuestas correctas.
- Eliminar un examen elimina sus preguntas y opciones; eliminar una pregunta
  elimina sus opciones, conforme a las relaciones `CASCADE` del modelo.

Para comprobar un ciclo CRUD de opciones con eliminación `204`, crea un
distractor (`is_correct: false`) en una pregunta válida y luego elimínalo.
Eliminar directamente la única opción correcta devuelve `400` por diseño.

## Filtros, búsqueda y paginación

Los parámetros pueden combinarse en `/api/questions/`:

```text
/api/questions/?exam=1
/api/questions/?search=prefetch_related
/api/questions/?page=2
/api/questions/?exam=1&search=related&page=1
```

`exam` debe ser un entero positivo; un valor mal formado devuelve `400` en lugar
de ignorar el filtro. Un ID válido sin preguntas produce una lista vacía.
`search` busca en `text` sin distinguir mayúsculas de minúsculas. Las páginas
devuelven `count`, `next`, `previous` y `results`, con un máximo de cinco elementos.
Una página inexistente devuelve `404`. El orden por ID mantiene la paginación
estable entre peticiones mientras los datos no cambien.

El esquema OpenAPI está en `/api/schema/` y la documentación interactiva en
`/api/docs/`. Estos documentos se generan a partir de las vistas y serializadores.

## Verificación automatizada de la implementación

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test quiz.tests.test_api quiz.tests.test_lab08 quiz.tests.test_permissions quiz.tests.test_agent
```

Estas comprobaciones no sustituyen las pruebas manuales ni la tabla que debe
preparar el segundo integrante. `quizctl.py` pertenece al laboratorio extra del
cliente de consola y conserva sus dos ejercicios pendientes; no se necesita para
probar esta API con Postman, Insomnia o un cliente HTTP equivalente.
