from python:3.9

ENV PYTHONPATH "${PYTHONPATH}:/app"

RUN pip install --upgrade pip

WORKDIR /app/

COPY requirements.txt

RUN pip install -r requirements.txt

COPY src/ src/