# VISORA backend — FastAPI + psycopg3 (binary wheels, no build deps needed)
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# Strip possible CRLF (Windows) so the shebang works on Linux, then make executable.
RUN sed -i 's/\r$//' entrypoint.sh && chmod +x entrypoint.sh

EXPOSE 8000
CMD ["./entrypoint.sh"]
