def carma_change(bot, chat_id, params):
    carma_to = params[0]
    carma_to_username = params[1]
    carma_from = params[2]
    carma_from_username = params[3]
    x = params[4]
    change_text = params[5]
    bot.send_message(
        chat_id,
        '[{to_user_name}](tg://user?id={to_user_id}), твою карму {change_text}'
        ' [{from_user_name}](tg://user?id={from_user_id}).\n'
        'Твоя текущая карма {x}.'.format(
            to_user_name=carma_to_username,
            to_user_id=carma_to,
            from_user_name=carma_from_username,
            from_user_id=carma_from,
            change_text=change_text,
            x=x
        ),
        parse_mode='Markdown'
    )


def carma_stats(bot, chat_id, data):
    text = 'Топ пользователей по карме:\n\n'
    for i in data:
        text += '<b>{crm}</b> - {nn}\n'.format(nn=i[0], crm=i[1])
    bot.send_message(chat_id, text, parse_mode='HTML')


def private_stat(bot, chat_id, data):
    text = 'Твоя карма в группах:\n\n'
    for i in data:
        text += '{crm} - <b>{chat_title}</b>\n'.format(
            chat_title=i[1],
            crm=i[0]
        )
    bot.send_message(chat_id, text, parse_mode='HTML')


def help_message(bot, chat_id):
    text = ('Список доступных команд:\n'
            '/start - Начать работу с ботом (рекомендуется вызывать в группах '
            'перед началом использования).\n'
            '/help - Получить список доступных команд.\n\n'
            'Чтобы изменить карму другому пользователю, ответьте на его '
            'сообщение через "reply"(ответить) текстом "+" или "спасибо" для '
            'повышения кармы, или "-" для понижения. Изменить карму себе '
            'нельзя! Не злоупотребляйте "минусами", иначе администратор может '
            'вас заблокировать.\n\n'
            'Команды для групповых чатов:\n'
            '    /stats - Топ пользователей по карме.\n'
            '    /your_stat - Твоя карма.\n'
            '    /block - Заблокировать пользователя '
            '(только для администраторов).\n'
            '    /unblock - Разблокировать пользователя '
            '(только для администраторов).\n'
            '    /delete - сбросить/удалить данные по чату '
            '(только для администраторов).\n\n'
            'Команды для личного чата с ботом:\n'
            '    /your_stat - Твоя карма в чатах.')
    bot.send_message(chat_id, text)
