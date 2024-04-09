FROM python:3.10-bullseye
COPY . .
RUN pip install -r requirements.txt
RUN pip install psycopg2-binary
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]