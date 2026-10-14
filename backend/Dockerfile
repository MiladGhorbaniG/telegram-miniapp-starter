FROM python:3.12-slim

WORKDIR /app

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY backend /app/backend
COPY sample_data ./sample_data

WORKDIR /app/backend

ENV PYTHONPATH=/app/backend:/app/src
ENV FAQ_PATH=/app/sample_data/faq.json
ENV DJANGO_DEBUG=1
ENV DJANGO_SECRET_KEY=dev-only-booknook-key

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
