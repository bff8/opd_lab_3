# Импорт необходимых модулей
from flask import Flask, render_template, \
    request  # Flask - фреймворк, render_template - для работы с HTML, request - для обработки запросов
import requests  # Для выполнения HTTP-запросов к API курсов валют

# Создание экземпляра Flask-приложения
app = Flask(__name__)  # __name__ - имя текущего модуля, нужно для Flask


# Функция для получения актуальных курсов валют
def get_currency_rates():
    try:
        # Отправляем GET-запрос к API курсов валют (базовая валюта - USD)
        response = requests.get('https://api.exchangerate-api.com/v4/latest/USD')
        data = response.json()  # Преобразуем ответ в формат JSON
        return data['rates']  # Возвращаем только часть с курсами валют
    except:
        # Если произошла ошибка (нет интернета или API недоступно), используем фиксированные курсы
        return {
            'USD': 1.0,  # 1 USD = 1 USD
            'EUR': 0.85,  # 1 USD = 0.85 EUR
            'RUB': 75.0,  # 1 USD = 75 RUB
            'KZT': 420.0  # 1 USD = 420 KZT
        }


# Декоратор route определяет URL-адрес, по которому будет доступна страница
# methods указывает, какие HTTP-методы принимает этот маршрут (GET и POST)
@app.route('/', methods=['GET', 'POST'])
def index():
    # Получаем текущие курсы валют
    currencies = get_currency_rates()
    result = None  # Переменная для хранения результата конвертации

    # Проверяем, был ли запрос POST (отправка формы)
    if request.method == 'POST':
        # Получаем данные из формы:
        # amount - сумма для конвертации (по умолчанию 1)
        amount = float(request.form.get('amount', 1))
        # from_currency - валюта, из которой конвертируем (по умолчанию USD)
        from_currency = request.form.get('from_currency', 'USD')
        # to_currency - валюта, в которую конвертируем (по умолчанию EUR)
        to_currency = request.form.get('to_currency', 'EUR')

        # Проверяем, что обе валюты есть в нашем словаре курсов
        if from_currency in currencies and to_currency in currencies:
            # Вычисляем результат: amount * (курс целевой валюты / курс исходной валюты)
            result = amount * (currencies[to_currency] / currencies[from_currency])

    # Рендерим HTML-шаблон и передаем в него данные:
    # currencies - список доступных валют, отсортированный по алфавиту
    # result - результат конвертации, округленный до 2 знаков после запятой (или None, если конвертация не проводилась)
    return render_template(
        'index.html',
        currencies=sorted(currencies.keys()),
        result=round(result, 2) if result is not None else None
    )


# Стандартная проверка для запуска приложения только при прямом вызове файла
if __name__ == '__main__':
    # Запускаем Flask-приложение с режимом отладки (debug=True)
    app.run(debug=True)

# При запуске приложение будет доступно по адресу http://127.0.0.1:5000/
# (localhost на порту 5000)