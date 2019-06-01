"""
事前に、create_db.pyを実行してDBファイルを作成しておく必要がある。
Amazon Kindle Unlimitedのコミックス検索ページについて
各ページをスクレイピングしてSqlite3のデータに保存する。
"""
import os
import sqlite3
import sys
import traceback
from contextlib import closing
from time import sleep

from retry import retry
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Chrome, ChromeOptions

db_name = 'database.db'

if not (os.path.exists(db_name)):
    sys.exit('create_db.pyを先に実行してね')

# 一時的に環境変数を設定
delimiter = ';' if os.name == 'nt' else ':'
os.environ['PATH'] += (delimiter + os.path.abspath('driver'))

options = ChromeOptions()
options.add_argument('--headless')
driver = Chrome(options=options)
driver.set_window_size(10240, 10240)

page_counter = 0


@retry(TimeoutException, tries=4, delay=5, backoff=2)
def get_next_page(driver, next_page_link):
    driver.get(next_page_link.get_attribute('href'))


try:
    # コミックトップにアクセス
    driver.get('https://www.amazon.co.jp/s/?rh=n%3A3201084051&ref_=msw_list_shoveler_KU_mangatop_title')

    with closing(sqlite3.connect(db_name)) as conn:
        c = conn.cursor()
        c.execute('delete from comics')
        insert_sql = '''insert into comics (
                                            thumbnail, 
                                            book_name, 
                                            book_url, 
                                            release_date, 
                                            author_name) values (?, ?, ?, ?, ?)'''

        while True:
            page_counter += 1
            print(str(page_counter) + 'ページ目の処理を開始しました。')

            books = driver.find_elements_by_xpath(
                '//*[@id="search"]//div[@class="s-include-content-margin s-border-bottom"]')
            comics = []

            # ページ内処理
            for book in books:
                # サムネイル取得
                thumbnail = book.find_element_by_xpath('.//a/div/img[@class="s-image"]').get_attribute('src')
                # 本の詳細情報取得
                title_box = book.find_element_by_xpath('.//h2/a')
                book_name = title_box.text.strip()
                book_url = title_box.get_attribute('href')
                release_date = ''
                try:
                    release_date = book.find_element_by_xpath(
                        './/span[@class="a-size-base a-color-secondary a-text-normal"]').text
                except NoSuchElementException:
                    pass
                author_name = ''
                try:
                    author_name = \
                        book.find_element_by_xpath('.//div[@class="a-row a-size-base a-color-secondary"]').text.split(
                            '|')[
                            0]
                except NoSuchElementException:
                    pass
                # SQLのパラメータを作成
                comics.append((thumbnail, book_name, book_url, release_date, author_name))

            # ページごとにまとめて登録
            c.executemany(insert_sql, comics)
            conn.commit()

            try:
                next_page_link = driver.find_element_by_xpath(
                    '//*[@id="search"]//ul[@class="a-pagination"]//li[@class="a-last"]/a')
                sleep(2)
                get_next_page(driver, next_page_link)

                if (page_counter % 100) == 0:
                    print('ちょっと休憩')
                    sleep(30)

            except NoSuchElementException:
                print(str(page_counter) + 'ページ目が最後のページの様です。処理を終了します。')
                break
except:
    traceback.print_exc()
finally:
    driver.quit()
