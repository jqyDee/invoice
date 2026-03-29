FROM python:3.11-slim

WORKDIR /app

# Install backend dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Copy backend source
COPY app ./app
COPY assets ./assets

EXPOSE 8000

CMD ["sh", "-c", "alembic -c app/alembic.ini upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]


