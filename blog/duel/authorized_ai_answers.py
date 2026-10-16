"""New AI answers for step 8, with teacher authorization reported by the student.

Keep these separate from the student's unaided work and the saved, deliberately
flawed answers in ai_answers.py. Each function returns an unevaluated QuerySet.
"""
from datetime import date

from django.db.models import Count

from blog.models import Author, Comment, Post


def q1():
    """Los artículos que ya están publicados."""
    return Post.objects.filter(published=True)


def q2():
    """Los artículos que no tienen categoría asignada."""
    return Post.objects.filter(category__isnull=True)


def q3():
    """Los artículos publicados entre ambas fechas, incluidos los extremos."""
    return Post.objects.filter(
        published=True,
        published_at__range=(date(2026, 3, 1), date(2026, 5, 31)),
    )


def q4():
    """Los artículos con más de dos comentarios."""
    return Post.objects.annotate(n_comments=Count("comments")).filter(n_comments__gt=2)


def q5():
    """Los tres publicados con más comentarios, sin multiplicar los conteos."""
    return (
        Post.objects.filter(published=True)
        .annotate(
            n_comments=Count("comments", distinct=True),
            n_tags=Count("tags", distinct=True),
        )
        .order_by("-n_comments", "pk")[:3]
    )


def q6():
    """Los artículos de autores cuyo perfil indica Perú."""
    return Post.objects.filter(author__profile__country="Perú")


def q7():
    """Los comentarios de artículos de Tecnología."""
    return Comment.objects.filter(post__category__name="Tecnología")


def q8():
    """Los autores sin ningún artículo publicado, aunque tengan borradores."""
    return Author.objects.exclude(posts__published=True)
