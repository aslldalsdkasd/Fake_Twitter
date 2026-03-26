FROM python:3.13-slim


RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /app
COPY . /app


COPY server/requirements.txt /app/server/requirements.txt
RUN pip install --no-cache-dir -r /app/server/requirements.txt


ENV PYTHONPATH=/app

WORKDIR /app/server
EXPOSE 5000

CMD ["uvicorn", "api.fast_app:app", "--host", "0.0.0.0", "--port", "5000"]