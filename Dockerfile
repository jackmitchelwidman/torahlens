# Stage 1: build the React frontend
FROM node:20-bookworm-slim AS frontend
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

# Stage 2: Python runtime serving API + static build
FROM python:3.10-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PORT=8080
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./backend/
COPY --from=frontend /app/frontend/build ./backend/build
EXPOSE 8080
CMD ["sh", "-c", "gunicorn -b 0.0.0.0:${PORT} --workers 2 --timeout 120 backend.app:app"]
