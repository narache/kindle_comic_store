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

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

db_name = 'database.db'

if not (os.path.exists(db_name)):
    sys.exit('create_db.pyを先に実行してね')

# 一時的に環境変数を設定
delimiter = ';' if os.name == 'nt' else ':'
os.environ['PATH'] += (delimiter + os.path.abspath('driver'))

options = ChromeOptions()
options.add_argument('--headless')
driver = Chrome(options=options)

page_counter = 0

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

            books = driver.find_element_by_id('s-results-list-atf').find_elements_by_tag_name('li')
            comics = []

            # ページ内処理
            for book in books:
                # サムネイル取得
                thumbnail = book.find_element_by_tag_name('img').get_attribute('src')
                # 本の詳細情報取得
                info_box = book.find_element_by_class_name('a-col-right')
                title_box = info_box.find_element_by_class_name('s-color-twister-title-link')
                book_name = title_box.text.strip()
                book_url = title_box.get_attribute('href')
                release_date = info_box.find_elements_by_class_name('a-color-secondary')[0].text
                author_name = info_box.find_elements_by_class_name('a-spacing-none')[1].text
                # SQLのパラメータを作成
                comics.append((thumbnail, book_name, book_url, release_date, author_name))

            # ページごとにまとめて登録
            c.executemany(insert_sql, comics)
            conn.commit()

            try:
                next_page_link = driver.find_element_by_id('pagnNextLink')
                # 「次のページ」を押下したいが、Seleniumに画面外にあると誤判定されてしまう様なので無理やりスクロールする
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                next_page_link.click()
                # 「前のページ」が表示されるまで待つ
                wait = WebDriverWait(driver, 10)
                wait.until(
                    expected_conditions.visibility_of_element_located((By.ID, 'pagnPrevString')))
                sleep(1)
            except NoSuchElementException:
                print(str(page_counter) + 'ページ目が最後のページの様です。処理を終了します。')
                break
except:
    traceback.print_exc()
finally:
    driver.quit()
