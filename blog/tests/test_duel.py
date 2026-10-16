"""The duel itself is code, so it has tests: the oracle must agree with the
reference answers, and the assistant's answers must fail in the way the lab says."""
import importlib.util
import unittest
from io import StringIO

from django.core.management import call_command
from django.db.models import QuerySet
from django.test import TestCase

from blog.duel import authorized_ai_answers
from blog.duel.questions import QUESTIONS
from blog.duel.runner import run_all

HAS_TEACHER = importlib.util.find_spec("teacher") is not None


class DuelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_blog", verbosity=0)

    def statuses(self, source):
        return {verdict.key: verdict.status for verdict in run_all(source)}

    @unittest.skipUnless(HAS_TEACHER, "carpeta teacher/ ausente")
    def test_reference_solutions_are_all_correct_and_cheap(self):
        self.assertEqual(set(self.statuses("solutions").values()), {"ok"})

    def test_team_answers_are_correct_when_provided(self):
        for verdict in run_all("team"):
            with self.subTest(question=verdict.key):
                if verdict.key in {"q1", "q2", "q3", "q4"} and verdict.status == "todo":
                    continue  # The student must complete these without AI.
                self.assertEqual(verdict.status, "ok", verdict.detail)

    def test_the_assistant_fails_where_the_lab_says(self):
        self.assertEqual(
            self.statuses("ai"),
            {
                "q1": "ok",
                "q2": "ok",
                "q3": "wrong",   # excludes the boundary dates
                "q4": "costly",  # right result, filtered in Python (N+1)
                "q5": "wrong",   # counts multiplied: no distinct=True
                "q6": "error",   # invented field `author__country`
                "q7": "ok",
                "q8": "wrong",   # drafts are not "never published"
            },
        )

    def test_authorized_ai_answers_are_querysets_correct_and_cheap(self):
        for question in QUESTIONS:
            with self.subTest(question=question.key):
                self.assertIsInstance(
                    getattr(authorized_ai_answers, question.key)(), QuerySet,
                )
        for verdict in run_all("ai_authorized"):
            with self.subTest(question=verdict.key):
                self.assertEqual(verdict.status, "ok", verdict.detail)
                self.assertEqual(verdict.queries, 1)

    def test_command_accepts_authorized_ai_in_strict_mode(self):
        out = StringIO()
        call_command("duel", source="ai_authorized", strict=True, stdout=out)
        self.assertIn("8 de 8 correctas y baratas", out.getvalue())

    def test_single_question(self):
        verdicts = run_all("ai", only="q4")
        self.assertEqual(len(verdicts), 1)
        self.assertEqual(verdicts[0].queries, 1 + 15)
