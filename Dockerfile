# Первый этап: сборка зависимостей и создание требований
FROM python:3.10.11-slim-buster AS builder

# Копируем исходный код приложения
WORKDIR /usr/src/ai_interviwer/
COPY src /usr/src/ai_interviwer/src
COPY poetry.lock pyproject.toml .

# Устанавливаем Poetry и экспортируем зависимости в файл requirements.txt
RUN pip install --no-cache-dir poetry && \
    poetry install --no-root && \
    poetry run pip freeze > requirements.txt

# Второй этап: создание финального образа
FROM python:3.10.11-alpine

# Копируем требования из первого этапа
COPY --from=builder /usr/src/ai_interviwer/requirements.txt .

# Установливаем инструменты сборки и заголовочные файлы
RUN apk update && apk add --no-cache \
    build-base \
    gcc \
    make \
    linux-headers

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходники без лишних файлов
COPY src /usr/src/ai_interviwer/src

# Устанавливаем рабочую директорию
WORKDIR /usr/src/ai_interviwer/

# Устанавливаем переменную окружения
ENV PYTHONPATH=/usr/src/ai_interviwer/

# Устанавливаем curl
# Загружаем сертификат для взаимодействия с GigaChatAPI
RUN apk add --no-cache curl && \
    curl -k "https://gu-st.ru/content/Other/doc/russian_trusted_root_ca.cer" -w "\n" >> $(python -m certifi)
