FROM python:3.13-slim

# Створюємо робочу директорію
WORKDIR /app

# Копіюємо requirements.txt і встановлюємо залежності
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо увесь код
COPY . .

# Вказуємо команду для запуску бота
CMD ["python", "tg_bot.py"]
