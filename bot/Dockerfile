FROM python:3.12-slim

WORKDIR /app

COPY bot/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY bot/booknook_bot ./booknook_bot
COPY sample_data ./sample_data

ENV PYTHONPATH=/app/src
ENV FAQ_PATH=/app/sample_data/faq.json
ENV BOT_HEALTH_PORT=8081

EXPOSE 8081

CMD ["python", "-m", "booknook_bot"]
