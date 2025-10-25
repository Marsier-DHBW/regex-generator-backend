# Basis-Image mit Python
FROM python:3.12.3
WORKDIR /app
ENV Backend.API.URL="0.0.0.0"
ENV Backend.API.PORT="8000"
ENV Backend.API.ENDPOINT="/v1/api/endpoint"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "main.py"]