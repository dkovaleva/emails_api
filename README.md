API Reference

1)Создание письма:

ФОРМАТ ЗАПРОСА

method = POST
URL = 'http://127.0.0.1:8000/emails/send_email/'

data = {
	'header': "", /заголовок
	'content': "", /текст
	'From': 'test@mail.ru', /валидный email адрес отправителя
	'To': 'user1@mail.ru,user2@gmail.com,user3@list.ru'/список email адресов получателей через запятую
}

ФОРМАТ ОТВЕТА (ответ в json)

status_code = 200

json = {
	'result': 'OK'/'Fail',
	'msg': ***,
	'description': ***,/опционально в случае ошибки (например, передана строка, не являющаяся email адресом и т.п.)
}


2)Посмотреть список отправленных писем (каталог sent конкретного юзера)

ФОРМАТ ЗАПРОСА

method = GET

URL = 'http://127.0.0.1:8000/emails/sentbox/'

data = {
	'email_address': 'test@mail.ru' /email адрес юзера, чьи письма просматриваем
}

ФОРМАТ ОТВЕТА

status_code = json

json = [{'id': id_письма, 'header': заголовок_письма}, {'id': ***, 'header': ***}, ...]

ЛИБО status_code=404, если юзер с таким емейлом не найден в системе

3)Посмотреть список полученных писем (каталог inbox конкретного юзера)

ФОРМАТ ЗАПРОСА

method = GET

URL = 'http://127.0.0.1:8000/emails/inbox/'

data = {
	'email_address': 'test@mail.ru' /email адрес юзера, чьи письма просматриваем
}

ФОРМАТ ОТВЕТА

status_code = 200

json = [{'id': id_письма, 'header': заголовок_письма, 'from': email_отправителя, 'is_read': прочитано_или_нет}, {...}, {...}] /список словарей, каждый словарь = письмо

ЛИБО
status_code = 404 если юзер с таким емейлом не найден в системе

4)Посмотреть детали письма

ФОРМАТ ЗАПРОСА:
method = GET
URL = 'http://127.0.0.1:8000/emails/detail/ID_ПИСЬМА/', например
URL = 'http://127.0.0.1:8000/emails/detail/1/'

ФОРМАТ ОТВЕТА

status_code = 404 если письмо с таким id не найдено

или

status_code = 200

json = {
	'id': id_письма,
	'header': заголовок_письма,
	'content': содержание_письма,
	'from': email адрес отправителя,
	'to': список email адресов получателей
}

5)Пометить письмо как прочитанное/не прочитанное

ФОРМАТ ЗАПРОСА
method = POST

URL = 'http://127.0.0.1:8000/emails/mark_email/ID_ПИСЬМА/', например
'http://127.0.0.1:8000/emails/mark_email/1/'

data = {
	'email_address': 'receiver@mail.ru', /email адрес юзера, который помечает письмо как прочитанное
	'is_read': "0" или "1", /"1" если помечаем как прочитанное, "0" если как непрочтанное
}

ФОРМАТ ОТВЕТА

status_code = 200

json = {
	'result': 'OK'/'Fail',
	'msg': ***,
	'description': ***/опционально в случае ошибки (переданы неверные данные и т.п.)
}

5)Удалить письмо из своего inbox каталога

ФОРМАТ ЗАПРОСА

method = POST

URL = 'http://127.0.0.1:8000/emails/remove/ID_ПИСЬМА/', например
'http://127.0.0.1:8000/emails/remove/1/'

data = {
	'email_address': 'receiver@mail.ru', /email адрес юзера, который удаляет письмо из своих входящих
}

ФОРМАТ ОТВЕТА

status_code = 200

json = {
	'result': 'OK'/'Fail',
	'msg': ***,
	'description': ***/опционально при попытке удалить письмо, которого и так нет во входящих и т.п.
}
