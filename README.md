# SMS Gate

SMS-шлюз для отправки и приёма SMS через Android-телефон, подключённый к macOS по USB.

## Архитектура

```
Клиент → [FastAPI :8095] → [ADB USB forward :8081] → [Android SMS Gateway app] → SMS
                         ← webhook входящих SMS ←
```

- **macOS**: FastAPI-сервер (REST API), ADB port forwarding
- **Android**: приложение SMS Gateway (capcom6/android-sms-gateway), подключение по USB
- Интернет приходит НЕ через телефон — телефон только для SMS

## Стек

- Python 3.12+, FastAPI, httpx, Pydantic
- ADB (Android SDK Platform Tools)
- Android SMS Gateway app

## Быстрый старт

```bash
pip install -r requirements.txt
cp .env.example .env
# Подключить Android по USB, включить отладку
python main.py          # http://localhost:8095
```

## API

```
POST /sms/send      — отправка SMS
GET  /sms/status     — статус шлюза
POST /webhook/sms    — входящие SMS (callback)
```

## Структура

```
main.py      # Точка входа FastAPI
gateway.py   # Логика отправки/приёма SMS
adb.py       # ADB port forwarding
config.py    # Настройки из .env
models.py    # Pydantic-модели
```
