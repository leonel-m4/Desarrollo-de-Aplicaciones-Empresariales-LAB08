"""Regression tests for the three resources and the browsable API setup."""
from django.contrib.auth.models import User
from rest_framework.test import APIClient, APITestCase

from quiz.models import Choice, Exam, Question

from .helpers import exam_id, reader_token, seed, valid_body


class ResourceTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.person, cls.agent = seed()

    def setUp(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.person}")
        self.question = Question.objects.first()

    def test_router_exposes_all_three_resources(self):
        response = self.client.get("/api/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            set(response.json()), {"exams", "questions", "choices"}
        )

    def test_exam_crud_and_read_only_fields(self):
        response = self.client.post("/api/exams/", {
            "id": 99999,
            "title": "Examen de prueba",
            "created_at": "2000-01-01T00:00:00Z",
            "question_count": 99,
        }, format="json")
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertNotEqual(data["id"], 99999)
        self.assertFalse(data["created_at"].startswith("2000-"))
        self.assertEqual(data["question_count"], 0)
        url = f"/api/exams/{data['id']}/"
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertEqual(
            self.client.put(url, {"title": "Reemplazo"}).status_code, 200
        )
        self.assertEqual(
            self.client.patch(url, {"title": "Edición"}).status_code, 200
        )
        self.assertEqual(self.client.delete(url).status_code, 204)
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_choice_crud_uses_a_question_identifier(self):
        response = self.client.post("/api/choices/", {
            "question": self.question.pk,
            "text": "Otro distractor",
            "is_correct": False,
        }, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["question"], self.question.pk)
        url = f"/api/choices/{response.json()['id']}/"
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertEqual(
            self.client.patch(url, {"text": "Texto actualizado"}).status_code,
            200,
        )
        self.assertEqual(self.client.put(url, {
            "question": self.question.pk,
            "text": "Texto reemplazado",
            "is_correct": False,
        }, format="json").status_code, 200)
        self.assertEqual(self.client.delete(url).status_code, 204)
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_choice_list_is_paginated(self):
        response = self.client.get("/api/choices/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], Choice.objects.count())
        self.assertEqual(len(response.json()["results"]), 5)
        self.assertIsNotNone(response.json()["next"])

    def test_creating_a_second_correct_choice_is_rejected(self):
        count = self.question.choices.count()
        response = self.client.post("/api/choices/", {
            "question": self.question.pk,
            "text": "Segunda correcta",
            "is_correct": True,
        }, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("exactamente una", str(response.json()))
        self.assertEqual(self.question.choices.count(), count)

    def test_changing_correctness_cannot_invalidate_the_question(self):
        for choice in self.question.choices.all():
            with self.subTest(choice=choice.pk):
                response = self.client.patch(f"/api/choices/{choice.pk}/", {
                    "is_correct": not choice.is_correct,
                }, format="json")
                self.assertEqual(response.status_code, 400)
                choice.refresh_from_db()
        self.assertEqual(
            self.question.choices.filter(is_correct=True).count(), 1
        )

    def test_deleting_the_correct_choice_is_rejected(self):
        choice = self.question.choices.get(is_correct=True)
        response = self.client.delete(f"/api/choices/{choice.pk}/")
        self.assertEqual(response.status_code, 400)
        self.assertTrue(Choice.objects.filter(pk=choice.pk).exists())

    def test_deleting_a_choice_cannot_leave_less_than_two(self):
        self.question.choices.filter(is_correct=False).exclude(
            pk=self.question.choices.filter(is_correct=False).first().pk
        ).delete()
        choice = self.question.choices.get(is_correct=False)
        response = self.client.delete(f"/api/choices/{choice.pk}/")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.question.choices.count(), 2)

    def test_an_incorrect_choice_can_move_between_valid_questions(self):
        choice = self.question.choices.filter(is_correct=False).first()
        target = Question.objects.exclude(pk=self.question.pk).first()
        response = self.client.patch(f"/api/choices/{choice.pk}/", {
            "question": target.pk,
        }, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.question.choices.count(), 3)
        self.assertEqual(target.choices.count(), 5)

    def test_moving_the_correct_choice_does_not_invalidate_its_source(self):
        choice = self.question.choices.get(is_correct=True)
        target = Question.objects.exclude(pk=self.question.pk).first()
        response = self.client.patch(f"/api/choices/{choice.pk}/", {
            "question": target.pk,
        }, format="json")
        self.assertEqual(response.status_code, 400)
        choice.refresh_from_db()
        self.assertEqual(choice.question_id, self.question.pk)

    def test_agent_and_reader_permissions_apply_to_choices_too(self):
        choice = self.question.choices.filter(is_correct=False).first()
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.agent}")
        self.assertEqual(
            self.client.delete(f"/api/choices/{choice.pk}/").status_code, 403
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {reader_token()}")
        self.assertEqual(self.client.get("/api/choices/").status_code, 200)
        self.assertEqual(self.client.post("/api/choices/", {
            "question": self.question.pk, "text": "No permitido",
        }, format="json").status_code, 403)

    def test_missing_or_invalid_question_identifiers_return_400(self):
        for question in (None, "no-es-un-numero", 99999):
            with self.subTest(question=question):
                body = {"text": "Opción"}
                if question is not None:
                    body["question"] = question
                response = self.client.post(
                    "/api/choices/", body, format="json"
                )
                self.assertEqual(response.status_code, 400)
                self.assertIn("question", response.json())

    def test_choices_are_declared_in_the_openapi_contract(self):
        schema = self.client.get("/api/schema/", {"format": "json"}).json()
        self.assertTrue(
            {"get", "post"} <= set(schema["paths"]["/api/choices/"])
        )
        self.assertTrue(
            {"get", "put", "patch", "delete"}
            <= set(schema["paths"]["/api/choices/{id}/"])
        )


class QuestionValidationTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.person, _ = seed()

    def setUp(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.person}")
        self.question = Question.objects.first()

    def test_zero_correct_choices_is_rejected_without_writing(self):
        body = valid_body(exam_id())
        for choice in body["choices"]:
            choice["is_correct"] = False
        response = self.client.post("/api/questions/", body, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("exactamente una", str(response.json()))
        self.assertEqual(Question.objects.count(), 8)

    def test_at_least_two_choices_are_required(self):
        for choices in ([], [{"text": "Única", "is_correct": True}]):
            with self.subTest(choices=choices):
                body = valid_body(exam_id())
                body["choices"] = choices
                response = self.client.post(
                    "/api/questions/", body, format="json"
                )
                self.assertEqual(response.status_code, 400)
                self.assertEqual(Question.objects.count(), 8)

    def test_patch_can_replace_choices_and_switch_the_correct_answer(self):
        old_ids = set(self.question.choices.values_list("pk", flat=True))
        choices = [
            {"id": 99999, "text": "Incorrecta", "is_correct": False},
            {"text": "Correcta", "is_correct": True},
        ]
        response = self.client.patch(f"/api/questions/{self.question.pk}/", {
            "choices": choices,
        }, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["choices"]), 2)
        self.assertEqual(
            self.question.choices.get(is_correct=True).text, "Correcta"
        )
        self.assertFalse(self.question.choices.filter(pk__in=old_ids).exists())
        self.assertNotIn(
            99999, self.question.choices.values_list("pk", flat=True)
        )

    def test_put_replaces_the_question_with_a_valid_complete_body(self):
        body = valid_body(exam_id("Django · Plantillas"))
        response = self.client.put(
            f"/api/questions/{self.question.pk}/", body, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["exam"], body["exam"])
        self.assertEqual(response.json()["text"], body["text"])
        self.assertEqual(len(response.json()["choices"]), 3)

    def test_invalid_partial_nested_choices_are_400_not_a_database_error(self):
        old_ids = list(self.question.choices.values_list("pk", flat=True))
        response = self.client.patch(f"/api/questions/{self.question.pk}/", {
            "text": "No debe guardarse",
            "choices": [{"is_correct": True}, {"text": "Incorrecta"}],
        }, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("text", str(response.json()["choices"]))
        self.question.refresh_from_db()
        self.assertNotEqual(self.question.text, "No debe guardarse")
        self.assertEqual(
            list(self.question.choices.values_list("pk", flat=True)), old_ids
        )

    def test_invalid_exam_filters_return_field_errors(self):
        for value in ("", "abc", "0", "-1", "1.5", "²"):
            with self.subTest(exam=value):
                response = self.client.get("/api/questions/", {"exam": value})
                self.assertEqual(response.status_code, 400)
                self.assertIn("exam", response.json())

    def test_filter_and_search_can_be_combined(self):
        response = self.client.get("/api/questions/", {
            "exam": exam_id(), "search": "PREFETCH_RELATED",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["results"][0]["exam"], exam_id())
        response = self.client.get("/api/questions/", {
            "exam": exam_id("Django · Plantillas"),
            "search": "prefetch_related",
        })
        self.assertEqual(response.json()["count"], 0)

    def test_second_page_has_no_duplicates_and_invalid_page_is_404(self):
        first = self.client.get("/api/questions/").json()
        second = self.client.get("/api/questions/", {"page": 2}).json()
        self.assertEqual(len(second["results"]), 3)
        self.assertIsNone(second["next"])
        self.assertIsNotNone(second["previous"])
        self.assertFalse(
            {row["id"] for row in first["results"]}
            & {row["id"] for row in second["results"]}
        )
        self.assertEqual(
            self.client.get("/api/questions/", {"page": 3}).status_code, 404
        )


class BrowsableApiTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        seed()
        User.objects.create_user(
            username="browser_staff", password="BrowserTestOnly123!",
            is_staff=True,
        )

    def setUp(self):
        self.client = APIClient(enforce_csrf_checks=True)

    def login_through_browser(self):
        response = self.client.get("/api-auth/login/")
        self.assertEqual(response.status_code, 200)
        response = self.client.post("/api-auth/login/", {
            "username": "browser_staff",
            "password": "BrowserTestOnly123!",
            "csrfmiddlewaretoken": self.client.cookies["csrftoken"].value,
            "next": "/api/",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/api/")

    def test_anonymous_browsable_api_shows_the_login_link(self):
        response = self.client.get("/api/", HTTP_ACCEPT="text/html")
        self.assertContains(response, "/api-auth/login/", status_code=401)

    def test_session_login_renders_all_resource_lists_and_their_forms(self):
        self.login_through_browser()
        paths = ["/api/", "/api/exams/", "/api/questions/", "/api/choices/"]
        paths.extend([
            f"/api/exams/{Exam.objects.first().pk}/",
            f"/api/questions/{Question.objects.first().pk}/",
            f"/api/choices/{Choice.objects.first().pk}/",
        ])
        for path in paths:
            with self.subTest(path=path):
                response = self.client.get(path, HTTP_ACCEPT="text/html")
                self.assertEqual(response.status_code, 200)
                self.assertTrue(
                    response["Content-Type"].startswith("text/html")
                )

    def test_session_writes_require_csrf(self):
        self.login_through_browser()
        response = self.client.post(
            "/api/exams/", {"title": "Sin CSRF"}, format="json"
        )
        self.assertEqual(response.status_code, 403)
        response = self.client.post(
            "/api/exams/", {"title": "Con CSRF"}, format="json",
            HTTP_X_CSRFTOKEN=self.client.cookies["csrftoken"].value,
        )
        self.assertEqual(response.status_code, 201)
