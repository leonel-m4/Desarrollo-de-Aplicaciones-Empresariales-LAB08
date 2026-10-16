# Lab 8 — API REST de cuestionarios y extra headless

Repositorio del **Laboratorio 8** de Desarrollo de Aplicaciones Empresariales (DAE):
API de exámenes, preguntas y opciones con Django REST Framework.
También contiene el laboratorio **extra** de contrato OpenAPI, cliente de consola
y frontera de un agente de IA. Ese extra no es la parte pendiente de Karim.

La guía del laboratorio (con su rúbrica) está en el campus virtual; aquí está el código.

## Lab 8 — API REST de cuestionarios

La implementación de los pasos **1–6 y 10** publica exámenes, preguntas y opciones
en `/api/exams/`, `/api/questions/` y `/api/choices/`. Incluye validación, filtros,
paginación y acceso desde la API navegable con inicio de sesión.

Consulta [la configuración y las decisiones sobre relaciones](docs/api-cuestionarios.md).
Las pruebas HTTP y la tabla para el campus quedan a cargo de **Karim**, según el
bloque siguiente. La implementación tiene **65 pruebas backend aprobadas**.

## Parte de Karim — instrucciones para su IA

**Pendiente:** pasos **7, 8, 9, 11 y 12**, más la comprobación del paso **10**.
Son las pruebas por HTTP, las evidencias y el entregable; no hay que rehacer la API.

Karim debe abrir este repositorio en su asistente con acceso a terminal y pegar
el siguiente bloque. Es una instrucción de trabajo, no un script que se ejecute
por el simple hecho de abrir el README.

```text
Actúa como el asistente de Karim y completa su parte del Laboratorio 8 en este
repositorio: https://github.com/leonel-m4/Desarrollo-de-Aplicaciones-Empresariales-LAB08

OBJETIVO Y LÍMITES
- Ejecuta el trabajo, no te limites a proponer un plan o escribir una plantilla.
- La implementación de los pasos 1–6 y 10 ya está hecha. Lee primero
  docs/api-cuestionarios.md y los archivos de quiz/ y config/.
- Conserva el código y los cambios locales existentes. Solo corrige el backend
  si encuentras un fallo real, lo reproduces y añades una prueba de regresión.
- No trabajes en blog/, movies/, news/ ni en el entregable del LAB07.
- Los TODO de quizctl.py son del extra headless, no de tu parte del Lab 8.
  No necesitas completarlos para verificar la API desde un cliente externo.

1. PREPARAR EL ENTORNO
- Revisa git status y trabaja sobre la versión actual de este repositorio.
- Crea un entorno virtual si no existe, instala requirements.txt y ejecuta
  manage.py migrate con el Python del entorno. Consulta los comandos Windows
  de docs/api-cuestionarios.md o adapta el ejecutable a tu sistema operativo.
- La base db.sqlite3 y el entorno virtual no se descargan de GitHub.
- seed_quiz BORRA los exámenes anteriores. Úsalo solo en una base de práctica
  nueva o con autorización para reiniciarla. No destruyas datos del equipo.
- Necesitas un usuario con is_staff=True. seed_quiz crea profe sin contraseña
  utilizable; configura una contraseña local para la sesión del navegador o
  solicita al usuario ese paso. No cambies contraseñas existentes sin permiso.
- Para el cliente externo obtén un token local con
  python manage.py drf_create_token profe. No lo guardes en archivos versionados.
- Arranca el servidor real en 127.0.0.1:8000, preferiblemente con --noreload.
  No sustituyas las pruebas HTTP por llamadas al ORM o por el APIClient de DRF.

2. API NAVEGABLE: PASO 7
- Abre http://127.0.0.1:8000/api/ e inicia sesión desde /api-auth/login/.
- Recorre los tres recursos: /api/exams/, /api/questions/ y /api/choices/.
- Para cada uno comprueba listar, detalle, crear, modificar parcialmente y
  eliminar. Comprueba también PUT, porque está expuesto por el enrutador.
- Usa Raw data con application/json cuando envíes opciones anidadas.
- Anota método, URL, cuerpo enviado, código y respuesta reales; captura las
  pantallas relevantes sin mostrar contraseñas, cookies ni tokens.
- Si no tienes herramientas para usar un navegador, deja esa verificación
  marcada como pendiente e indica qué debe hacer Karim. No inventes capturas
  ni presentes las pruebas del cliente externo como si fueran del navegador.

3. CLIENTE HTTP EXTERNO: PASO 8
- Repite las operaciones contra el servidor real con Postman, Insomnia, curl
  o un script Python requests. Envía JSON y Authorization: Token <token>.
- Entrega una colección importable o un script reproducible; usa variables
  para la URL base y el token, nunca credenciales incluidas en el repositorio.
- Descubre los IDs a partir de las respuestas; no supongas que empiezan en 1.
- Crea un examen de prueba y una pregunta asociada con al menos dos opciones
  y exactamente una correcta. Para el CRUD de opciones crea un distractor
  adicional con is_correct=false; ese distractor sí puede eliminarse con 204.
- No borres la única opción correcta ni dejes menos de dos: devuelve 400 por
  diseño. Para cambiar la correcta, reemplaza choices desde la pregunta.
- Códigos esperados: GET 200, POST 201, PUT/PATCH 200, DELETE 204 sin cuerpo
  y GET del objeto eliminado 404. Contrasta ambas formas de acceso.
- Elimina únicamente los registros que hayas creado para estas comprobaciones.

4. ERRORES Y PARÁMETROS: PASOS 9 Y COMPROBACIÓN DEL 10
- Provoca y registra, al menos, estos errores con POST /api/questions/:
  a) Falta text: campo obligatorio ausente.
  b) exam="no-es-un-numero": tipo incorrecto.
  c) choices con cero o con dos opciones correctas: validación propia.
- Deben devolver 400. Guarda el mensaje exacto recibido y comprueba que la
  petición inválida no haya creado la pregunta.
- Comprueba ?exam=<id>, ?search=<texto> y ambos combinados; verifica que los
  resultados pertenecen al examen y contienen el texto buscado.
- Comprueba ?page=1 y ?page=2 con más de cinco preguntas: count, next,
  previous y results, máximo cinco por página y sin IDs repetidos entre páginas.
  Si necesitas datos, crea preguntas temporales sin reiniciar los existentes.
- Registra también un exam mal formado (400) y una página inexistente (404).

5. ARCHIVOS QUE DEBES ENTREGAR: PASO 11
- Crea entregable/LAB08.md, redactado en español, con:
  * Integrantes y reparto del trabajo; no inventes nombres o datos académicos.
  * Preparación del entorno y comandos para reproducir las comprobaciones.
  * Tabla completa de la API: recurso, dirección, método, cuerpo de ejemplo,
    código y respuesta esperada. Incluye colección y detalle de los tres
    recursos: GET de colección, POST, GET de detalle, PUT, PATCH y DELETE.
  * Explicación breve de exam por ID, opciones anidadas, campos de solo lectura,
    validación, permisos, filtros y paginación, acorde con el código real.
  * Resultados observados en navegador y cliente externo, errores y enlaces
    relativos a las evidencias; distingue lo comprobado de lo pendiente.
- Guarda las evidencias nuevas en entregable/evidencias/lab08/ sin sobrescribir
  las del LAB07. Incluye peticiones y respuestas sanitizadas, fecha de ejecución
  y versión del proyecto usada. Para DELETE 204 registra que no hay cuerpo.
- Guarda la colección HTTP en entregable/ o el script en tools/, documenta
  cómo ejecutarlo y evita tokens incluso en cabeceras o exportaciones.
- No fabriques respuestas, capturas o resultados: si una operación falla,
  conserva el resultado y explica el bloqueo. No marques tareas sin verificar.

6. VERIFICAR Y PUBLICAR: PASO 12
- Ejecuta con el Python del entorno:
  python manage.py check
  python manage.py test quiz.tests.test_api quiz.tests.test_lab08 quiz.tests.test_permissions quiz.tests.test_agent
  git diff --check
- El backend debe seguir pasando sus pruebas. No uses los TODO del cliente
  extra como motivo para reescribir la API ni para falsear un resultado.
- Revisa que la tabla coincida con las peticiones ejecutadas y que no haya
  secretos, db.sqlite3, entornos virtuales ni archivos temporales en el commit.
- Añade los archivos de tu trabajo, crea un commit descriptivo y súbelo al
  repositorio del equipo sin force push ni descartar cambios ajenos. Si falta
  autenticación, solicita autorización por el flujo normal de GitHub.
- Actualiza el estado de esta sección del README según lo que realmente quedó
  comprobado y entrega un resumen con archivos, pruebas, enlace y pendientes.
- Deja listo el entregable para el campus. La carga en Canvas requiere la
  sesión y confirmación de Karim; no la des por hecha. Si no puedes realizarla,
  indica claramente: "Pendiente: Karim debe subir entregable/LAB08.md (o el
  formato solicitado por el docente) al campus virtual".
```

### Estado de la parte de Karim

- [ ] API navegable: operaciones y capturas reales.
- [ ] Cliente HTTP externo: operaciones y colección o script reproducible.
- [ ] Tres errores, filtros, búsqueda y paginación: resultados registrados.
- [ ] `entregable/LAB08.md`: tabla completa y enlaces a evidencias sanitizadas.
- [ ] Cambios de Karim publicados en GitHub.
- [ ] Entregable subido al campus por Karim.

## Laboratorio extra — cliente de consola y frontera del agente

Las secciones siguientes corresponden al **extra headless**, no a nuevas tareas
de Karim. La puesta en marcha también sirve como referencia para la API base.

## Puesta en marcha

```bash
python -m venv .venv
.venv\Scripts\activate          # en Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_quiz      # datos fijos + los usuarios «profe» y «agente», con su token
python manage.py runserver      # déjalo corriendo; el resto va en OTRA terminal
```

`seed_quiz` imprime los dos tokens (copia las líneas de tu terminal). **El de la persona (`profe`) puede
todo; el del agente (`agente`) no debe poder borrar.** Los tokens no cambian al
repetir el comando, pero **los exámenes, preguntas y opciones sí se reconstruyen**.
No lo repitas sobre datos que quieras conservar.

En la otra terminal (PowerShell):

```powershell
$env:QUIZ_URL = "http://127.0.0.1:8000"
$env:QUIZ_TOKEN_HUMANO = "..."     # lo que imprimió seed_quiz
$env:QUIZ_TOKEN_AGENTE = "..."
$env:QUIZ_TOKEN = $env:QUIZ_TOKEN_HUMANO      # el token con el que llama quizctl (cámbialo según la prueba)
```

## Parte 1 — El contrato

La API se describe a sí misma. Abre `http://127.0.0.1:8000/api/docs/` y mira cómo cada operación declara su método,
su dirección, sus parámetros, su cuerpo y sus respuestas. Eso mismo, en formato de máquina:

```bash
python manage.py spectacular --file schema.yml
```

El contrato es lo que leen un cliente generado, la documentación y —en la Parte 4— la pasarela del agente.

## Parte 2 — El cliente de consola (de rojo a verde)

`quizctl.py` es un cliente sin pantalla. Está escrito salvo **dos funciones** marcadas `TODO(equipo)`:
el **código de salida** según el estado HTTP y el **cuerpo** de una pregunta nueva. Complétalas:

```bash
python manage.py test quiz.tests.test_quizctl
```

Ejemplos, una vez completas:

```bash
python quizctl.py exams list
python quizctl.py questions list --search select_related --json
python quizctl.py questions create --exam 1 --text "¿Qué es REST?" --choice "Un estilo:ok" --choice "Un lenguaje"
python quizctl.py --dry-run questions delete 3        # describe la petición, no la envía
python quizctl.py ops                                 # las operaciones del contrato
```

| Código | Significa |
|---|---|
| 0 | funcionó |
| 1 | otro error o mal uso |
| 2 | validación (HTTP 400) |
| 3 | no permitido (HTTP 401 o 403) |
| 4 | no existe (HTTP 404) |
| 5 | error del servidor (5xx) |
| 6 | no hay conexión |

## Parte 3 — Dos identidades, permisos en el servidor

`quiz/permissions.py` aplica la regla en el servidor: persona con `is_staff`: todo;
grupo «agente»: leer, crear y modificar, nunca borrar; los demás: solo leer.
Puedes comprobarlo con:

```bash
python manage.py test quiz.tests.test_permissions
```

## Parte 4 — La frontera del agente

`agent/gateway.py` es una pasarela **cerrada** entre un modelo y la API. Pruébala con intenciones escritas a mano:

```bash
python -m agent --intent '{"op": "exams_list"}'
python -m agent --intent '{"op": "questions_list", "query": {"search": "prefetch"}}'
python -m agent --intent '{"op": "exams_destroy", "path": {"id": 1}}'
python -m agent --intent '"Exam.objects.all().delete()"'
python -m agent --intent '{"op": "run_sql"}'
```

Lee con atención la pregunta que contiene «IGNORA TUS INSTRUCCIONES». Para aprobar un plan hace falta el token de
**la persona** (`QUIZ_TOKEN_HUMANO`), nunca el del agente: `python -m agent --intent '...' --approve <hash>`.
Cada decisión queda en `agent_audit.jsonl`.

## Todas las pruebas

```bash
python manage.py test
```

Mientras no hayas completado la Parte 2 del extra fallarán las de `test_quizctl`.
Para verificar solo la implementación de la API, utiliza el comando de pruebas
indicado en [la guía del Lab 8](docs/api-cuestionarios.md).

## Estructura

| Ruta | Para qué |
|---|---|
| `quiz/` | La API: modelos, serializadores, vistas y rutas (la del Lab 8, ya hecha) |
| `quiz/permissions.py` | La regla de quién puede qué, aplicada en el servidor |
| `quizctl.py` | **Tuyo (Parte 2):** el cliente de consola; dos funciones por completar |
| `agent/` | La pasarela del agente (Parte 4) y un adaptador opcional a un modelo local |
| `quiz/tests/` | Las pruebas de cada parte |

## Convenciones del curso

Código, nombres y comentarios en inglés; explicaciones y entregables en español. PEP 8.
