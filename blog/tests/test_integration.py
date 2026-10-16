"""The ORM lab shares Nexo's layout, not the other apps' records."""
from io import BytesIO, StringIO, TextIOWrapper

from django.contrib.auth import get_user_model
from django.contrib.staticfiles import finders
from django.core.management import call_command, get_commands
from django.test import TestCase
from django.urls import reverse

from blog.models import Post
from movies.models import Movie
from news.models import Article, Author, Category


class NexoIntegrationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_blog", verbosity=0)
        cls.movie = Movie.objects.create(title="Película conservada", release_year=2026)
        cls.author = Author.objects.create(name="Ana Quispe")
        cls.category = Category.objects.create(name="Tecnología", slug="tecnologia")
        cls.article = Article.objects.create(
            title="Noticia conservada", slug="noticia-conservada", summary="Resumen",
            body="Texto de la noticia", author=cls.author,
        )
        cls.article.categories.add(cls.category)
        cls.admin = get_user_model().objects.create_superuser(
            username="integration_admin", password="IntegrationAdmin12345",
            email="integration@example.com",
        )

    def test_blog_uses_its_own_route_and_shared_layout(self):
        self.assertEqual(reverse("front_page"), "/blog/")
        response = self.client.get(reverse("front_page"))
        self.assertEqual(response.status_code, 200)
        for template in ("base.html", "components/navbar.html", "components/breadcrumbs.html"):
            self.assertTemplateUsed(response, template)
        self.assertContains(response, 'aria-current="page">Blog ORM</a>')
        self.assertContains(response, reverse("movies:home"))
        self.assertContains(response, reverse("news:home"))
        self.assertContains(response, "/static/blog/css/style.css")
        self.assertIsNotNone(finders.find("blog/css/style.css"))
        self.assertNotContains(response, self.article.title)

    def test_other_sections_link_to_the_blog(self):
        for url in (
            reverse("movies:home"), reverse("movies:catalog"),
            reverse("news:home"), self.article.get_absolute_url(),
        ):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(response, f'href="{reverse("front_page")}"')

    def test_one_admin_lists_all_three_apps(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("admin:index"))
        self.assertContains(response, "Laboratorio ORM e IA")
        for model in ("blog_post", "movies_movie", "news_article"):
            self.assertContains(response, reverse(f"admin:{model}_changelist"))

    def test_all_blog_admin_pages_render(self):
        self.client.force_login(self.admin)
        for model in ("author", "profile", "category", "tag", "post", "comment"):
            with self.subTest(model=model):
                response = self.client.get(reverse(f"admin:blog_{model}_changelist"))
                self.assertEqual(response.status_code, 200)

    def test_resetting_the_blog_preserves_movies_news_and_users(self):
        call_command("seed_blog", verbosity=0)
        self.assertEqual(Post.objects.count(), 15)
        self.assertTrue(Movie.objects.filter(pk=self.movie.pk).exists())
        self.assertTrue(Article.objects.filter(pk=self.article.pk).exists())
        self.assertTrue(Author.objects.filter(pk=self.author.pk).exists())
        self.assertTrue(Category.objects.filter(pk=self.category.pk).exists())
        self.assertTrue(self.article.categories.filter(pk=self.category.pk).exists())
        self.assertTrue(get_user_model().objects.filter(pk=self.admin.pk).exists())

    def test_lab_commands_allow_pending_manual_answers(self):
        commands = get_commands()
        for command in ("seed_blog", "duel", "agent"):
            self.assertEqual(commands[command], "blog")
        self.assertEqual(commands["seed_lab"], "movies")
        self.assertEqual(commands["seed_news"], "news")
        out = StringIO()
        call_command("duel", source="team", stdout=out)
        self.assertLessEqual(out.getvalue().count("sin escribir"), 4)
        buffer = BytesIO()
        with TextIOWrapper(buffer, encoding="cp1252", write_through=True) as output:
            call_command("duel", source="ai", stdout=output)
            text = buffer.getvalue().decode("cp1252")
        self.assertIn("[OK] correcta", text)
        self.assertIn("[!] correcta pero cara", text)
        self.assertIn("->", text)

    def test_blog_content_remains_escaped(self):
        post = Post.objects.filter(published=True).first()
        post.title = '<script>alert("title")</script>'
        post.body = "<strong>Texto del usuario</strong>"
        post.save()
        response = self.client.get(reverse("front_page"))
        self.assertContains(response, "&lt;script&gt;")
        self.assertContains(response, "&lt;strong&gt;Texto del usuario&lt;/strong&gt;")
        self.assertNotContains(response, post.title)
        self.assertNotContains(response, post.body)
