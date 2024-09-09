import requests
from bs4 import BeautifulSoup
import lxml

import json
import config

session = requests.Session()

url_login_get = "https://us.gblnet.net/"
url_login = "https://us.gblnet.net/body/login"

HEADERS = {
    "main": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0"
}

data_users = {
    "_csrf": '',
    "return_page": "",
    "username": config.loginUS,
    "password": config.pswUS
}

# Создание сессии, получение токена и авторизация

session_users = requests.Session()
print(f"session_users {session_users}")

req = session_users.get(url_login_get)

soup = BeautifulSoup(req.content, 'html.parser')
print("###################")
scripts = soup.find_all('script')
csrf_token = None
for script in scripts:
    if script.string is not None:
        # print(script.string)
        script_lst = script.string.split(" ")
        # print(script_lst)
        for num, val in enumerate(script_lst):
            if val == "_csrf:":
                csrf = script_lst[num + 1]
                csrf_token = csrf[1:-3]
print(f"csrf {csrf_token}")


def create_users_sessions():
    while True:
        try:
            data_users["_csrf"] = csrf_token
            print(f"data_users {data_users}")
            response_users2 = session_users.post(url_login, data=data_users, headers=HEADERS).text
            print("Сессия Юзера создана 2")
            print(f"response_users2 {response_users2}")
            return response_users2
        except ConnectionError:
            print("Ошибка создания сессии")
            # TODO функция отправки тут отсутствует
            # send_telegram("Ошибка создания сессии UserSide, повтор запроса через 5 минут")
            # time.sleep(300)


response_users = create_users_sessions()


def get_html(to):
    url = "https://us.gblnet.net/task/"
    link_west = (f"https://us.gblnet.net/task_list?task_state0_value=1&filter_selector0=task_state&"
                 f"task_state0_value=1&filter_selector1=task_type&task_type1_value%5b%5d=31&"
                 f"task_type1_value%5b%5d=1&task_type1_value%5b%5d=41&filter_selector2=task_division_w_staff&"
                 f"task_division_w_staff2_value=68&filter_selector3=additional_field_task&"
                 f"additional_field_task3_value4=193&additional_field_task3_value2=99&"
                 f"additional_field_task3_value99=%d0%ad%d0%bb%d0%b5%d0%ba%d1%82%d1%80%d0%be%d0%bd%d0%a2%d0%b5%d0%bb%d0%b5%d0%ba%d0%be%d0%bc&"
                 f"additional_field_task3_value=&desc=1&sort=datedo&sort_typer=1")
    link_north = (f"https://us.gblnet.net/task_list?task_state0_value=1&filter_selector0=task_state&"
                 f"task_state0_value=1&filter_selector1=task_type&task_type1_value%5b%5d=31&"
                 f"task_type1_value%5b%5d=1&task_type1_value%5b%5d=41&filter_selector2=task_division_w_staff&"
                 f"task_division_w_staff2_value=69&filter_selector3=additional_field_task&"
                 f"additional_field_task3_value4=193&additional_field_task3_value2=99&"
                 f"additional_field_task3_value99=%d0%ad%d0%bb%d0%b5%d0%ba%d1%82%d1%80%d0%be%d0%bd%d0%a2%d0%b5%d0%bb%d0%b5%d0%ba%d0%be%d0%bc&"
                 f"additional_field_task3_value=&desc=1&sort=datedo&sort_typer=1")
    print(link_west)

    link = ""
    if to == "west":
        link = link_west
    elif to == "north":
        link = link_north

    # Список всех заявок для поиска совпадений по времени, а так же отправки новых.
    list_old_numbers_date = []
    list_new_numbers_date = []
    list_all_old = []
    list_all = []

    # Список номеров заявок необходимо прочитать из файла.
    try:
        with open(f'{to}/list_numbers.json', 'r') as f:
            list_old_numbers_date = json.load(f)
        print("Список номеров заявок обновлен из файла")
        print(f"list_numbers {list_old_numbers_date}")
    except FileNotFoundError:
        print(f"Файл '{to}/list_numbers.json' не найден")

    # Список всех заявок для обработки дублей
    try:
        with open(f'{to}/list_all.json', 'r') as f:
            list_all_old = json.load(f)
        print("Список заявок обновлен из файла 'list_all.json'")
        print(f"list_all_old {list_all_old}")
    except FileNotFoundError:
        print(f"Файл '{to}/list_all.json' не найден.")


    try:
        print("Проверяем сессию. 1")
        HEADERS["_csrf"] = csrf_token
        print(f"HEADERS: {HEADERS}")
        print("Пытаемся получить страничку")
        print(f"Токен: {csrf}")
        html = session_users.get(link, headers=HEADERS)
        answer = []
        if html.status_code == 200:
            print("Код ответа 200")
            soup = BeautifulSoup(html.text, 'lxml')
            # print(f"soup {soup}")
            table = soup.find_all('tr', class_="cursor_pointer")
            print(f"Количество карточек: {len(table)}")
            for i in table:  # Цикл по списку всей таблицы
                txt_msg_one = ""
                # print(i)

                # Поиск ссылок, а среди них номер сервиса.
                list_a = i.find_all('a')  # Ищем ссылки во всей таблице
                conn_link = ""
                number_conn = ""
                for ii in list_a:  # Цикл по найденным ссылкам
                    if len(ii.text) == 7:  # Ищем похожесть на ид ремонта
                        number_conn = ii.text
                        conn_link = url + number_conn
                # print(f"number_conn {number_conn}")

                # Дата назначение
                ceil_date = i.find(id=f"td_{number_conn}_datedo_full_Id")
                # Вырежем слово "просрочено" из даты, если оно есть.
                # Без даты игнорируем.
                if ceil_date.text.strip() == "-":
                    continue
                elif ceil_date.text[-11:-1].strip() == "просрочено":
                    date = ceil_date.text[:-11].strip()
                else:
                    date = ceil_date.text.strip()

                # Адрес
                ceil_address = i.find(id=f"td_{number_conn}_address_full_Id")
                address = ceil_address.text.strip()
                address_split = address.split(" ")
                address_arr = []
                # "Удаляем" с нового списка с адресом пустые элементы
                for s in address_split:
                    if s != '':
                        address_arr.append(s)
                    else:
                        break
                # Обьединяем список с адресом в нормальную строку
                address_f = ' '.join(address_arr)

                # Если номер уже есть в списке, то пропускаем итерацию.
                # Делаем это в конце, т.к. необходим еще поиск дублей и перенесенных заявок.
                one_to_list_all = [date, address_f, conn_link]
                list_all.append(one_to_list_all)

                num_date = number_conn + " " + date
                list_new_numbers_date.append(num_date)
                if num_date in list_old_numbers_date:
                    continue
                print(f"new number_conn {number_conn}")

                # Проверка на дубли
                # Выше мы не вышли из итерации, поскольку заявка свежая, можем делать поиск совпадений.
                text_err = ""
                for z in list_all_old:
                    if date == z[0]:
                        # Найдено совпадение по времени, добавим текст.
                        text_err += (f"{z[0]}\n\n"
                                     f"{z[1]}\n\n"
                                     f"{z[2]}\n\n"
                                     f"------------------------------------------\n\n")
                if text_err != "":
                    text_err = ("------------------------------------------\n\n"
                                "Внимание, обнаружено совпадение по времени со следующими заявками.\n\n") + text_err

                # Для автоопределения новая или перенесенная нужна еще одна запись в файл.
                # Поэтому сначала надо понять если ли в это необходимость.
                txt_msg_new = (f"Обнаружена новая или перенесенная заявка:\n\n"
                               f"{date}\n\n"
                               f"{address_f}\n\n"
                               f"{conn_link}\n\n")
                answer.append(txt_msg_new + text_err)

                print(one_to_list_all)

        # Обновим json
        try:
            with open(f"{to}/list_numbers.json", 'w') as f:
                json.dump(list_new_numbers_date, f, sort_keys=False, ensure_ascii=False, indent=4, separators=(',', ': '))
                print(f"Файл '{to}/list_numbers.json' обновлен.")
        except FileNotFoundError:
            print(f"Файл '{to}/list_numbers.json' не найден.")

        try:
            with open(f"{to}/list_all.json", 'w') as f:
                json.dump(list_all, f, sort_keys=False, ensure_ascii=False, indent=4, separators=(',', ': '))
                print(f"Файл '{to}/list_all.json' обновлен.")
        except FileNotFoundError:
            print(f"Файл '{to}/list_all.json' не найден.")

        return answer

    except:
        # create_users_sessions()
        print("Произошла ошибка сессии, бот залогинится снова, "
              "попробуйте выполнить запрос позже, возможно программа даже не сломалась.")
        return ["Произошла ошибка сессии, бот залогинится снова, "
                "попробуйте выполнить запрос позже, возможно программа даже не сломалась."]