# Movie Library application

## Работа с приложением

### Требования

Необходимо, чтобы были установлены следующие компоненты:

- `Docker` и `docker-compose`
- `Python 3.12`
- `Poetry`

### Установка

1. Создание виртуального окружения и установка зависимостей
```commandline
poetry install
```

2. Активация виртуального окружения

```commandline
poetry shell
```


### Запуск

0. Создать `.env` файл с этими переменными (можно командой `make env`)
```dotenv
POSTGRES_DB=...
POSTGRES_USER=...
POSTGRES_PASSWORD=...
POSTGRES_HOST=...
POSTGRES_PORT=5432
```

2. Создание базы в docker-контейнере:
```commandline
make db
```
2. Выполнение миграций:
```commandline
make migrate head
```
3. Запуск приложения:
```commandline
make run
```

Посмотреть документацию можно после запуска приложения по адресу `http://127.0.0.1:8080/swagger`.
### Тестирование

- Запуск тестов со всеми необходимыми флагами:
```commandline
make test
```

- Запуск тестов с генерацией отчета о покрытии:
```commandline
make test-cov
```

### Статический анализ

- Запуск линтеров
```commandline
make lint
```

- Запуск форматирования кода
```commandline
make format
```

### Дополнительные команды

- Создание новой ревизии:
```commandline
make revision
```
