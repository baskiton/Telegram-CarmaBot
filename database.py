# python3
# -*- coding: utf-8 -*-
from os import environ

from psycopg2 import connect, sql


def db_create(chat_id):
    sql_r = sql.SQL(
        """
        CREATE TABLE IF NOT EXISTS {}
        (user_id integer UNIQUE NOT NULL,
        user_name text,
        name text,
        carma integer NOT NULL,
        date integer,
        chat_title text,
        block integer NOT NULL)
        """
    ).format(sql.Identifier(str(chat_id)))
    return db_execute(sql_r)


def db_add(
        chat_id, user_id, user_name, name, chat_title, carma=0, date=0, block=0
):
    sql_r = sql.SQL(
        """
        INSERT INTO {}
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
    ).format(sql.Identifier(str(chat_id)))
    return db_execute(
        sql_r, user_id, user_name, name, carma, date, chat_title, block
    )


def db_update(chat_id, user_id, user_name, name, chat_title, carma):
    sql_r = sql.SQL(
        """
        UPDATE {}
        SET carma=%s,
        user_name=%s,
        name=%s,
        chat_title=%s
        WHERE user_id=%s
        """
    ).format(sql.Identifier(str(chat_id)))
    return db_execute(sql_r, carma, user_name, name, chat_title, user_id)


def db_update_date(chat_id, user_id, user_name, name, chat_title, date):
    sql_r = sql.SQL(
        """
        UPDATE {}
        SET date=%s,
        user_name=%s,
        name=%s,
        chat_title=%s
        WHERE user_id=%s
        """
    ).format(sql.Identifier(str(chat_id)))
    return db_execute(sql_r, date, user_name, name, chat_title, user_id)


def db_delete(chat_id):
    sql_r = sql.SQL(
        """DROP TABLE {}"""
    ).format(sql.Identifier(str(chat_id)))
    return db_execute(sql_r)


def db_select(chat_id, user_id, column='*'):
    sql_r = sql.SQL(
        """
        SELECT {0} FROM {1}
        WHERE user_id=%s
        """
    ).format(
        sql.SQL(', ').join(sql.Identifier(i) for i in column),
        sql.Identifier(str(chat_id))
    )
    return db_execute(sql_r, user_id)


def db_carma_stat(chat_id):
    sql_r = sql.SQL(
        """
        SELECT name, carma FROM {}
        ORDER BY carma DESC
        LIMIT 10
        """
    ).format(sql.Identifier(str(chat_id)))
    return db_execute(sql_r)


def db_table_list():
    sql_r = """
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema NOT IN ('information_schema','pg_catalog')
    """
    return sum(db_execute(sql_r), ())


def db_search_stat(chat_id, user_id):
    sql_r = sql.SQL(
        """
        SELECT carma, chat_title
        FROM {}
        WHERE user_id=%s
    """
    ).format(sql.Identifier(str(chat_id)))
    return list(sum(db_execute(sql_r, user_id), ()))


def db_block(chat_id, user_id, block):
    sql_r = sql.SQL(
        """
        UPDATE {}
        SET block=%s
        WHERE user_id=%s
        """
    ).format(sql.Identifier(str(chat_id)))
    return db_execute(sql_r, block, user_id)


def db_execute(sql_r, *data):
    database_url = environ['DATABASE_URL']

    with connect(database_url, sslmode='require') as conn:
        with conn.cursor() as cursor:
            try:
                cursor.execute(sql_r, data)
                return cursor.fetchall()
            except BaseException as err:
                print(err)
                return err
