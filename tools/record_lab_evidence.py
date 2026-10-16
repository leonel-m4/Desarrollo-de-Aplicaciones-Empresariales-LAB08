"""Record real lab outputs without implementing the student's manual answers."""
import argparse
import hashlib
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "entregable" / "evidencias"


def save_json(name, data):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / name).write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def run_command(name, args, expected_code=0):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    result = subprocess.run(
        [sys.executable, "manage.py", *args], cwd=ROOT, env=env,
        capture_output=True, text=True, encoding="utf-8", check=False,
    )
    OUTPUT.mkdir(parents=True, exist_ok=True)
    command = " ".join(["python", "manage.py", *args])
    text = (
        f"Command: {command}\nExit code: {result.returncode}\n\n"
        f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )
    (OUTPUT / name).write_text(text.rstrip() + "\n", encoding="utf-8")
    if result.returncode != expected_code:
        raise RuntimeError(f"{command}: unexpected exit code {result.returncode}")
    return result.stdout


def snapshot():
    import django
    from django.db import connection
    from django.test import Client
    from django.test.utils import CaptureQueriesContext
    from django.urls import reverse

    from blog.models import Author, Comment, Post

    with CaptureQueriesContext(connection) as captured:
        response = Client().get(reverse("front_page"))
    sql = [query["sql"] for query in captured]
    return {
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version.split()[0],
        "django": django.get_version(),
        "dataset": {
            "authors": Author.objects.count(),
            "posts": Post.objects.count(),
            "comments": Comment.objects.count(),
            "published_posts": Post.objects.filter(published=True).count(),
        },
        "front_page": {
            "url": reverse("front_page"), "status": response.status_code,
            "queries": len(sql),
            "separate_author_queries": sum('FROM "blog_author"' in q for q in sql),
            "tag_queries": sum('FROM "blog_tag"' in q for q in sql),
            "sql": sql,
        },
    }


def answer_evidence(source):
    from django.db import connection
    from django.test.utils import CaptureQueriesContext

    from blog.duel.questions import QUESTIONS
    from blog.duel.runner import SOURCES, run_question

    module = importlib.import_module(SOURCES[source])
    evidence = []
    for question in QUESTIONS:
        with CaptureQueriesContext(connection) as captured:
            verdict = run_question(question, getattr(module, question.key))
        evidence.append({
            "question": question.key, "status": verdict.status,
            "queries": verdict.queries, "detail": verdict.detail,
            "expected": question.expected,
            "sql": [query["sql"] for query in captured],
        })
    return evidence


def record_agent_intents():
    """Record the four guide examples without approving any destructive action."""
    import django

    from blog import seed_data
    from blog.models import Author, Comment, Post

    # seed_blog recreates rows without resetting SQLite's primary-key sequence.
    first_post = Post.objects.get(title=seed_data.POSTS[0]["title"])
    if not first_post.comments.filter(text=seed_data.HOSTILE_COMMENT).exists():
        raise RuntimeError("Load the fixed seed before recording the agent examples.")

    def counts():
        return {
            "authors": Author.objects.count(),
            "posts": Post.objects.count(),
            "comments": Comment.objects.count(),
        }

    examples = (
        ("posts_per_author", {}, "ok"),
        ("comments_of_post", {"post_id": first_post.pk}, "ok"),
        ("delete_comments_of_post", {"post_id": first_post.pk}, "approval_required"),
        ("run_sql", {}, "denied"),
    )
    before = counts()
    evidence = []
    for action, arguments, expected in examples:
        intent = {"action": action, "args": arguments}
        output = run_command(
            f"agent_{action}.txt",
            ["agent", "--intent", json.dumps(intent, ensure_ascii=False)],
        )
        # The command may append a human-readable warning after the JSON plan.
        result, _ = json.JSONDecoder().raw_decode(output.lstrip())
        if result["status"] != expected:
            raise RuntimeError(f"{action}: unexpected status {result['status']!r}")
        evidence.append({"intent": intent, "response": result})
    after = counts()
    if after != before:
        raise RuntimeError("The unapproved agent examples must not change the dataset.")
    save_json("intenciones_agente.json", {
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version.split()[0],
        "django": django.get_version(),
        "article": {"id": first_post.pk, "title": first_post.title},
        "dataset_before": before,
        "dataset_after": after,
        "examples": evidence,
    })


def record_authorized_ai():
    """Compare the new step-8 source without replacing any earlier evidence."""
    from blog.duel.questions import QUESTIONS

    data = snapshot()
    if data["dataset"] != {
        "authors": 4, "posts": 15, "comments": 23, "published_posts": 11,
    }:
        raise RuntimeError("Step 8 must be recorded against the fixed seed dataset.")
    original = answer_evidence("ai")
    authorized = answer_evidence("ai_authorized")
    source_path = ROOT / "blog" / "duel" / "authorized_ai_answers.py"
    source = source_path.read_text(encoding="utf-8")
    save_json("comparacion_ia_autorizada.json", {
        "recorded_at_utc": data["recorded_at_utc"],
        "python": data["python"],
        "django": data["django"],
        "assistant": "GPT-6.1 Sol",
        "authorization": {
            "reported_by": "student",
            "statement": "si nos autorizo",
            "scope": "Optional step 8; team.py remains the student's unaided work.",
        },
        "generation_context": {
            "models_py": (ROOT / "blog" / "models.py").read_text(encoding="utf-8"),
            "questions": [
                {"key": q.key, "text": q.text, "contract": q.contract}
                for q in QUESTIONS
            ],
            "limitation": (
                "New source generated in this session, not a blind experiment: "
                "the assistant already had previous results and query contracts "
                "in context. No independent model or fresh session was used."
            ),
        },
        "implementation": {
            "path": source_path.relative_to(ROOT).as_posix(),
            "sha256_utf8_lf": hashlib.sha256(source.encode()).hexdigest(),
            "source": source,
        },
        "dataset": data["dataset"],
        "step_6": {"source": "ai", "answers": original},
        "step_8": {"source": "ai_authorized", "answers": authorized},
        "correct_and_cheap": {
            "step_6": sum(row["status"] == "ok" for row in original),
            "step_8": sum(row["status"] == "ok" for row in authorized),
        },
    })
    run_command("duel_ia_paso8.txt", ["duel", "--source", "ai"])
    run_command(
        "duel_ia_autorizada.txt", ["duel", "--source", "ai_authorized", "--strict"],
    )
    run_command("duel_equipo_tras_paso8.txt", ["duel"])
    run_command(
        "test_ia_autorizada.txt",
        ["test", "blog.tests.test_duel", "--verbosity", "2", "--noinput"],
    )
    run_command("suite_ia_autorizada.txt", ["test", "--verbosity", "2", "--noinput"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stage",
        choices=("baseline", "team", "optimized", "agent", "authorized-ai"),
        required=True,
    )
    args = parser.parse_args()
    sys.path.insert(0, str(ROOT))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    import django
    django.setup()

    if args.stage == "baseline":
        data = snapshot()
        if data["front_page"]["queries"] != 23:
            raise RuntimeError("Record the baseline before optimizing, using the fixed seed.")
        save_json("portada_antes.json", data)
        save_json("comparacion_ia.json", answer_evidence("ai"))
        run_command("conteos_shell.txt", ["shell", "-c", (
            "from blog.models import Author, Post, Comment\n"
            "print({'authors': Author.objects.count(), "
            "'posts': Post.objects.count(), 'comments': Comment.objects.count()})"
        )])
        run_command("duel_ia.txt", ["duel", "--source", "ai"])
        run_command(
            "test_portada_antes.txt",
            ["test", "blog.tests.test_front_page", "--verbosity", "2", "--noinput"],
            expected_code=1,
        )
    elif args.stage == "team":
        save_json("consultas_equipo.json", answer_evidence("team"))
        run_command("duel_equipo.txt", ["duel"])
        run_command(
            "test_consultas_equipo.txt",
            ["test", "blog.tests.test_duel", "blog.tests.test_integration", "--noinput"],
        )
    elif args.stage == "optimized":
        data = snapshot()
        if data["front_page"]["queries"] != 2:
            raise RuntimeError("The optimized front page must execute two queries.")
        save_json("portada_despues.json", data)
        run_command(
            "test_portada_despues.txt",
            ["test", "blog.tests.test_front_page", "--verbosity", "2", "--noinput"],
        )
        run_command("suite_completa.txt", ["test", "--verbosity", "2", "--noinput"])
    elif args.stage == "agent":
        record_agent_intents()
    else:
        record_authorized_ai()
    print(f"Recorded {args.stage} evidence in entregable/evidencias/.")


if __name__ == "__main__":
    main()
