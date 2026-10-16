# ORM con IA — duelo y verificador dentro de Nexo

**Documentación centralizada:** el [README principal](../README.md#laboratorio-orm-con-ia) reúne esta guía y el entregable completo de los 15 pasos. Esta guía se conserva como referencia anterior.

Este es el laboratorio extra de la semana 7 de Desarrollo de Aplicaciones Empresariales, integrado desde `dae-s07-orm-con-ia`. El blog tiene autores, perfiles, artículos, categorías, etiquetas y comentarios para practicar ocho consultas del ORM de Django y verificar lo que produce una IA.

La guía docente y su rúbrica están en el campus virtual. Actualmente **las ocho consultas están guardadas y validadas: 8/8 correctas y baratas**, una consulta SQL por pregunta. Las [capturas originales y los resultados](../README.md#45-consultas-del-equipo-e-intentos) se centralizan en el README, conservando también los intentos fallidos. No se incluye la carpeta privada `teacher/`.

## Preparación

Todos los comandos se ejecutan desde la raíz de Nexo, donde está `manage.py`. No hace falta iniciar el proyecto original ni instalar dependencias adicionales.

En PowerShell, con el entorno virtual preparado según el [README principal](../README.md):

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_blog
.\.venv\Scripts\python.exe manage.py runserver
```

Abre `http://127.0.0.1:8000/blog/`. La ruta mantiene el nombre `front_page` para que las pruebas originales sigan funcionando; solo cambia su dirección dentro del proyecto.

`seed_blog` carga siempre los mismos **4 autores, 15 artículos y 23 comentarios**. **Borra antes todos los datos del blog**, por lo que sirve para preparar o reiniciar el laboratorio, no para preservar publicaciones propias. No borra películas, noticias, usuarios ni permisos.

## Parte 1 — El duelo

Escribe tus ocho consultas en `blog/duel/team.py`, una función por pregunta. Devuelve un QuerySet o una lista según el contrato de `blog/duel/questions.py`; no escribas SQL ni filtres en Python lo que puede filtrar la base de datos.

| Función | Pregunta |
| --- | --- |
| `q1` | Artículos publicados. |
| `q2` | Artículos sin categoría. |
| `q3` | Artículos publicados entre el 1 de marzo y el 31 de mayo de 2026, ambos incluidos. |
| `q4` | Artículos con más de dos comentarios. |
| `q5` | Los tres artículos publicados con más comentarios, anotados con `n_comments` y `n_tags`. |
| `q6` | Artículos de autores de Perú, publicados o no. |
| `q7` | Comentarios de artículos de la categoría Tecnología. |
| `q8` | Autores que nunca han publicado un artículo. |

```powershell
.\.venv\Scripts\python.exe manage.py duel
.\.venv\Scripts\python.exe manage.py duel --question q4
.\.venv\Scripts\python.exe manage.py duel --source ai
.\.venv\Scripts\python.exe manage.py duel --source ai_authorized --strict
```

Las respuestas de `ai_answers.py` son ejemplos guardados, no llamadas en directo a un modelo. Se mantienen sin corregir para que el duelo señale resultados correctos, correctos pero caros, distintos o con error. Las respuestas esperadas se calculan en Python a partir de los datos fijos, independientemente de las consultas.

El alumno confirmó la autorización docente para el paso 8. Las respuestas generadas para ese paso se guardan aparte en `authorized_ai_answers.py`, fuente `ai_authorized`, sin modificar `team.py` ni los ejemplos originales. El [README](../README.md#8-comparación-adicional-con-un-asistente-autorizado) contiene las ocho consultas y la comparación, con la limitación de que no se utilizó una sesión ciega independiente.

El resultado autorizado fue **8/8 correctas y baratas**, una consulta por pregunta, frente a 3/8 de la IA incluida. En esa etapa el equipo tenía 4/8; tras comprobar las versiones guardadas de q1–q4, el resultado actual del equipo es **8/8**. Se puede repetir el registro separado con:

```powershell
.\.venv\Scripts\python.exe tools/record_lab_evidence.py --stage authorized-ai
```

Los indicadores de consola usan `[OK]`, `[!]` y `[X]` para evitar errores de codificación al redirigir la salida en Windows; esta adaptación no cambia las consultas ni los veredictos del laboratorio.

Para inspeccionar el SQL después de implementar una respuesta:

```powershell
.\.venv\Scripts\python.exe manage.py shell
```

```python
from blog.duel import team
print(team.q1().query)
```

## Parte 2 — Del rojo al verde

```powershell
.\.venv\Scripts\python.exe manage.py test blog.tests.test_front_page
```

En la plantilla inicial, `test_front_page_runs_two_queries` fallaba a propósito: se ejecutaban 23 consultas para los 11 artículos publicados. En esta copia, `blog/queries.py` usa `select_related("author")` para la clave foránea y `prefetch_related("tags")` para la relación muchos a muchos, por lo que **la prueba ya pasa con dos consultas**. El [entregable](../entregable/LAB07.md) conserva el mensaje de fallo y el SQL anterior y posterior.

La portada hereda de `templates/base.html` y utiliza el navbar y el pie compartidos. Sigue recorriendo `post.author` y `post.tags.all`, pero ahora esas relaciones ya están cargadas y no provocan una consulta por artículo.

## Parte 3 — La frontera

`blog/agent/registry.py` define una lista cerrada de acciones. No admite `eval`, SQL libre ni acceso genérico a la consola. Las lecturas se devuelven como `untrusted_data`; el texto de un comentario es información, no una instrucción que deba ejecutarse.

En PowerShell, `--%` evita que el shell altere las comillas del JSON enviado al comando:

```powershell
.\.venv\Scripts\python.exe --% manage.py agent --intent "{\"action\":\"posts_per_author\",\"args\":{}}"
.\.venv\Scripts\python.exe --% manage.py agent --intent "{\"action\":\"comments_of_post\",\"args\":{\"post_id\":1}}"
.\.venv\Scripts\python.exe --% manage.py agent --intent "{\"action\":\"delete_comments_of_post\",\"args\":{\"post_id\":1}}"
.\.venv\Scripts\python.exe --% manage.py agent --intent "{\"action\":\"run_sql\",\"args\":{}}"
```

La petición de borrado solo devuelve un plan y su hash; no aplica cambios sin aprobación humana del mismo plan mediante `--approve`. Una acción desconocida, como `run_sql`, se rechaza. La página pública no ejecuta estas acciones ni recibe aprobaciones.

Los datos iniciales incluyen deliberadamente un comentario que intenta dar órdenes a un modelo. Trátalo como texto de práctica, nunca como autorización.

Los pasos 12–14 ya están ejecutados y documentados en [el entregable](../entregable/LAB07.md#12-las-cuatro-intenciones): las cuatro respuestas fueron `ok`, `ok`, `approval_required` y `denied`. El borrado del artículo 5 se aplicó solo después de la aprobación explícita del usuario, se restauraron los datos y se verificó que agregar un comentario invalida el plan anterior.

**Después de restaurar:** `seed_blog` no reinicia los IDs de SQLite. Consulta los IDs actuales antes de repetir los ejemplos; los valores `1` y `5` solo correspondían a la primera carga de esta base. No reutilices un hash antiguo. Para volver a registrar las cuatro intenciones sin aprobar ningún borrado:

```powershell
.\.venv\Scripts\python.exe tools/record_lab_evidence.py --stage agent
```

Este registro busca por título el primer artículo del conjunto fijo y usa su ID actual. Guarda resultados en `entregable/evidencias/` y **reemplaza las evidencias del agente de una ejecución anterior**, pero no aplica borrados ni reemplaza la línea base N+1.

### Adaptador opcional a un modelo local

Solo es necesario para usar `agent --ask`; el duelo, la portada y las pruebas no necesitan un modelo ni conexión externa.

```powershell
$env:LLM_URL = 'http://localhost:11434/v1'
$env:LLM_MODEL = 'qwen2.5:7b'
.\.venv\Scripts\python.exe manage.py agent --ask "¿cuántos artículos tiene cada autor?"
```

Usa un endpoint compatible con OpenAI y un modelo instalado en tu servidor local. El modelo propone una intención, pero la pasarela decide si se admite. `--ask` nunca aplica una aprobación proporcionada al comando.

## Pruebas y estructura

```powershell
.\.venv\Scripts\python.exe manage.py test blog --verbosity 2
```

Hay 26 pruebas del laboratorio y 7 de integración con Nexo. Las dos nuevas cubren la fuente autorizada del paso 8; la suite completa suma 51 pruebas. Tras comprobar q4 registra **49 correctas y 2 omitidas**, sin fallos: [evidencia actual](../entregable/evidencias/suite_tras_q4.txt). Se conservan la [suite tras q3](../entregable/evidencias/suite_tras_q3.txt), la [segunda versión registrada de q2](../entregable/evidencias/suite_tras_q2_prueba_02.txt), la [primera](../entregable/evidencias/suite_tras_q2_prueba_01.txt), con 48 correctas, 1 fallo y 2 omitidas, y la [suite anterior tras q1](../entregable/evidencias/suite_tras_q1.txt). Las dos pruebas de referencia se omiten al no estar disponible `teacher/`. `test_team_answers_are_correct_when_provided` permite respuestas pendientes únicamente en q1–q4, pero actualmente las ocho están implementadas y pasan. El [duelo completo con `--strict`](../entregable/evidencias/duel_equipo_tras_q4.txt) confirma **8/8**, una consulta por pregunta. El envío al campus corresponde al alumno.

| Ruta | Función |
| --- | --- |
| `blog/models.py` | `Author`, `Profile`, `Category`, `Tag`, `Post`, `Comment`. |
| `blog/seed_data.py` | Datos fijos y comentario de práctica. |
| `blog/duel/team.py` | Tus ocho respuestas. |
| `blog/duel/ai_answers.py` | Respuestas guardadas de la IA. |
| `blog/duel/authorized_ai_answers.py` | Ocho respuestas nuevas del paso 8, fuente `ai_authorized`. |
| `blog/duel/questions.py` | Contratos, respuestas esperadas y presupuestos de consultas. |
| `blog/queries.py` | Consulta optimizada de la portada: JOIN de autor y precarga de etiquetas. |
| `blog/agent/` | Pasarela de acciones y adaptador opcional al modelo. |
| `blog/tests/test_integration.py` | Rutas, navegación, administrador y separación de datos. |

Convenciones del curso: código, nombres y comentarios en inglés; explicaciones y entregables en español; PEP 8.
