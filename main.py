# python3
# -*- coding: utf-8 -*-
from os import environ
from re import match
from time import time, sleep

from telebot import TeleBot

import database as db
from messages_constructor import (
    carma_change, carma_stats, private_stat, help_message
)

API_TOKEN = environ.get('API_TOKEN')

bot = TeleBot(API_TOKEN)

chat_types = ["group", "supergroup"]


@bot.message_handler(commands=['start', 'help', 'stats', 'your_stat',
                               'block', 'unblock', 'delete'])
def commands_messages(message):
    if message.text == '/start':
        bot.send_message(message.chat.id, "Добро пожаловать!")

    elif message.text == '/help':
        help_message(bot, message.chat.id)

    elif message.text == '/your_stat':
        tables = db.db_table_list()
        data = list()
        for chat_id in tables:
            x = db.db_search_stat(chat_id, message.from_user.id)
            if x:
                x.append(int(chat_id))
                data.append(x)
        data = sorted(data, key=lambda c: c[0], reverse=True)
        private_stat(bot, message.chat.id, data)

    elif message.chat.type in chat_types:
        if message.text == '/start@carmas_bot':
            db.db_create(message.chat.id)
            bot.send_message(message.chat.id, "Добро пожаловать!")

        elif message.text == '/help@carmas_bot':
            help_message(bot, message.chat.id)

        elif message.text == '/stats@carmas_bot':
            data = db.db_carma_stat(message.chat.id)
            if match(r'^relation.+', str(data)):
                return
            carma_stats(bot, message.chat.id, data)

        elif message.text == '/your_stat@carmas_bot':
            crm = db.db_select(message.chat.id, message.from_user.id,
                               ['carma'])
            if match(r'^relation.+', str(crm)) or not crm:
                return
            bot.send_message(
                message.chat.id,
                "[{user_name}](tg://user?id={user_id}), "
                "твоя текущая карма {crm}".format(
                    user_name=(message.from_user.username
                               if message.from_user.username
                               else message.from_user.id),
                    user_id=message.from_user.id,
                    crm=crm[0][0]
                ),
                parse_mode='Markdown'
            )

        elif ((message.text == '/block@carmas_bot'
               or message.text == '/unblock@carmas_bot')
              and message.reply_to_message):
            status = bot.get_chat_member(message.chat.id, message.from_user.id)
            if status.status == 'creator' or status.status == 'administrator':
                block = (1 if message.text == '/block@carmas_bot' else 0)
                data = db.db_block(
                    message.chat.id,
                    message.reply_to_message.from_user.id,
                    block
                )
                if match(r'^relation.+', str(data)):
                    return
                bot.send_message(
                    message.chat.id,
                    'Пользователь {}.'.format(
                        'заблокирован' if block else 'разблокирован'
                    ))
            else:
                bot.send_message(
                    message.chat.id,
                    'Только администраторы могут изменять '
                    'возможность модификации кармы!'
                )

        elif message.text == '/delete@carmas_bot':
            status = bot.get_chat_member(message.chat.id, message.from_user.id)
            if status.status == 'creator' or status.status == 'administrator':
                bot.send_message(
                    message.chat.id,
                    'Вы действительно хотите удалить данные по вашему чату?\n'
                    '(Для продолжения ответьте "*да*" или "*нет*" на это '
                    'сообщение через "reply"(ответить))',
                    parse_mode='Markdown'
                )
            else:
                bot.send_message(
                    message.chat.id,
                    'Эта команда доступна только администраторам!'
                )


@bot.message_handler(
    content_types=['text'],
    regexp='^(да)$',
    func=lambda message: (
            message.chat.type in chat_types and message.reply_to_message and
            message.reply_to_message.text == (
                    'Вы действительно хотите удалить данные по вашему чату?\n'
                    '(Для продолжения ответьте "да" или "нет" на это сообщение'
                    ' через "reply"(ответить))'
            ) and
            (bot.get_chat_member(message.chat.id, message.from_user.id).status
             == 'creator' or
             bot.get_chat_member(message.chat.id, message.from_user.id).status
             == 'administrator')
    )
)
def delete_chat(message):
    db.db_delete(message.chat.id)
    bot.send_message(message.chat.id, 'Данные по карме в вашем чате удалены')


@bot.message_handler(
    content_types=['text'],
    regexp=r'^([+-]|спасибо\W*)$',
    func=lambda message: (message.chat.type in chat_types and
                          message.reply_to_message)
)
def carma(message):
    carma_to = message.reply_to_message.from_user.id
    carma_to_username = (message.reply_to_message.from_user.username
                         if message.reply_to_message.from_user.username
                         else carma_to)
    carma_to_name = (message.reply_to_message.from_user.first_name
                     if message.reply_to_message.from_user.first_name
                     else carma_to_username)
    to_lastname = message.reply_to_message.from_user.last_name
    if to_lastname:
        carma_to_name += ' ' + to_lastname
    carma_from = message.from_user.id
    carma_from_username = (message.from_user.username
                           if message.from_user.username
                           else carma_from)
    carma_from_name = (message.from_user.first_name
                       if message.from_user.first_name
                       else carma_from_username)
    from_lastname = message.from_user.last_name
    if from_lastname:
        carma_from_name += ' ' + from_lastname

    if carma_from == carma_to:
        return

    x = 0
    current_time = int(time())

    if message.text.lower() == '+' or match(r'^спасибо\W*$',
                                            message.text.lower()):
        x += 1
        change_text = 'увеличил'
    else:
        x -= 1
        change_text = 'уменьшил'

    select_from = db.db_select(
        chat_id=message.chat.id,
        user_id=carma_from,
        column=['date', 'block']
    )
    last_change = 0
    if select_from:
        if match(r'^relation.+', str(select_from)):
            db.db_create(message.chat.id)
            db.db_add(
                chat_id=message.chat.id,
                user_id=carma_from,
                user_name=carma_from_username,
                name=carma_from_name,
                chat_title=message.chat.title,
                date=current_time
            )
        elif select_from[0][1]:
            bot.send_message(message.chat.id,
                             'Вы не можете модифицировать карму')
            return
        else:
            last_change = select_from[0][0]
    if (current_time - last_change) < 10:
        return

    select_to = db.db_select(
        chat_id=message.chat.id,
        user_id=carma_to,
        column=['carma']
    )
    if select_to:
        x += select_to[0][0]
        db.db_update(
            chat_id=message.chat.id,
            user_id=carma_to,
            user_name=carma_to_username,
            name=carma_to_name,
            chat_title=message.chat.title,
            carma=x
        )
    else:
        db.db_add(
            chat_id=message.chat.id,
            user_id=carma_to,
            user_name=carma_to_username,
            name=carma_to_name,
            chat_title=message.chat.title,
            carma=x
        )

    if select_from:
        db.db_update_date(
            chat_id=message.chat.id,
            user_id=carma_from,
            user_name=carma_from_username,
            name=carma_from_name,
            chat_title=message.chat.title,
            date=current_time
        )
    else:
        db.db_add(
            chat_id=message.chat.id,
            user_id=carma_from,
            user_name=carma_from_username,
            name=carma_from_name,
            chat_title=message.chat.title,
            date=current_time
        )

    carma_params = [carma_to, carma_to_name,
                    carma_from, carma_from_name,
                    x, change_text]
    carma_change(bot, message.chat.id, carma_params)


if __name__ == '__main__':
    bot.remove_webhook()
    sleep(0.1)
    bot.polling()
