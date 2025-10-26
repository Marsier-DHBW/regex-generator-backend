# Basis-Image mit Python
FROM python:3.12.12-slim-trixie
WORKDIR /app
ENV URL="0.0.0.0"
ENV PORT=8000
ENV ENDPOINT="/v1/api/endpoint"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE ${PORT}
CMD ["python", "main.py"]