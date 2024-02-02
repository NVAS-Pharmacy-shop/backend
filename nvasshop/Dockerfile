FROM python:3
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
#RUN chmod +x /code/wait-for-it.sh
#RUN ./wait-for-it.sh db:5432
#RUN python manage.py makemigrations
#RUN python manage.py migrate
# Uncomment the following lines to run migrations only after the database is ready
#CMD ["./wait-for-it.sh", "db:5432"]
#RUN python manage.py makemigrations
#RUN python manage.py migrate
#RUN python manage.py start_commands
#CMD gunicorn --bind 0.0.0.0:3000 --workers 3 nvasshop.wsgi:application
RUN chmod +x /code/start.sh
ENTRYPOINT ["sh", "-c", "./start.sh"]


