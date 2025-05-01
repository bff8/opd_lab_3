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
            'RUB': 82.0,  # 1 USD = 82 RUB
            'KZT': 420.0  # 1 USD = 420 KZT
        }


# Декоратор route определяет URL-адрес, по которому будет доступна страница
# methods указывает, какие HTTP-методы принимает этот маршрут (GET и POST)
@app.route('/', methods=['GET', 'POST'])
def index():
    # Получаем текущие курсы валют
    currencies = get_currency_rates()
    result = None  # Переменная для хранения результата конвертации
    error_message = None  # Переменная для хранения сообщения об ошибке

    # Проверяем, был ли запрос POST (отправка формы)
    if request.method == 'POST':
        try:
            # Получаем данные из формы:
            amount_str = request.form.get('amount', '1').strip()

            # Проверяем, что введено число
            try:
                amount = float(amount_str)
            except ValueError:
                error_message = "Пожалуйста, введите корректное число"
                amount = None

            # Проверяем, что число положительное
            if amount is not None and amount <= 0:
                error_message = "Введите положительное количество денег"
                amount = None

            # Проверяем, что введено не слишком большое число
            if amount is not None and amount > 1_000_000_000:
                error_message = "Сумма слишком большая для конвертации"
                amount = None

            # Получаем валюты
            from_currency = request.form.get('from_currency', 'USD')
            to_currency = request.form.get('to_currency', 'EUR')

            # Проверяем, что обе валюты есть в нашем словаре курсов
            if (amount is not None and from_currency in currencies
                    and to_currency in currencies):
                # Вычисляем результат
                result = amount * (currencies[to_currency] / currencies[from_currency])

        except Exception as e:
            error_message = f"Ошибка при конвертации: {str(e)}"

    return render_template(
        'index.html',
        currencies=sorted(currencies.keys()),
        result=round(result, 2) if result is not None else None,
        error_message=error_message,
        form_data=request.form  # Передаем данные формы для сохранения введенных значений
    )


# Стандартная проверка для запуска приложения только при прямом вызове файла
if __name__ == '__main__':
    # Запускаем Flask-приложение с режимом отладки (debug=True)
    app.run(debug=True)