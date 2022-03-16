FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

ENV PYTHONPATH "${PYTHONPATH}:/app"

RUN pip install --upgrade pip

WORKDIR /app/

COPY requirements.txt cert.pem key.pem sqlite_db .

RUN pip install -r requirements.txt

COPY src/ src/

CMD ["python", "./src/app/app.py"]

EXPOSE 80
