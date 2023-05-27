# Проект парсинга pep
## Парсер документации Python

### Как запустить проект:
Чтобы развернуть проект, вам потребуется:
1) Клонировать репозиторий GitHub (не забываем создать виртуальное окружение и установить зависимости):
```python
git clone https://github.com/AlDzu/foodgram-project-react
```

2) Cоздать и активировать виртуальное окружение:
```python
python3 -m venv venv
source venv/bin/activate
```
3) Установить зависимости:
```python
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```
## Примеры команд
Вывод информации нововведениях в python:
```
python main.py whats-new
```
Вывод информации о нововведениях в форме "Ссылка на документацию", "Версия", "Статус":
```
python main.py latest-versions
```
Скачивает zip архив с документацией Рython:
```
python main.py download
```
Вывод списка статусов документов РЕР и количества в каждом статусе:
```
python main.py pep
```
### Аргументы
Справка:
```
-h, --help
```
Очистить кеш:
```
-c, --clear-cache
```
Изменить вывод результата:
```
-o {pretty,file}, --output {pretty,file}
pretty представление в табличном виде
file сохранить в файле .csv
```
