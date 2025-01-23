AI-помощник для подготовки к интервью Middle Python-разработчика. Работает на основе GigaChat.

### Инструкция для быстрого запуска в контейнере
1. Скачать исходники из репозитория
2. Создать файл `.env` из шаблона `template.env`
3. Запустить `docker compose up --build` для сборки образа 
4. Для первого запуска написать `/start`, для последующих — `/get_question` в боте или воспользоваться кнопками

### Инструкция для быстрого запуска локально
1. Указать в .env тестовый `TG_TOKEN` и `DB_HOST=localhost` для локалки
2. Запустить контейнер базы данных:
`docker run --name pg-container -e POSTGRES_DB=inter_db -e POSTGRES_USER=inter_user -e POSTGRES_PASSWORD=inter_password -p 5432:5432 -d postgres:15`
3. Запустить контейнер Redis:
`docker run -d -p 6379:6379 --name redis_local redis_local`
4. Скачать сертификат Минцифры (на Mac):
`curl -k "https://gu-st.ru/content/Other/doc/russian_trusted_root_ca.cer" -o russian_trusted_root_ca.cer`
5. Установить сертификат:
`cat russian_trusted_root_ca.cer >> $(python -m certifi)`
6. Запустить main.py, можно прямо из консоли

### Профилирование кода
1. Для проверки асинхронности можно запустить `pyinstrument`:
`PYTHONPATH=. pyinstrument src/main.py -t -r RENDERER`
2. Для общего профилирования — `scalene`:
`scalene --cpu --memory --cli src/main.py`