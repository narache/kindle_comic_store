"""
Sqlite3のDBファイル作成を行う。
"""
import os
import sqlite3
import sys
from contextlib import closing

db_name = 'database.db'

if os.path.exists(db_name):
    sys.exit()

with closing(sqlite3.connect(db_name)) as conn:
    c = conn.cursor()

    # executeメソッドでSQL文を実行する
    create_table = '''create table comics (thumbnail varchar(2048),
                                            book_name varchar(500),
                                            book_url varchar(2048),
                                            release_date varchar(10),
                                            author_name varchar(500))'''
    c.execute(create_table)

    # index作成
    create_index = 'create index idx_comics on comics(book_name, author_name)'
    c.execute(create_index)
