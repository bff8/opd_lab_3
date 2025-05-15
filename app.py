from flask import Flask, render_template, request # Веб-фреймворк для создания сайтов, отображения HTML, данными, которые приходят от пользователя
import requests #HTTP-запросы
app = Flask(__name__) # Инициализация приложения + запуск скрипта
def get_currency_rates():# Получает курсы валют с API или возвращает запасные курсы
    try:
        # Делаем HTTP GET-запрос, чтобы получить последние курсы валют с базовой валютой USD (доллар). Ответ сохраняется в переменной response
        response = requests.get('https://api.exchangerate-api.com/v4/latest/USD')
        # Преобразуем ответ от API в Python-словарь с помощью метода response.json(). Результат сохраняем в переменную data.
        data = response.json()
        # Возвращаем только словарь rates из ответа API, где хранятся курсы валют относительно доллара.
        return data['rates']
    # Ловим любые ошибки (except без указания типа ловит ВСЁ, что плохо
    except:
        # Если API не сработал, возвращаем запасной словарь с hardcoded
        return {
            'USD': 1.0,
            'EUR': 0.85,
            'RUB': 82.0,
            'KZT': 420.0
        }
# Определяем маршрут (route) для главной страницы с помощью @app.route. Указываем, что этот маршрут
# обрабатывает запросы когда пользователь просто заходит на страницу и когда пользователь отправляет форму.
@app.route('/', methods=['GET', 'POST'])
# Обрабатывает запросы к главной странице и содержит всю логику для отображения страницы
def index():
    # Вызываем функцию, чтобы получить курсы валют и сохраняем результат
    currencies = get_currency_rates()
    # Инициализируем переменную result как None. Она будет хранить результат конвертации
    result = None
    # Инициализируем переменную error_message как None. Она будет хранить сообщение об ошибке
    error_message = None
    # По умолчанию для decimal_places равным 2 - знаки после запятой.
    decimal_places = 2
    # Проверяем, является ли запрос POST-запросом (то есть пользователь отправил форму).
    # request.method — ('GET' или 'POST'), которая берётся из объекта request, содержащего информацию о HTTP-запросе.
    if request.method == 'POST':
        try:
            # request.form — это словарь с данными формы (ключ — имя поля, значение — введённые данные).
            # Метод .get() берёт значение по ключу 'decimal_places', а если ключа нет, возвращает 2
            # Преобразуем значение в целое число (int), так как оно приходит как строка.
            decimal_places = int(request.form.get('decimal_places', 2))
            # Получаем значение поля amount из формы (сумма для конвертации) с помощью request.form.get('amount', '1').
            # Если поле amount пустое, берём '1' по умолчанию. Метод strip() убирает пробелы в начале и конце строки
            amount_str = request.form.get('amount', '1').strip()
            # Начинаем вложенный try, чтобы поймать ошибку, если пользователь ввёл не число (например, "abc").
            try:
                # Пробуем преобразовать строку amount_str в float и сохранить в amount.
                amount = float(amount_str)
            # Ловим ValueError, который возникает, если строка не является числом (например, "abc" или пустая строка).
            except ValueError:
                error_message = "Пожалуйста, введите корректное число"
                amount = None # Устанавливаем amount в None, чтобы показать, что конвертация невозможна.
            # Проверяем, если amount не None (то есть преобразование в число прошло успешно) и сумма меньше или равна нулю.
            if amount is not None and amount <= 0:
                error_message = "Введите положительное количество денег"
                amount = None # Устанавливаем amount в None, чтобы не продолжать конвертацию.
            # Проверяем, если amount не None и сумма больше 1 миллиарда.
            if amount is not None and amount > 1_000_000_000:
                error_message = "Сумма слишком большая для конвертации"
                amount = None # Устанавливаем amount в None, чтобы не продолжать конвертацию.
            # Получаем валюту, из которой конвертируем (from_currency), из формы. Если поле не указано, берём 'USD' по умолчанию.
            from_currency = request.form.get('from_currency', 'USD')
            # Получаем валюту, в которую конвертируем (to_currency), из формы. Если поле не указано, берём 'EUR' по умолчанию.
            to_currency = request.form.get('to_currency', 'EUR')

            # Проверяем, что сумма корректна и что обе валюты есть в словаре currencies
            if (amount is not None and from_currency in currencies and to_currency in currencies):
                # Выполняем конвертацию: умножаем сумму на отношение курсов (курс целевой валюты / курс исходной валюты).
                result = amount * (currencies[to_currency] / currencies[from_currency])

        # Ловим любые ошибки, которые могут возникнуть при обработке формы (например, если decimal_places не число).
        except Exception as e:
            # Устанавливаем сообщение об ошибке, включая текст ошибки (str(e)), чтобы пользователь знал, что пошло не так.
            error_message = f"Ошибка при конвертации: {str(e)}"

    # Вызываем render_template, чтобы отобразить HTML-шаблон index.html. Передаём в шаблон данные:
    return render_template(
        'index.html',
        currencies=sorted(currencies.keys()), # - currencies: список валют
        result=round(result, decimal_places) if result is not None else None, # - result: результат конвертации, округлённый до decimal_places знаков
        error_message=error_message,# - error_message: сообщение об ошибке
        form_data=request.form, # - form_data: данные формы (request.form), чтобы сохранить введённые пользователем значения при перезагрузке страницы.
        decimal_places=decimal_places # - decimal_places: текущее значение количества знаков после запятой.
    )
# Проверяем, запущен ли скрипт напрямую (а не импортирован как модуль). __name__ будет "__main__", если скрипт запущен напрямую.
if __name__ == '__main__':
    # Запускаем Flask-приложение в режиме отладки (debug=True). Это включает автоматическую перезагрузку при изменении кода
    # и показывает подробные ошибки в браузере
    app.run(debug=True)