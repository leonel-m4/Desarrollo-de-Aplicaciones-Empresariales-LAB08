from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from movies.models import Genre, Movie, Person, Rating


class Command(BaseCommand):
    help = 'Crea usuarios, grupo editores y datos de prueba para el laboratorio.'

    def handle(self, *args, **options):
        User = get_user_model()

        superuser, created = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@example.com', 'is_staff': True, 'is_superuser': True},
        )
        if created:
            superuser.set_password('Admin12345')
            superuser.save()

        editors, _ = Group.objects.get_or_create(name='editores')
        movie_permissions = Permission.objects.filter(codename__in=['add_movie', 'change_movie'])
        editors.permissions.set(movie_permissions)

        editor, created = User.objects.get_or_create(
            username='editor',
            defaults={'email': 'editor@example.com', 'is_staff': True},
        )
        if created:
            editor.set_password('Editor12345')
        editor.is_staff = True
        editor.is_superuser = False
        editor.save()
        editor.groups.add(editors)

        Rating.objects.all().delete()
        Movie.objects.all().delete()

        genres = {name: Genre.objects.get_or_create(name=name)[0] for name in ['Accion', 'Drama', 'Ciencia ficcion', 'Comedia']}
        people = {
            name: Person.objects.get_or_create(name=name)[0]
            for name in [
                'Christopher Nolan',
                'Denis Villeneuve',
                'Matt Reeves',
                'Greta Gerwig',
                'James Gunn',
                'George Miller',
                'Martin Scorsese',
                'David Fincher',
                'Leonardo DiCaprio',
                'Timothee Chalamet',
                'Robert Pattinson',
                'Margot Robbie',
                'Chris Pratt',
            ]
        }

        movies = [
            {
                'title': 'The Batman',
                'year': 2022,
                'genre': 'Accion',
                'director': 'Matt Reeves',
                'cast': ['Robert Pattinson'],
                'poster_url': 'https://image.tmdb.org/t/p/w780/74xTEgt7R36Fpooo50r9T25onhq.jpg',
                'synopsis': 'Batman investiga una serie de crimenes que revelan la corrupcion oculta de Gotham.',
            },
            {
                'title': 'John Wick',
                'year': 2014,
                'genre': 'Accion',
                'director': 'Chad Stahelski',
                'cast': ['Keanu Reeves'],
                'poster_url': 'https://image.tmdb.org/t/p/w780/fZPSd91yGE9fCcCe6OoQr6E3Bev.jpg',
                'synopsis': 'Un exasesino regresa al mundo criminal para cobrar venganza.',
            },
            {
                'title': 'The Dark Knight',
                'year': 2008,
                'genre': 'Accion',
                'director': 'Christopher Nolan',
                'cast': ['Christian Bale'],
                'poster_url': 'https://image.tmdb.org/t/p/w780/qJ2tW6WMUDux911r6m7haRef0WH.jpg',
                'synopsis': 'Batman enfrenta al Joker, un criminal que busca hundir Gotham en el caos.',
            },
            {
                'title': 'Mad Max: Fury Road',
                'year': 2015,
                'genre': 'Accion',
                'director': 'George Miller',
                'cast': ['Margot Robbie'],
                'poster_url': 'https://image.tmdb.org/t/p/w780/hA2ple9q4qnwxp3hKVNhroipsir.jpg',
                'synopsis': 'Furiosa y Max escapan de un tirano en una persecucion brutal por el desierto.',
            },
            {
                'title': 'Gladiator',
                'year': 2000,
                'genre': 'Accion',
                'director': 'Ridley Scott',
                'cast': ['Russell Crowe'],
                'poster_url': 'https://image.tmdb.org/t/p/w780/ty8TGRuvJLPUmAR1H1nRIsgwvim.jpg',
                'synopsis': 'Un general romano traicionado lucha como gladiador para recuperar su honor.',
            },
            {
                'title': 'Top Gun: Maverick',
                'year': 2022,
                'genre': 'Accion',
                'director': 'Joseph Kosinski',
                'cast': ['Tom Cruise'],
                'poster_url': 'https://image.tmdb.org/t/p/w780/62HCnUTziyWcpDaBO2i1DX17ljH.jpg',
                'synopsis': 'Maverick entrena a una nueva generacion de pilotos para una mision extrema.',
            },
            {
                'title': 'Guardians of the Galaxy',
                'year': 2014,
                'genre': 'Accion',
                'director': 'James Gunn',
                'cast': ['Chris Pratt'],
                'poster_url': 'https://image.tmdb.org/t/p/w780/r7vmZjiyZw9rpJMQJdXpjgiCOk9.jpg',
                'synopsis': 'Un grupo de inadaptados espaciales debe unirse para proteger una gema cosmica.',
            },
            {
                'title': 'The Matrix',
                'year': 1999,
                'genre': 'Accion',
                'director': 'Lana Wachowski',
                'cast': ['Keanu Reeves'],
                'poster_url': 'https://image.tmdb.org/t/p/w780/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg',
                'synopsis': 'Un programador descubre que la realidad es una simulacion controlada por maquinas.',
            },
            {
                'title': 'Avengers: Endgame',
                'year': 2019,
                'genre': 'Accion',
                'director': 'Anthony Russo',
                'cast': ['Robert Downey Jr.'],
                'poster_url': 'https://image.tmdb.org/t/p/w780/or06FN3Dka5tukK1e9sl16pB3iy.jpg',
                'synopsis': 'Los Vengadores intentan revertir las consecuencias del chasquido de Thanos.',
            },
            {
                'title': 'Mission: Impossible - Fallout',
                'year': 2018,
                'genre': 'Accion',
                'director': 'Christopher McQuarrie',
                'cast': ['Tom Cruise'],
                'poster_url': 'https://image.tmdb.org/t/p/w780/AkJQpZp9WoNdj7pLYSj1L0RcMMN.jpg',
                'synopsis': 'Ethan Hunt enfrenta una carrera contrarreloj despues de una mision fallida.',
            },
            {
                'title': 'Interstellar',
                'year': 2014,
                'genre': 'Ciencia ficcion',
                'director': 'Christopher Nolan',
                'cast': ['Leonardo DiCaprio'],
                'poster_url': 'https://image.tmdb.org/t/p/w780/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg',
                'synopsis': 'Exploradores viajan por un agujero de gusano para encontrar un nuevo hogar para la humanidad.',
            },
            {
                'title': 'Inception',
                'year': 2010,
                'genre': 'Ciencia ficcion',
                'director': 'Christopher Nolan',
                'cast': ['Leonardo DiCaprio'],
                'poster_url': 'https://image.tmdb.org/t/p/w780/edv5CZvWj09upOsy2Y6IwDhK8bt.jpg',
                'synopsis': 'Un ladron que entra en los suenos recibe una mision para implantar una idea.',
            },
            {
                'title': 'Dune',
                'year': 2021,
                'genre': 'Ciencia ficcion',
                'director': 'Denis Villeneuve',
                'cast': ['Timothee Chalamet'],
                'poster_url': 'https://image.tmdb.org/t/p/w780/d5NXSklXo0qyIYkgV94XAgMIckC.jpg',
                'synopsis': 'Paul Atreides llega a Arrakis, planeta clave en una guerra por el recurso mas valioso.',
            },
            {
                'title': 'Blade Runner 2049',
                'year': 2017,
                'genre': 'Ciencia ficcion',
                'director': 'Denis Villeneuve',
                'cast': ['Ryan Gosling'],
                'poster_url': 'https://image.tmdb.org/t/p/w780/gajva2L0rPYkEWjzgFlBXCAVBE5.jpg',
                'synopsis': 'Un nuevo blade runner descubre un secreto capaz de alterar el futuro de la humanidad.',
            },
            {
                'title': 'Arrival',
                'year': 2016,
                'genre': 'Ciencia ficcion',
                'director': 'Denis Villeneuve',
                'cast': ['Amy Adams'],
                'poster_url': 'https://image.tmdb.org/t/p/w780/x2FJsf1ElAgr63Y3PNPtJrcmpoe.jpg',
                'synopsis': 'Una linguista intenta comunicarse con visitantes extraterrestres recien llegados a la Tierra.',
            },
            {
                'title': 'The Martian',
                'year': 2015,
                'genre': 'Ciencia ficcion',
                'director': 'Ridley Scott',
                'cast': ['Matt Damon'],
                'poster_url': 'https://image.tmdb.org/t/p/w780/3ndAx3weG6KDkJIRMCi5vXX6Dyb.jpg',
                'synopsis': 'Un astronauta queda varado en Marte y debe sobrevivir con recursos limitados.',
            },
            {
                'title': 'Ex Machina',
                'year': 2014,
                'genre': 'Ciencia ficcion',
                'director': 'Alex Garland',
                'cast': ['Alicia Vikander'],
                'poster_url': 'https://image.tmdb.org/t/p/w780/9goPE2IoMIXxTLWzl7aizwuIiLh.jpg',
                'synopsis': 'Un joven programador evalua la conciencia de una inteligencia artificial avanzada.',
            },
            {
                'title': 'Avatar',
                'year': 2009,
                'genre': 'Ciencia ficcion',
                'director': 'James Cameron',
                'cast': ['Sam Worthington'],
                'poster_url': 'https://image.tmdb.org/t/p/w780/kyeqWdyUXW608qlYkRqosgbbJyK.jpg',
                'synopsis': 'Un exmarine llega a Pandora y queda atrapado entre dos mundos en conflicto.',
            },
            {
                'title': 'Back to the Future',
                'year': 1985,
                'genre': 'Ciencia ficcion',
                'director': 'Robert Zemeckis',
                'cast': ['Michael J. Fox'],
                'poster_url': 'https://image.tmdb.org/t/p/w780/fNOH9f1aA7XRTzl1sAOx9iF553Q.jpg',
                'synopsis': 'Marty McFly viaja accidentalmente al pasado y debe reparar su propia historia.',
            },
            {
                'title': 'Tenet',
                'year': 2020,
                'genre': 'Ciencia ficcion',
                'director': 'Christopher Nolan',
                'cast': ['John David Washington'],
                'poster_url': 'https://image.tmdb.org/t/p/w780/aCIFMriQh8rvhxpN1IWGgvH0Tlg.jpg',
                'synopsis': 'Un agente se enfrenta a una amenaza global usando tecnologia de inversion temporal.',
            },
            {
                'title': 'Barbie',
                'year': 2023,
                'genre': 'Comedia',
                'director': 'Greta Gerwig',
                'cast': ['Margot Robbie'],
                'poster_url': 'https://image.tmdb.org/t/p/w780/iuFNMS8U5cb6xfzi51Dbkovj7vM.jpg',
                'synopsis': 'Barbie viaja al mundo real y descubre preguntas sobre identidad y libertad.',
            },
            {
                'title': 'The Wolf of Wall Street',
                'year': 2013,
                'genre': 'Comedia',
                'director': 'Martin Scorsese',
                'cast': ['Leonardo DiCaprio', 'Margot Robbie'],
                'poster_url': 'https://image.tmdb.org/t/p/w780/34m2tygAYBGqA9MXKhRDtzYd4MR.jpg',
                'synopsis': 'Jordan Belfort asciende en Wall Street entre ambicion, excesos y caos financiero.',
            },
            {
                'title': 'The Grand Budapest Hotel',
                'year': 2014,
                'genre': 'Comedia',
                'director': 'Wes Anderson',
                'cast': ['Ralph Fiennes'],
                'poster_url': 'https://image.tmdb.org/t/p/w780/eWdyYQreja6JGCzqHWXpWHDrrPo.jpg',
                'synopsis': 'Un conserje y su joven protegido quedan envueltos en una aventura llena de crimen y estilo.',
            },
            {
                'title': 'The Hangover',
                'year': 2009,
                'genre': 'Comedia',
                'director': 'Todd Phillips',
                'cast': ['Bradley Cooper'],
                'poster_url': 'https://upload.wikimedia.org/wikipedia/en/b/b9/Hangoverposter09.jpg',
                'synopsis': 'Tres amigos despiertan sin recordar la despedida de soltero y deben encontrar al novio.',
            },
            {
                'title': 'Mean Girls',
                'year': 2004,
                'genre': 'Comedia',
                'director': 'Mark Waters',
                'cast': ['Lindsay Lohan'],
                'poster_url': 'https://image.tmdb.org/t/p/w780/fXm3YKXAEjx7d2tIWDg9TfRZtsU.jpg',
                'synopsis': 'Una estudiante nueva entra al mundo social competitivo de una preparatoria estadounidense.',
            },
            {
                'title': 'Knives Out',
                'year': 2019,
                'genre': 'Comedia',
                'director': 'Rian Johnson',
                'cast': ['Daniel Craig'],
                'poster_url': 'https://image.tmdb.org/t/p/w780/pThyQovXQrw2m0s9x82twj48Jq4.jpg',
                'synopsis': 'Un detective investiga la muerte de un novelista rodeado de una familia sospechosa.',
            },
            {
                'title': 'Jojo Rabbit',
                'year': 2019,
                'genre': 'Comedia',
                'director': 'Taika Waititi',
                'cast': ['Roman Griffin Davis'],
                'poster_url': 'https://image.tmdb.org/t/p/w780/7GsM4mtM0worCtIVeiQt28HieeN.jpg',
                'synopsis': 'Un nino aleman cambia su vision del mundo durante los ultimos dias de la guerra.',
            },
            {
                'title': 'Deadpool',
                'year': 2016,
                'genre': 'Comedia',
                'director': 'Tim Miller',
                'cast': ['Ryan Reynolds'],
                'poster_url': 'https://image.tmdb.org/t/p/w780/zq8Cl3PNIDGU3iWNRoc5nEZ6pCe.jpg',
                'synopsis': 'Un mercenario con humor irreverente busca venganza tras obtener habilidades regenerativas.',
            },
            {
                'title': 'School of Rock',
                'year': 2003,
                'genre': 'Comedia',
                'director': 'Richard Linklater',
                'cast': ['Jack Black'],
                'poster_url': 'https://image.tmdb.org/t/p/w780/zXLXaepIBvFVLU25DH3wv4IPSbe.jpg',
                'synopsis': 'Un musico desempleado se hace pasar por profesor y forma una banda escolar.',
            },
            {
                'title': 'Hot Fuzz',
                'year': 2007,
                'genre': 'Comedia',
                'director': 'Edgar Wright',
                'cast': ['Simon Pegg'],
                'poster_url': 'https://image.tmdb.org/t/p/w780/zPib4ukTSdXvHP9pxGkFCe34f3y.jpg',
                'synopsis': 'Un policia ejemplar descubre secretos violentos en un pueblo aparentemente tranquilo.',
            },
            {
                'title': 'Oppenheimer',
                'year': 2023,
                'genre': 'Drama',
                'director': 'Christopher Nolan',
                'cast': ['Robert Pattinson'],
                'poster_url': 'https://image.tmdb.org/t/p/w780/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg',
                'synopsis': 'J. Robert Oppenheimer lidera el proyecto que cambiaria la historia moderna.',
            },
            {
                'title': 'The Social Network',
                'year': 2010,
                'genre': 'Drama',
                'director': 'David Fincher',
                'cast': ['Timothee Chalamet'],
                'poster_url': 'https://image.tmdb.org/t/p/w780/n0ybibhJtQ5icDqTp8eRytcIHJx.jpg',
                'synopsis': 'La creacion de Facebook provoca conflictos legales y rupturas entre sus fundadores.',
            },
            {
                'title': 'The Godfather',
                'year': 1972,
                'genre': 'Drama',
                'director': 'Francis Ford Coppola',
                'cast': ['Marlon Brando'],
                'poster_url': 'https://image.tmdb.org/t/p/w780/3bhkrj58Vtu7enYsRolD1fZdja1.jpg',
                'synopsis': 'La familia Corleone enfrenta poder, lealtad y violencia dentro del crimen organizado.',
            },
            {
                'title': 'Forrest Gump',
                'year': 1994,
                'genre': 'Drama',
                'director': 'Robert Zemeckis',
                'cast': ['Tom Hanks'],
                'poster_url': 'https://image.tmdb.org/t/p/w780/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg',
                'synopsis': 'Un hombre sencillo atraviesa momentos clave de la historia moderna estadounidense.',
            },
            {
                'title': 'The Shawshank Redemption',
                'year': 1994,
                'genre': 'Drama',
                'director': 'Frank Darabont',
                'cast': ['Tim Robbins'],
                'poster_url': 'https://image.tmdb.org/t/p/w780/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg',
                'synopsis': 'Un banquero condenado injustamente construye esperanza y amistad dentro de prision.',
            },
            {
                'title': 'Fight Club',
                'year': 1999,
                'genre': 'Drama',
                'director': 'David Fincher',
                'cast': ['Brad Pitt'],
                'poster_url': 'https://image.tmdb.org/t/p/w780/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg',
                'synopsis': 'Un empleado insomne conoce a Tyler Durden y entra en una espiral de rebeldia.',
            },
            {
                'title': 'Goodfellas',
                'year': 1990,
                'genre': 'Drama',
                'director': 'Martin Scorsese',
                'cast': ['Ray Liotta'],
                'poster_url': 'https://image.tmdb.org/t/p/w780/aKuFiU82s5ISJpGZp7YkIr3kCUd.jpg',
                'synopsis': 'La vida de Henry Hill dentro de la mafia muestra poder, ambicion y caida.',
            },
            {
                'title': 'Whiplash',
                'year': 2014,
                'genre': 'Drama',
                'director': 'Damien Chazelle',
                'cast': ['Miles Teller'],
                'poster_url': 'https://image.tmdb.org/t/p/w780/6uSPcdGNA2A6vJmCagXkvnutegs.jpg',
                'synopsis': 'Un joven baterista enfrenta la presion extrema de un exigente profesor de musica.',
            },
            {
                'title': 'Parasite',
                'year': 2019,
                'genre': 'Drama',
                'director': 'Bong Joon-ho',
                'cast': ['Song Kang-ho'],
                'poster_url': 'https://image.tmdb.org/t/p/w780/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg',
                'synopsis': 'Una familia pobre se infiltra en la vida de una familia rica con consecuencias inesperadas.',
            },
            {
                'title': 'Joker',
                'year': 2019,
                'genre': 'Drama',
                'director': 'Todd Phillips',
                'cast': ['Joaquin Phoenix'],
                'poster_url': 'https://image.tmdb.org/t/p/w780/udDclJoHjfjb8Ekgsd4FDteOkCU.jpg',
                'synopsis': 'Arthur Fleck desciende hacia una identidad violenta en una ciudad indiferente.',
            },
        ]

        required_titles = {
            'The Batman',
            'Mad Max: Fury Road',
            'Guardians of the Galaxy',
            'Interstellar',
            'Inception',
            'Dune',
            'Barbie',
            'The Wolf of Wall Street',
            'Oppenheimer',
            'The Social Network',
        }
        movies = [movie for movie in movies if movie['title'] in required_titles]

        for data in movies:
            people.setdefault(data['director'], Person.objects.get_or_create(name=data['director'])[0])
            for actor_name in data['cast']:
                people.setdefault(actor_name, Person.objects.get_or_create(name=actor_name)[0])

        created_movies = []
        for data in movies:
            movie = Movie.objects.create(
                title=data['title'],
                release_year=data['year'],
                director=people[data['director']],
                poster_url=data['poster_url'],
                synopsis=data['synopsis'],
            )
            movie.genres.add(genres[data['genre']])
            movie.cast.add(*(people[name] for name in data['cast']))
            created_movies.append(movie)

        for index, movie in enumerate(created_movies):
            scores = [5, 4, 3 + (index % 3)]
            for score in scores:
                Rating.objects.get_or_create(movie=movie, score=score, comment=f'Valoracion {score}/5')

        self.stdout.write(self.style.SUCCESS('Datos del laboratorio creados.'))
        self.stdout.write('Peliculas creadas: 10')
        self.stdout.write('Superusuario: admin / Admin12345')
        self.stdout.write('Editor: editor / Editor12345')
