# Su dung Python 3.10 ban nhe
FROM python:3.10-slim

# Dat thu muc lam viec trong container
WORKDIR /app

# Copy va cai dat thu vien
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toan bo code vao container
COPY . .

# Chay file main.py khi Docker khoi dong, roi thoat
CMD ["python", "main.py"]