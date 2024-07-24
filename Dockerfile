# Python 3.9 imajını kullan
FROM python:3.9

# Çalışma dizinini ayarla
WORKDIR /app

# Gereken Python paketlerini yükle
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Python kodunu container'a kopyala
COPY app.py app.py

# Python scriptini çalıştır
CMD ["python", "app.py"]
