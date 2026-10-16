from django.db import transaction
from rest_framework import serializers

from .models import Choice, Exam, Question
from .validators import validate_choice_set, validate_question_choices


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ["id", "question", "text", "is_correct"]
        read_only_fields = ["id"]

    @transaction.atomic
    def create(self, validated_data):
        question = validated_data["question"]
        Question.objects.select_for_update().get(pk=question.pk)
        validate_question_choices(
            question,
            extra={"is_correct": validated_data.get("is_correct", False)},
        )
        return super().create(validated_data)

    @transaction.atomic
    def update(self, instance, validated_data):
        question = validated_data.get("question", instance.question)
        # Lock both parents in a stable order when a choice changes question.
        list(
            Question.objects.select_for_update()
            .filter(pk__in=[instance.question_id, question.pk])
            .order_by("pk")
        )
        if question.pk != instance.question_id:
            validate_question_choices(instance.question, exclude=instance.pk)
        validate_question_choices(
            question,
            exclude=instance.pk,
            extra={
                "is_correct": validated_data.get(
                    "is_correct", instance.is_correct
                )
            },
        )
        return super().update(instance, validated_data)


class NestedChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ["id", "text", "is_correct"]
        read_only_fields = ["id"]

    def validate(self, attrs):
        # A supplied list replaces all rows, even during a question PATCH.
        if "text" not in attrs:
            raise serializers.ValidationError({
                "text": "Este campo es requerido.",
            })
        return attrs


class ExamSerializer(serializers.ModelSerializer):
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = ["id", "title", "created_at", "question_count"]
        read_only_fields = ["id", "created_at", "question_count"]

    def get_question_count(self, obj) -> int:
        count = getattr(obj, "question_count", None)
        return count if count is not None else obj.questions.count()


class QuestionSerializer(serializers.ModelSerializer):
    # Choices travel nested; the exam travels as an identifier.
    choices = NestedChoiceSerializer(many=True)

    class Meta:
        model = Question
        fields = ["id", "exam", "text", "choices", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_choices(self, value):
        return validate_choice_set(value)

    def create(self, validated_data):
        choices = validated_data.pop("choices")
        with transaction.atomic():
            question = Question.objects.create(**validated_data)
            Choice.objects.bulk_create(
                Choice(question=question, **choice) for choice in choices
            )
        return question

    def update(self, instance, validated_data):
        choices = validated_data.pop("choices", None)
        with transaction.atomic():
            instance = Question.objects.select_for_update().get(pk=instance.pk)
            instance = super().update(instance, validated_data)
            if choices is not None:  # sent choices replace the old ones
                instance.choices.all().delete()
                Choice.objects.bulk_create(
                    Choice(question=instance, **choice) for choice in choices
                )
        return instance


class QuestionFilterSerializer(serializers.Serializer):
    exam = serializers.IntegerField(
        required=False, min_value=1,
        help_text="Solo las preguntas de este examen (ID entero positivo).",
    )
