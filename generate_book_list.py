"""
事前に、store_kindle_book_info.pyを実行してDBへのデータ登録を行う必要がある。
Amazon Kindle Unlimitedのコミックス情報から、筆者とタイトルでソートしたHTMLファイルを生成する。
どんなコミックがAmazon Kindle Unlimitedに登録されているかを一望できる。
"""
import datetime
import os
import shutil
import sqlite3
import sys
import urllib.parse
import urllib.request
from contextlib import closing

db_name = 'database.db'

# 前段処理の実施確認
if not (os.path.exists(db_name)):
    sys.exit('store_kindle_book_info.pyを先に実行してね')

# DBからブック情報を全件取得
with closing(sqlite3.connect(db_name)) as conn:
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('select * from comics order by author_name asc, release_date asc, book_name asc')
    book_data_list = c.fetchall()

# 出力対象の有無を確認
if len(book_data_list) < 1:
    sys.exit('出力対象のレコードがありません。')

# 出力先が無ければ作成
if not (os.path.isdir('output/html')):
    os.makedirs('output/html')

download_thumbnails_again = False
print('サムネイルをローカルにダウンロードしますか？')
print('前回実行時のサムネイルを信じる場合は「n」を入力すると処理が速いです。')
if input('y/n:').lower() == 'y':
    download_thumbnails_again = True

# 前回実施時のイメージフォルダがあったら消しておく
if download_thumbnails_again:
    if os.path.isdir('output/images'):
        shutil.rmtree('output/images')

output_file = 'output/html/' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.html'
with open(output_file, mode='w', encoding='utf-8') as f:
    # ヘッダをテンプレートから読み込み
    with open('template/htm_head.tmpl', mode='r', encoding='utf-8') as h:
        f.write(h.read())

    write_no = 1
    # ブック情報を全て出力
    for book_data in book_data_list:
        # イメージフォルダの確認と作成
        if download_thumbnails_again:
            image_path = os.path.dirname(urllib.parse.urlparse(book_data['thumbnail']).path)
            if not (os.path.isdir('output' + image_path)):
                os.makedirs('output' + image_path)
            # サムネイルをイメージフォルダに保存する
            urllib.request.urlretrieve(book_data['thumbnail'],
                                       'output' + urllib.parse.urlparse(book_data['thumbnail']).path)
        # HTMLの出力
        f.write('<tr>\n')
        f.write('    <td>' + str(write_no) + '</td>\n')
        f.write('    <td><a href="' + book_data['book_url'] + '" target="_blank"><img src="..' + urllib.parse.urlparse(
            book_data['thumbnail']).path + '"></a></td>\n')
        f.write('    <td class="left">' + book_data['author_name'] + '</td>\n')
        f.write('    <td class="left"><a href="' + book_data['book_url'] + '" target="_blank">' + book_data[
            'book_name'] + '</a></td>\n')
        f.write('    <td>' + book_data['release_date'] + '</td>\n')
        f.write('</tr>\n')
        write_no += 1

    # フッタをテンプレートから読み込み
    with open('template/htm_foot.tmpl', mode='r', encoding='utf-8') as ft:
        f.write(ft.read())

print(os.path.abspath(output_file))
print('を作成しました。')
