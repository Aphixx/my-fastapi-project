# Python version

FROM python:3.11-slim

# Working folder

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

# Port

EXPOSE 8000

# Run command

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]