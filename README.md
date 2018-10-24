# kindle comic store
日本のAmazon Kindle Unlimitedに登録されているコミックスの一覧をHTMLとして生成します。  
公式には数百ページに渡るページングがされており、ソート順も不明なので  
各ページをスクレイピングしてDBに登録後、筆者名とタイトルでソートした一覧をHTMLとして出力する動きをします。  
  
# Dependency
Python3の環境で作成しています。  
必要なライブラリはrequirements.txtを参照してください。  
また、Windows上で動作させる場合はSQLite3をインストールしてPATHに通す必要があります。  
(MacはSQLite3ははじめからインストールされて…ますよね？)  
  
# 使い方
コマンドラインでの単純な実行です。  
  
- 1.DBファイルの作成  
初回実行時はSQLite3のDBファイルの作成が必要です。  
下記コマンドで作成します。  
```python create_db.py```  
  
- 2.データの取得  
下記コマンドでデータ取得します。  
```python store_kindle_book_info.py```  
  
- 3.HTMLの生成  
下記コマンドでHTMLを生成します。  
```python generate_book_list.py```  
output/htmlフォルダが生成され、実行日時のHTMLファイルが出力されます。  
  
# Licence
This software is released under the MIT License, see LICENSE.
