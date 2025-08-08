FROM python:3.10-slim

WORKDIR /workdir

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

CMD ["python", "/app/connector.py"]
