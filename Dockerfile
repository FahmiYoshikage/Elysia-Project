# 1. Mulai dari image Python resmi
FROM python:3.14-slim

# 2. Set folder kerja di dalam container
WORKDIR /app

# 3. Salin file requirements Anda (Anda bisa buat dari pip list)
# (Jalankan "pip freeze > requirements.txt" dulu di terminal Anda)
COPY requirements.txt .

# 4. Install semua dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Salin sisa kode proyek Anda ke dalam container
COPY . .

# 6. Perintah untuk menjalankan aplikasi Anda saat container start
CMD ["python", "Elysia-gmn.py"]