FROM python:3.11

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

CMD ["python", "-m","flask", "run", "--host=0.0.0.0"]