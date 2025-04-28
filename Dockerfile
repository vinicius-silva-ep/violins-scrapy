FROM python:3.12.6

WORKDIR /app

COPY  . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "app.py"]