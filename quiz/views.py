from django.db import transaction
from django.db.models import Count
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, viewsets

from .models import Choice, Exam, Question
from .serializers import (
    ChoiceSerializer,
    ExamSerializer,
    QuestionFilterSerializer,
    QuestionSerializer,
)
from .validators import validate_question_choices


class ExamViewSet(viewsets.ModelViewSet):
    serializer_class = ExamSerializer
    queryset = Exam.objects.annotate(
        question_count=Count("questions")
    ).order_by("id")


@extend_schema_view(list=extend_schema(parameters=[QuestionFilterSerializer]))
class QuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["text"]

    def get_queryset(self):
        queryset = Question.objects.select_related("exam").prefetch_related(
            "choices"
        )
        if getattr(self, "swagger_fake_view", False):
            return queryset.none()
        params = QuestionFilterSerializer(
            data=self.request.query_params.dict()
        )
        params.is_valid(raise_exception=True)
        if "exam" in params.validated_data:
            queryset = queryset.filter(exam_id=params.validated_data["exam"])
        return queryset


class ChoiceViewSet(viewsets.ModelViewSet):
    serializer_class = ChoiceSerializer
    queryset = Choice.objects.select_related("question").order_by("id")

    @transaction.atomic
    def perform_destroy(self, instance):
        Question.objects.select_for_update().get(pk=instance.question_id)
        validate_question_choices(instance.question, exclude=instance.pk)
        instance.delete()
