
down:
	docker-compose down -v
up:
	docker-compose -f docker-compose.yml up -d --build
run:
	docker-compose -f docker-compose.yml exec web python manage.py migrate --noinput
static:
	docker-compose -f docker-compose.yml exec web python manage.py collectstatic --no-input --clear
