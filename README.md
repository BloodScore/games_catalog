# Games Muster
Training project for internship in ItechArt

## What's it about?
This is Django application which is games catalog. User can search games stored in database using various filters and add them to favourites. There is a detailed page for each game, where user can explore more information about single game such as game description, release date, screenshots, ratings and tweets with #game_name as the hashtag

## API
There is REST API created for this project. It can be accessed by /api route. There are 4 endpoints:
- `profile` - authorized user can get information about his profile
- `games` - list of games stored in database
- `game_detailed` - detailed information about single game
- `must_games` - authorized user can get list of his favourite games. At this endpoint user can also add and remove game from his favourites passing `{ "game_id": <number> }` to post-request. If game with passed `game_id` is already in favourites, it will be removed, if not - it will be added.

## External APIs
This application uses some external APIs.
The first is [IGDB API](https://api-docs.igdb.com/). It is used to retrieve list of games. Then these games are stored in application database. To do this Celery and Redis are used. They are starting to run as soon as app docker container runs.
The second is [Twitter Api](https://developer.twitter.com/en/docs/twitter-api), which is used for retrieving tweets about single game.

## Installation and deploy
There are some steps bellow which you should follow to install and deploy this app.
1. Clone project code using
`$ git clone https://github.com/BloodScore/games_catalog.git`
2. Open terminal and cd to ../games_catalog folder.
3. Run pip install -r requirements.txt
4. In project root folder find the `.env.template` file. 
5. Rename it to `.env`
6. Set `IGDB_CLIENT_ID` and `IGDB_ACCESS_TOKEN` following [this](https://api-docs.igdb.com/#account-creation) guide.
7. Set `TWITTER_BEARER_TOKEN` following [this](https://developer.twitter.com/en/docs/twitter-api/getting-started/getting-access-to-the-twitter-api) guide.
8. Set `DB_NAME`, `DB_USERNAME` and `DB_PASSWORD` to whatever you want.
9. Set `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` for smtp-server. It is used for sending letters to users after registration and resetting password.
10. Set `DEBUG` option to 0 in order to use app in production or to 1 to use it in development.
11. Set `SECRET_KEY` from `games_catalog/settings.py`
12. Set `DJANGO_ALLOWED_HOSTS` to which you need
13. Set `SCHEDULE` to time in milliseconds. This parameter is used to configure the frequency of celery tasks.
14. Save this file and open `docker-compose.yml`
15. At `services-db-environment` set `POSTGRES_USER`, `POSTGRES_PASSWORD` and `POSTGRES_DB` same as parameters at step 8.
16. Build and run docker containers using command `sudo docker-compose up --build`
17. Run command `docker-compose exec web python manage.py migrate` to apply database migrations
18. Run command `docker-compose exec web python manage.py createsuperuser` to create admin user for application
19. Thats it!

## List of technologies
- Python
- Django
- Django REST Framework
- PostgreSQL
- Celery
- Redis
- Docker

## Demo
[Here](https://games-muster.herokuapp.com/) you can see working site and explore all the functions
