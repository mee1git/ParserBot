import telebot  # Импортируем библиотеку для работы с Telegram API
import requests  # Импортируем библиотеку для запросов к VK API
import botConfig  # Импортируем config бота, куда записаны токены
import os

from telebot import types  # Импортируем модуль для работы с кастомными клавиатурами
from telebot.types import InputMediaPhoto  # Импортируем модуль для работы метода SendMediaGroup


class VkParser:  # Создаём класс VkParser
    def __init__(self):  # Создаём конструктор класса
        self.__d = int(0)  # Индекс списка с доменами
        self.__domains = ['styd.pozor', 'stlbn', 'karkb', '4ch', 'reddit']  # Список доменов
        self.__domain = self.__domains[self.__d]  # Переменная для хранения домена, который используется
        self.__offset = int(0)  # Количество записей для смещения по стене

    def get_data(self):  # Функция парсинга данных со стены сообщества
        token = botConfig.vk_token  # Токен для обращения к VK API
        version = 5.103  # Версия VK API
        response = requests.get('https://api.vk.com/method/wall.get',  # Запрос данных при помощи метода wall.get
                                params=dict(access_token=token, v=version, domain=self.__domain, count=5,
                                            offset=self.__offset)
                                )
        data = response.json()['response']['items']  # Записываем ответ в перменную data в json формате, при этом
        return data  # выбирая только записи со стены, и возвращаем data

    def get_meme_text(self):  # Функция для получения текста с записей
        meme_text = ['', '', '', '', '']  # Создаём список из 5 элементов
        for i in range(5):  # Заполняем список в цикле
            if (self.get_data()[i]['text']) != '':  # Если в записи есть текст,
                meme_text[i] += str(self.get_data()[i]['text'])  # записываем его в список
            else:  # Если же нет,
                meme_text[i] += '...'  # записывем многоточие
        return meme_text  # Возвращаем список с текстами

    def get_meme_pic(self):  # Функция для получения картинок с записей
        meme_pic = [[], [], [], [], []]  # Создаём список из 5 списков
        for i in range(5):  # Заполняем список в цикле
            try:  # Проверка наличия дополнений к посту
                if self.get_data()[i]['attachments'][0]['type']:  # Если в записи есть картинки,
                    len_attachments = len(self.get_data()[i]['attachments'])  # проверяем их количестов и
                    for z in range(len_attachments):  # в цикле,
                        try:  # пытаемся записать их ссылки в отдельный элемент списка
                            meme_pic[i].append(str(self.get_data()[i]['attachments'][z]['photo']['sizes'][-1]['url']))
                        except KeyError:  # Если происходит ошибка значит, в записи находилось видео
                            meme_pic[i] = "Видео пока не доступно, извините"  # Оповещяем пользователя о видео
                else:  # Если кратинок нет,
                    meme_pic[i] = '...'  # записываем строку ... вместо списка
            except KeyError:  # Если происходит ошибка, значит дополнений не было
                meme_pic[i] = '...'  # записываем строку ... вместо списка
        return meme_pic  # Возвращаем список с ссылками на картинки

    def change_domain(self, index):  # Функция изменения домена
        self.__d = index  # Меняем индекс списка доменов
        self.__domain = self.__domains[self.__d]  # Обновляем значение домена

    def change_offset(self, new_offset):  # Функция изменения отступа записей
        if new_offset == 0:  # Если new_offset = 0
            self.__offset = new_offset  # Меняем на 0
        else:  # Если не равен нулю, прибавляем
            self.__offset += new_offset

    def get_domain_name(self):  # Функция для получения имени паблика по домену
        if self.__d == 0:                                                       # }
            return 'Позор'                                                      # }
        elif self.__d == 1:                                                     # }
            return 'Как я встретил столбняк'                                    # }
        elif self.__d == 2:                                                     # } По индексу d
            return 'Картинки категории Б'                                       # } возвращаем название паблика
        elif self.__d == 3:                                                     # }
            return '4CH'                                                        # }
        elif self.__d == 4:                                                     # }
            return 'Reddit'                                                     # }


bot = telebot.TeleBot(botConfig.tg_token)  # Создаём экземпляр бота
parser = VkParser()  # Создаём экзампляр парсера


def markup_set():  # Функция для создания клавиатуры
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)  # Объявляем экземпляр клавиатуры
    item1 = types.KeyboardButton('Позор')                     # }
    item2 = types.KeyboardButton('Как я встретил столбняк')   # }
    item3 = types.KeyboardButton('Картинки категории Б')      # } Объявляем кнопки
    item4 = types.KeyboardButton('4ch')                       # }
    item5 = types.KeyboardButton('Reddit')                    # }
    markup.add(item1, item2, item3, item4, item5)  # Добавляем кнопки на клавиатуру
    return markup  # Возвращаем клавиатуру


def markup2_set():  # Функция для создания клавиатуры2, аналогично первой
    markup2 = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item12 = types.KeyboardButton('get memes')
    item22 = types.KeyboardButton('back')
    markup2.add(item12, item22)
    return markup2


def inline_markup_set():  # Функция для создания inline клавиатуры, Reply меняем на Inline
    in_markup = types.InlineKeyboardMarkup(row_width=1)
    item0 = types.InlineKeyboardButton("more_memes", callback_data='more_memes')
    in_markup.add(item0)
    return in_markup


@bot.message_handler(commands=["start"])  # Обработка команды /start
def welcome(message):  # Функция приветствия
    markup = markup_set()  # Вызываем клавиатуру

    # Отправляем приветственное сообщение, прикрепив клавиатуру
    bot.send_message(message.chat.id, 'Хочешь почекать мемы? Тогда выбери паблик и нажми кнопку "get memes".\n' +
                     'Чтобы получить ещё 5 мемов, нажми кнопку "more memes"', reply_markup=markup)


@bot.message_handler(content_types=["text"])  # Обработка текстовых сообщений
def send_key(message):
    markup = markup_set()  # Вызываем клавиатуру
    markup2 = markup2_set()  # Вызываем клавиатуру2
    in_markup = inline_markup_set()  # Вызываем inline клавиатуру

    if message.text == 'Позор':                                                     # }
        bot.send_message(message.chat.id, 'Жми "get memes"', reply_markup=markup2)  # }
        parser.change_domain(index=0)                                               # }
    elif message.text == 'Как я встретил столбняк':                                 # }
        bot.send_message(message.chat.id, 'Жми "get memes"', reply_markup=markup2)  # }
        parser.change_domain(index=1)                                               # }
    elif message.text == 'Картинки категории Б':                                    # } Обрабатываем паблик
        bot.send_message(message.chat.id, 'Жми "get memes"', reply_markup=markup2)  # } Изменяем домен
        parser.change_domain(index=2)                                               # } Отправляем клавиатуру2
    elif message.text == '4ch':                                                     # }
        bot.send_message(message.chat.id, 'Жми "get memes"', reply_markup=markup2)  # }
        parser.change_domain(index=3)                                               # }
    elif message.text == 'Reddit':                                                  # }
        bot.send_message(message.chat.id, 'Жми "get memes"', reply_markup=markup2)  # }
        parser.change_domain(index=4)                                               # }

    if message.text == "get memes":  # Обрабатываем команду "get memes"
        bot.send_message(message.chat.id, "Подожди немного, выполняется запрос...")  # Оповещаем о загрузке
        mem_t = parser.get_meme_text()  # Получаем тексты записей
        mem_p = parser.get_meme_pic()  # Получаем ссылки кратинок с записей
        for i in range(5):  # В цикле отправляем записи
            z = 0
            bot.send_message(message.chat.id, str(parser.get_domain_name())+"\n"+str(mem_t[i]))  # Отправляем текст
            if mem_p[i] != '...' and 'Видео пока не доступно, извините':  # Если есть картинки
                if len(mem_p[i]) != 1:  # Если картинок несколько
                    pic_group = []  # создаём список под картинки
                    for z in range(len(mem_p[i])):  # В цикле
                        m = requests.get(mem_p[i][z])  # Скачиваем картинки
                        out = open("img" + str(z) + ".jpg", "wb")  # } Записываем их в файлы
                        out.write(m.content)                       # }
                        m.close()    # } Закрываем файлы
                        out.close()  # }
                        pic_group.append(open("img" + str(z) + ".jpg", "rb"))  # Открываем картинки в режиме чтения
                        # Отправляем медиа группу
                    bot.send_media_group(message.chat.id,
                                         [InputMediaPhoto(pic_group[z]) for z in range(len(mem_p[i]))])
                    for z in range(len(mem_p[i])):  # В цикле
                        pic_group[z].close()  # Закрыаем файлы
                        os.remove("img" + str(z) + ".jpg")
                else:  # Если же картинка одна
                    p = requests.get(mem_p[i][z])  # Скачиваем картинку по ссылке
                    out = open("img.jpg", "wb")  # } Записываем её в файл
                    out.write(p.content)         # }
                    p.close()    # } Закрываем файлы
                    out.close()  # }
                    out = open("img.jpg", "rb")  # Открываем картинку в режиме чтения
                    bot.send_photo(message.chat.id, photo=out)  # Отправляем картинку
                    out.close()  # Закрываем картинку
                    os.remove("img.jpg")
            else:  # Если это видео
                bot.send_message(message.chat.id, str(mem_p[i]))  # Оповещаем пользователя

        # Отправляем сообщение с inline клавиатурой
        bot.send_message(message.chat.id, 'Как быстро кончается 5 мемов...', reply_markup=in_markup)
    elif message.text == "back":  # Обрабатываем команду "back"
        parser.change_offset(new_offset=0)  # Меням значение offset на 0
        bot.send_message(message.chat.id, 'Выбери паблик.', reply_markup=markup)  # Отправляем первую клавиатуру


@bot.callback_query_handler(func=lambda call: True)  # Обработка inline клавиатуры
def callback_inline(call):  # Функция обработки
    in_markup = inline_markup_set()  # Вызываем inline клавиатуру

    if call.data == 'more_memes':  # Обрабатываем команду "more memes"
        parser.change_offset(5)  # Изменяем значение offset на пять, для увеличения отступа записей
        bot.send_message(call.message.chat.id, "Подожди немного, выполняется запрос...")  # Оповещяем о загрузке
        mem_t = parser.get_meme_text()  # Получаем тексты записей
        mem_p = parser.get_meme_pic()  # Получаем ссылки картинок с записей
        for i in range(5):  # В цикле отправляем записи
            z = 0
            bot.send_message(call.message.chat.id,
                             str(parser.get_domain_name()) + "\n" + str(mem_t[i]))  # Отправляем текст
            if mem_p[i] != '...' and 'Видео пока не доступно, извините':  # Если есть картинки
                if len(mem_p[i]) != 1:  # Если картинок несколько
                    pic_group = []  # создаём список под картинки
                    for z in range(len(mem_p[i])):  # В цикле
                        m = requests.get(mem_p[i][z])  # Скачиваем картинки
                        out = open("img" + str(z) + ".jpg", "wb")  # } Записываем их в файлы
                        out.write(m.content)  # }
                        m.close()  # } Закрываем файлы
                        out.close()  # }
                        pic_group.append(open("img" + str(z) + ".jpg", "rb"))  # Открываем картинки в режиме чтения
                        # Отправляем медиа группу
                    bot.send_media_group(call.message.chat.id,
                                         [InputMediaPhoto(pic_group[z]) for z in range(len(mem_p[i]))])
                    for z in range(len(mem_p[i])):  # В цикле
                        pic_group[z].close()  # Закрыаем файлы
                else:  # Если же картинка одна
                    p = requests.get(mem_p[i][z])  # Скачиваем картинку по ссылке
                    out = open("img.jpg", "wb")  # } Записываем её в файл
                    out.write(p.content)  # }
                    p.close()  # } Закрываем файлы
                    out.close()  # }
                    out = open("img.jpg", "rb")  # Открываем картинку в режиме чтения
                    bot.send_photo(call.message.chat.id, photo=out)  # Отправляем картинку
                    out.close()  # Закрываем картинку
            else:  # Если это видео
                bot.send_message(call.message.chat.id, str(mem_p[i]))  # Оповещаем пользователя
        # Отправляем сообщение с inline клавиатурой
        bot.send_message(call.message.chat.id, 'Как быстро кончается 5 мемов...', reply_markup=in_markup)


bot.polling(none_stop=True, interval=0)  # Постоянно проверяем писал ли кто-то боту
