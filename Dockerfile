FROM python:3.10

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt


EXPOSE 8000
# CMD ["flask", "run"]

WORKDIR /app/project
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]