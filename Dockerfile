FROM python:3.10-slim

WORKDIR /app

# Tizim uchun kerakli paketlarni o'rnatish
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Python kutubxonalarini o'rnatish
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Loyiha fayllarini nusxalash
COPY . .

# Portni sozlash va ilovani ishga tushirish (Hugging Face 7860 portini ishlatadi)
EXPOSE 7860
CMD ["gunicorn", "-b", "0.0.0.0:7860", "wsgi:app"]