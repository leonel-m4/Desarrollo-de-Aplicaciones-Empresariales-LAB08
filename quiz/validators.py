from rest_framework.exceptions import ValidationError


def validate_choice_set(choices):
    """Validate a complete set, including replacements in a question PATCH."""
    if len(choices) < 2:
        raise ValidationError("Una pregunta necesita al menos dos opciones.")
    if sum(bool(choice.get("is_correct", False)) for choice in choices) != 1:
        raise ValidationError("Debe haber exactamente una opción correcta.")
    return choices


def validate_question_choices(question, *, exclude=None, extra=None):
    """Check the resulting question before an individual choice is changed."""
    choices = list(question.choices.exclude(pk=exclude).values("is_correct"))
    if extra is not None:
        choices.append(extra)
    try:
        validate_choice_set(choices)
    except ValidationError as error:
        raise ValidationError({"choices": error.detail}) from error
