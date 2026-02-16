from selenium.webdriver.common.by import By
import re

def __split_column(column):
    splitted_column = column.split(" ", 2)
    name = splitted_column[0]
    type = splitted_column[1]
    if len(splitted_column) == 3: 
        option = splitted_column[2]
    else:
        option = ""
    return name, type, option

def __common_check(errors, warnings, name, type, option):
    continue_flg = False
    reserve_words = ["send", "day", "value", "state", "type", "transaction", "date", "text"]
    option_keywords = ["string", "integer", "text", "references", "reference", "date"]
    invalid_name_chars = ["-", "(", "（", ")", "）"]
    if any(keyword in option for keyword in option_keywords):
        errors.append(f"{name} {type} カラムから空白スペースが含まれています(型とオプションのチェックをスキップします）\m{name} {type} カラムの半角スペースを削除しましょう。\n\n■理由\nカラム名にスペースは使用できないためです。")
        continue_flg = True
    for char in invalid_name_chars:
        if char in name:
            errors.append(f"{name}カラムの名前に{char}が含まれています\m{name}カラムの{char}を削除または_に変更しましょう。\n\n■理由\n命名規則上、カラム名に{char}は使用できないためです。")
    if name in reserve_words:
        errors.append(f"{name} カラムのカラム名が予約語です\m{name}カラムを別の名前に変更しましょう。\n\n■理由\n{name}は予約語でカラム名に使用できないためです。")
    if re.search(r"\d", name):
        warnings.append(f"{name}カラムのカラム名に数字が含まれています\m{name}カラムにより適切な名前を付けられないか見直しましょう。\n\n■理由\nカラム名を数字で区別するのは保守上好ましくないためです。")
    return errors, warnings, continue_flg

def goto_readme(driver):
    try:
        readme_url = driver.find_element(By.XPATH, "//div[@data-path='README.md']/div[2]/div/details/details-menu/a[1]").get_attribute('href')
        driver.get(readme_url)
    except:
        return False
    else:
        return True

def check_table_num_and_association(driver):
    try:
        errors = []
        warnings = []
        table_num = len(driver.find_elements(By.TAG_NAME, 'table'))
        readme = driver.find_element(By.XPATH, '//*[@id="repo-content-pjax-container"]/react-app/div/div/div[1]/div/div/div[2]/div[2]/div/div[3]/div[2]/div/div[3]/section/div/article').text
        has_one_num = readme.count("has_one")
        has_one_num -= readme.count("has_one_attached")
        has_many_num = readme.count("has_many")
        belongs_to_num = readme.count("belongs_to")
        if readme.count("comments") > 0:
            warnings.append("追加実装のコメントテーブルが見つかりましたので、その分チェックするテーブルとアソシエーション数を減らしています")
            table_num -= 1
            belongs_to_num -= 2
            has_many_num -= 2
        if "good" in readme:
            errors.append("goodsテーブルが見つかりました。\mテーブル名にgoodsを使用しないようにしましょう。\ngoodsは絶対複数名詞で、単数形と複数形の区別が存在しないためです")
        if table_num == 0:
            errors.append("テーブルが見つかりませんでした。あるいはマークダウンが崩れている可能性があります\mREADMEのマークダウンがカリキュラムの指定通りになっているかを確認してください。")
        elif not table_num == 4: 
            errors.append("テーブルが4個必要なのに対し見つかったのは"+str(table_num)+"個でした\m要件に沿ってテーブルを作成できているか、またREADMEのマークダウンがカリキュラムの指定通りになっているかを確認してください。") 
        if has_one_num > 2:
            errors.append("DB設計全体において、has_oneの数が多いです\m要件に照らし合わせた際にhas_oneの数が期待通りでないため、改めて各テーブルのアソシエーションを見直しましょう。")
        elif has_one_num < 2:
            errors.append("DB設計全体において、has_oneの数が少ないです\m要件に照らし合わせた際にhas_oneの数が期待通りでないため、改めて各テーブルのアソシエーションを見直しましょう。")
        if has_many_num > 2:
            errors.append("DB設計全体において、has_manyの数が多いです\m要件に照らし合わせた際にhas_manyの数が期待通りでないため、改めて各テーブルのアソシエーションを見直しましょう。")
        elif has_many_num < 2:
            errors.append("DB設計全体において、has_manyの数が少ないです\m要件に照らし合わせた際にhas_manyの数が期待通りでないため、改めて各テーブルのアソシエーションを見直しましょう。")
        if belongs_to_num > 4:
            if belongs_to_num == 9 or belongs_to_num == 10:
                warnings.append("DB設計全体において、belongs_toの数が多いです\m要件に照らし合わせた際にbelongs_toの数が期待通りでないため、改めて各テーブルのアソシエーションを見直しましょう。\n※activehashの分も記載している形であれば問題ございません")
            else:
                errors.append("DB設計全体において、belongs_toの数が多いです\m要件に照らし合わせた際にbelongs_toの数が期待通りでないため、改めて各テーブルのアソシエーションを見直しましょう。")
        elif belongs_to_num < 4:
            errors.append("DB設計全体において、belongs_toの数が少ないです\m要件に照らし合わせた際にbelongs_toの数が期待通りでないため、改めて各テーブルのアソシエーションを見直しましょう。")
        association_dup = 0
        if "belong_to" in readme:
            errors.append("belong_toが存在しています\mrailsのルールに沿って、belong_toをbelongs_toに修正しましょう。")
        for row in readme.split("\n"):
            if "dependent:" in row:
                errors.append("アソシエーションにdependentオプションが見つかりました\mfurimaの実装要件において関連モデル情報の同時削除は求められていないため、DB設計全体においてdependentオプションを削除しましょう。")
                row = re.sub('dependent:.+','',row)
            if row.count("has_one")+row.count("belongs_to")+row.count("has_many") > 1:
                association_dup += 1
                continue
            if "has_one" in row:
                if row[-1] == "s" and not row[-7:] == "address" and not row[-6:] == "status": 
                    errors.append(row+"の末尾が複数形になっています\mhas_oneに続くモデル名は単数形にしましょう。")
            if "belongs_to" in row:
                if row[-1] == "s" and not row[-7:] == "address" and not row[-6:] == "status": 
                    errors.append(row+"の末尾が複数形になっています\mbelongs_toに続くモデル名は単数形にしましょう。")
            if "has_many" in row:
                if not row[-1] == "s" or row[-7:] == "address" or row[-6:] == "status": 
                    errors.append(row+"の末尾が複数形になっていません\mhas_manyに続くモデル名は複数形にしましょう。")
        if association_dup != 0:
            warnings.append("マークダウン適応時、アソシーエションが横並びになっている行が"+str(association_dup)+"行あります（該当行の複数形単数形のチェックをスキップしています）\mREADMEのマークダウンがカリキュラムの指定通りになっているかを確認してください。")
    except:
        errors.append("テーブル数とアソシエーションのチェック中にエラーが発生しました\mREADMEのマークダウンや記載の順番がカリキュラムの指定通りになっているかを確認してください。")
    return [errors, warnings]

def check_users_table(driver):
    errors = []
    warnings = []
    try:
        css_selector = "div:has(a[href*='user' i], a[href*='ユーザー'])"
        users_table = driver.find_element(By.CSS_SELECTOR, css_selector+"+markdown-accessiblity-table").text
    except:
        errors.append("ユーザーテーブルを見つけられませんでした\mもしユーザーテーブルを作成していない場合は、要件でユーザー情報の保存が求められているためユーザーテーブルを追加しましょう。")
    else:
        table_name = users_table.replace("table","").replace("Table","").replace(" ","")
        table_name = re.sub(r"[^a-zA-Z]", "", table_name)
        birth_dup = False
        # if table_name[-1] != "s": 
        #     errors.append("テーブル名が複数形になっていません\m"+table_name+"テーブルのテーブル名を複数形にしましょう。\n\n■理由\n命名規則においてテーブル名は複数形であることが求められているためです。")
        if users_table.count('\n') < 8: 
            errors.append("カラムの数が少ないです\m実装要件と比較してユーザーテーブルのカラム数が少ないです。\n実装要件及び見本アプリの新規登録ページを参考にカラムを見直しましょう。")
        if users_table.count('\n') > 8: 
            errors.append("カラムの数が多いです\m実装要件と比較してユーザーテーブルのカラム数が多いです。\n実装要件及び見本アプリの新規登録ページを参考にカラムを見直しましょう。")
        columns = users_table.split("\n")
        columns.pop(0)
        try:
            check_num = 0
            for column in columns:
                check_num += 1
                name,type,option = __split_column(column)
                errors,warnings,continue_flg = __common_check(errors,warnings,name,type,option)
                if continue_flg:
                    continue
                if "_id" in name: 
                    errors.append(name + "カラムのカラム名に_idが付与されています\m"+name+"カラムのカラム名に_idは不要になります\n\n■理由\n"+name+"カラムはid番号を扱うカラムではないためです。")
                if "reference" in type:
                    errors.append("ユーザーテーブルに"+ name + "の外部キーカラムが見つかりました\mユーザーテーブルに"+name+"の外部キーカラムは不要になります\n\n■理由\nユーザーは単独で存在し、belongs_toによる他テーブルとの紐付きがないためです。")
                    continue
                if not "string" in type and not "birth" in name:
                    errors.append(name + "カラムが文字列型ではありません\m誕生日カラムでなければ、"+name+"カラムの型を文字列型にしましょう。\n\n■理由\n値として短い文字列が入ることが想定されるためです。")
                if not "null:" in option: 
                    errors.append(name + "カラムにNOTNULL制約がついていません\m"+name+"カラムのオプションにNOTNULL制約を適応させましょう。\n\n■理由\n要件において"+name+"カラムに値が必ず入ることが求められているためです。")
                if "unique:" in option and not name == "email":
                    errors.append(name + "カラムにユニーク制約は不要です\m"+name+"カラムからユニーク制約を外しましょう。\n\n■理由\n要件において"+name+"カラムにユニーク制約が求められていないためです。")
                if name == "password":
                    errors.append("passwordカラムが見つかりました\mpasswordカラムのカラム名をencrypted_passwordにしましょう。\n\n■理由\ndeviseを用いる場合、デフォルトでパスワードは暗号化された上でencrypted_passwordカラムに保存されるためです。")
                    continue
                if name == "password_confirmation":
                    errors.append("password_confirmationカラムが見つかりました\mpassword_confirmationカラムを削除しましょう。\n\n■理由\ndeviseでは確認用パスワードをテーブルに保存しないためです。")
                if "email" in name and not "unique:" in option:
                    errors.append(name + "カラムにユニーク制約が見つかりませんでした\m"+name+"カラムにユニーク制約を適応させましょう。\n\n■理由\n要件においてメールアドレスは一意性であることが求められているためです。")
                    continue
                if  "birth" in name and not "date" in type:
                    errors.append(name + "カラムがdate型ではありません\m"+name+"カラムが誕生日カラムであれば、型をdate型にしましょう。\n\n■理由\n管理の容易さから、年月日はdate型で扱うことが推奨されているためです。")
        except:
            errors.append("上から"+str(check_num)+"番目のカラムのチェック中にエラーが発生しました。\m"+str(check_num)+"行目付近のマークダウンに不備がないか確認してください")
        if users_table.count("birth") > 1: 
            errors.append("誕生日カラムが複数見つかりました\m誕生日カラムを一つにまとめましょう。\n\n■理由\n日付型を用いることで年月日を一つのカラムで管理することが可能になるためです")
    return [errors, warnings]

def check_items_table(driver):
    errors = []
    warnings = []
    try: 
        items_table = driver.find_element(By.CSS_SELECTOR, "div:has(a[href*='item' i],a[href*='アイテム'],a[href*='商品'],a[href*='product' i],a[href*='good' i])+markdown-accessiblity-table").text
    except:
        errors.append("商品テーブルを見つけられませんでした（あるいはマークダウンが崩れています）\mもし商品テーブルを作成していない場合は、要件で商品情報の保存が求められているため商品テーブルを追加しましょう。")
    else:
        table_name = items_table.replace("table","").replace("Table","").replace(" ","")
        table_name = re.sub(r"[^a-zA-Z]", "", table_name)
        # if table_name[-1] != "s": errors.append("テーブル名が複数形になっていません\m"+table_name+"テーブルのテーブル名を複数形にしましょう。\n\n■理由\n命名規則においてテーブル名は複数形であることが求められているためになります。")
        if items_table.count('\n') < 9: 
            errors.append("カラムの数が少ないです\m実装要件と比較して商品テーブルのカラム数が少ないです。\n実装要件及び見本アプリの出品ページを参考にカラムを見直しましょう。")
        if items_table.count('\n') > 9: 
            errors.append("カラムの数が多いです\m実装要件と比較して商品テーブルのカラム数が多いです。\n実装要件及び見本アプリの出品ページを参考にカラムを見直しましょう。")
        if not "user" in items_table: 
            errors.append("ユーザーテーブルと繋がる外部キーカラムが見つかりません\mユーザーの外部キーカラムを追加しましょう。\n\n■理由\n実装要件において、商品テーブルには出品者が誰であるかを保存することが求められているためです。")
        if items_table.count("integer") < 6: 
            errors.append("数値型のカラムが不足しています\m商品テーブルの各カラムの型を見直しましょう。\nカテゴリー・商品の状態・配送料負担・発送元地域・発送までの日数はActivehashを用いた実装のため、型が数値型になります。")
        if items_table.count("integer") > 6: 
            errors.append("数値型のカラムが多いです\m商品テーブルの各カラムの型を見直しましょう。\n文字情報を保存するカラムを数値型にしていないか確認してください。")
        if items_table.count("_id") < 5: 
            errors.append("○○_idカラムが不足しています\mカテゴリー・商品の状態・配送料負担・発送元地域・発送までの日数カラムはActivehashを用いた実装になるため、Activehashのルールに沿ったカラム名と型にしましょう。\nactivehashにつきましては以下カリキュラムをご参考にいただければと思います。\n\nLesson1 最終課題補足カリキュラム\nカテゴリーの選択を工夫しよう")
        if items_table.count("_id") > 5: 
            errors.append("○○_idカラムが多いです\m○○_idといったid番号を保存するカラムの数が要件通りか確認しましょう。")
        columns = items_table.split("\n")
        columns.pop(0)
        try:
            check_num = 0
            for column in columns:
                check_num += 1
                name,type,option = __split_column(column)
                errors,warnings,continue_flg = __common_check(errors,warnings,name,type,option)
                if continue_flg:
                    continue
                if "image" in name:
                    errors.append("画像カラムが見つかりました\m"+name+"カラムが商品画像カラムであれば削除しましょう。\n\n■理由\n画像の管理にActiveStorageを用いる場合、画像情報は別テーブルに保存されるためです。")
                    continue
                if "name" in name and not "string" in type:
                    errors.append(f"{name}カラムは文字列型の方が適切な可能性があります\m{name}カラムに文字列が保存される想定であれば、型を文字列型にしましょう。")
                if (("exp" in name) or ("desc" in name) or ("info" in name)) and not "text" in type and not "_id" in name:
                    errors.append(f"{name}カラムはtext型の方が適切な可能性があります\m{name}カラムが商品説明カラムの場合、長い文章が入ることを想定してtext型にしましょう。")
                if "price" in name and not type == "integer":
                    errors.append(f"{name}カラムは数値型の方が適切な可能性があります\m{name}カラムが価格カラムの場合、数値が入ることを想定して数値型にしましょう。")
                elif "_id" in name and not "user" in name:
                    if (name[-4] == "s") and (not "status_id" in name) and (not "address_id" in name):
                        errors.append(f"{name}カラムが複数形_idになっている可能性があります\m{name}カラムがActivehashを用いるカラムの場合、Activehashのルールに沿って「単数形_id」にしましょう。")
                    if not type == "integer":
                        errors.append(f"{name}カラムは数値型の方が適切な可能性があります\m{name}カラムがActivehashを用いるカラムの場合、Activehashのルールに沿って数値型にしましょう。")
                if "user" in name:
                    if not name == "user": 
                        errors.append(f"外部キーカラムのカラム名が正しくない可能性があります\m{name}カラムが外部キーカラムの場合、カラム名がユーザーテーブルの名前に沿ったものになっているか確認しましょう。")
                    if not type == "references": 
                        errors.append(f"外部キーカラムがreferences型ではありません\m{name}カラムが外部キーカラムの場合、型をreferences型にしましょう。")
                    if not "foreign_key" in option: 
                        errors.append(f"外部キーカラムに外部キー制約が付与されていません\m{name}カラムが外部キーカラムの場合、オプションに外部キー制約を付与しましょう。")
                if "reference" in type and not "user" in name:
                    errors.append(f"ユーザー以外の外部キーカラムが見つかりました\m{name}カラムがユーザー以外のテーブルと繋がる外部キーカラムの場合は削除しましょう。\n\n■理由\n要件上、商品は出品者のみが紐づいていれば存在できるためです。")
                    continue
                if not "null:" in option:
                    errors.append(f"{name}カラムにNOTNULL制約が見つかりませんでした\m{name}カラムにNOTNULL制約を追加しましょう。\n\n■理由\n{name}カラムは値が入ることが必須なためです。")
                if "unique:" in option: 
                    errors.append(f"{name}カラムにユニーク制約が見つかりました\m{name}カラムのオプションからユニーク制約を外しましょう。\n{name}の値は複数レコードで重複可能なためです。")
                if "foreign_key:" in option and not "user" in name:
                    errors.append(f"{name}カラムに外部キー制約が見つかりました\m{name}カラムのオプションから外部キー制約を外しましょう。\n{name}カラムは他テーブルと関係を持つ外部キーカラムではないためです。")              
        except:
            errors.append("上から"+str(check_num)+"番目のカラムのチェック中にエラーが発生しました。\m"+str(check_num)+"行目付近のマークダウンに不備がないか確認してください")
    return [errors, warnings]

def check_orders_table(driver):
    errors = []
    warnings = []
    try: 
        orders_table = driver.find_element(By.CSS_SELECTOR, "div:has(a[href*='order' i],a[href*='record' i],a[href*='buy' i],a[href*='purchase' i],a[href*='tran' i],a[href*='manage'],a[href*='履歴'])+markdown-accessiblity-table").text
    except:
        errors.append("購入履歴テーブルを見つけられませんでした（あるいはマークダウンが崩れています）\mもし購入履歴テーブルを作成していない場合は、要件で購入履歴情報の保存が求められているため購入履歴テーブルを追加しましょう。")
    else:
        table_name = orders_table.replace("table","").replace("Table","").replace(" ","")
        table_name = re.sub(r"[^a-zA-Z]", "", table_name)
        # if table_name[-1] != "s":
        #     errors.append("テーブル名が複数形になっていません\m"+table_name+"テーブルのテーブル名を複数形にしましょう。\n\n■理由\n命名規則においてテーブル名は複数形であることが求められているためです。")
        if orders_table.count('\n') < 2:
            errors.append("カラムの数が少ないです\m実装要件と比較して購入履歴テーブルのカラム数が少ないです。\n購入履歴テーブルには「誰が」「どの商品を購入したか」を保存するためにユーザーと商品の外部キーカラムを用意しましょう。")
        if orders_table.count('\n') > 2:
            errors.append("カラムの数が多いです\m実装要件と比較して購入履歴テーブルのカラム数が多いです。\n購入履歴テーブルには「誰が」「どの商品を購入したか」を保存するためにユーザーと商品の外部キーカラムのみを用意しましょう。")
        if not "user" in orders_table:
            errors.append("ユーザーの外部キーカラムが見つかりません\m購入履歴テーブルには「誰が」「どの商品を購入したか」を保存するためにユーザーの外部キーカラムを追加しましょう。")
        if not (("item" in orders_table) or ("product" in orders_table)):
            errors.append("商品の外部キーカラムが見つかりません\m購入履歴テーブルには「誰が」「どの商品を購入したか」を保存するためにユーザーの外部キーカラムを追加しましょう。")
        columns = orders_table.split("\n")
        columns.pop(0)
        try:
            check_num = 0
            for column in columns:
                check_num += 1
                name,type,option = __split_column(column)
                errors,warnings,continue_flg = __common_check(errors,warnings,name,type,option)
                if continue_flg:
                    continue
                if "user" in name or "item" in name or "product" in name:
                    if "_id" in name:
                        errors.append(f"{name}カラムのカラム名に_idが付与されています\m{name}カラムのカラム名から_idを削除しましょう。\n\n■理由\nreferences型を用いる場合、DB設計では_idの記載が不要になるためです。")
                    if name[-1] == "s":
                        errors.append(f"{name}カラムが複数形になっています\m{name}カラムのカラム名を単数形にしましょう。\n\n■理由\n単数形にしないと外部キーカラムとして他テーブルとの繋がりを作れないためです。")
                    if not type == "references":
                        errors.append(f"{name}カラムがreferences型ではありません\m{name}カラムは外部キーカラムのため、型をreferences型にしましょう。")
                    if not "null:" in option:
                        errors.append(f"{name}カラムにNOTNULL制約がついていません\m{name}カラムは空を許容しないため、オプションにNOTNULL制約を追加しましょう。")
                    if not "foreign" in option:
                        errors.append(f"{name}カラムに外部キー制約がついていません\m{name}カラムは外部キーカラムのため、オプションに外部キー制約を追加しましょう。")
                    if "unique:" in option:
                        errors.append(f"{name}カラムにユニーク制約が見つかりました\m{name}カラムは重複した値を許容するため、オプションからユニーク制約を外しましょう。")
        except:
            errors.append("上から"+str(check_num)+"番目のカラムのチェック中にエラーが発生しました。\m"+str(check_num)+"行目付近のマークダウンに不備がないか確認してください")
    return [errors, warnings]

def check_addresses_table(driver):
    errors = []
    warnings = []
    try: 
        # 商品テーブルにもinfo等の名前がつくことがあるので、最後のテーブルを指定するために[-1]を付与
        addresses_table = driver.find_elements(By.CSS_SELECTOR, "div:has(a[href*='add' i],a[href*='ship' i],a[href*='desti' i],a[href*='payment' i],a[href*='deli' i],a[href*='info' i],a[href*='住所'])+markdown-accessiblity-table")[-1].text
    except:
        errors.append("配送先住所テーブルを見つけられませんでした（あるいはマークダウンが崩れています）\mもし配送先住所テーブルを作成していない場合は、要件で配送先住所情報の保存が求められているため配送先住所テーブルを追加しましょう。")
    else:
        table_name = addresses_table.replace("table","").replace("Table","").replace(" ","")
        table_name = re.sub(r"[^a-zA-Z]", "", table_name)
        # if table_name[-1] != "s" and not "addresses" in table_name:
        #     errors.append("テーブル名が複数形になっていません\m"+table_name+"テーブルのテーブル名を複数形にしましょう。\n\n■理由\n命名規則においてテーブル名は複数形であることが求められているためです。")
        if addresses_table.count('\n') < 7: 
            errors.append("カラムの数が少ないです\m実装要件と比較してカラム数が少ないです。\n実装要件及び見本アプリの商品購入ページを参考にカラムを見直しましょう。")
        if addresses_table.count('\n') > 7: 
            errors.append("カラムの数が多いです\m実装要件と比較してカラム数が多いです。\n実装要件及び見本アプリの商品購入ページを参考にカラムを見直しましょう。")
        if not (("order" in addresses_table) or ("purchase" in addresses_table) or ("buy" in addresses_table) or ("record" in addresses_table) or ("tran" in addresses_table)) or ("manage" in addresses_table):
            errors.append("購入履歴テーブルの外部キーカラムが見つかりません\mもし購入履歴テーブルと繋がる外部キーカラムを作成していない場合、配送先住所は購入履歴に紐づく情報なので外部キーカラムを追加しましょう。")
        columns = addresses_table.split("\n")
        columns.pop(0)
        try:
            check_num = 0
            for column in columns:
                check_num += 1
                name,type,option = __split_column(column)
                errors,warnings,continue_flg = __common_check(errors,warnings,name,type,option)
                if continue_flg:
                    continue
                if "item" in name or "user" in name or "product" in name:
                    errors.append(f"不要な外部キーカラムが見つかりました\m{name}カラムが商品やユーザーに紐づく外部キーカラムの場合は削除しましょう。\n\n■理由\n「誰が」「どの商品を購入したか」は全て購入履歴テーブルで管理するためです。")
                    continue
                if not "string" in type and not (("prefecture" in name) or ("order" in name) or ("purchase" in name) or ("buy" in name) or ("record" in name) or ("tran" in name) or ("sender" in name) or ("area" in name) or ("_id" in name)):
                    errors.append(f"{name}カラムは文字列型の方が適切な可能性があります\m{name}カラムに文字列が保存される想定であれば、型を文字列型にしましょう。")
                if "unique:" in option: 
                    errors.append(f"{name}カラムにユニーク制約が見つかりました\m{name}カラムは重複した値を許容するため、オプションからユニーク制約を外しましょう。")
                if not "null:" in option and not ("building" in name or "apart" in name):
                    errors.append(f"{name}カラムにNOTNULL制約が見つかりませんでした\m{name}カラムは入力必須のため、オプションにNOTNULL制約を追加しましょう。\n（建物名カラムであればNOTNULL制約は無しで問題ありません）")
                if ("prefecture" in name or "area" in name):
                    readme = driver.find_element(By.XPATH, '//*[@id="repo-content-pjax-container"]/react-app/div/div/div[1]/div/div/div[2]/div[2]/div/div[3]/div[2]/div/div[3]/section/div/article').text
                    if readme.count(name) != 2:
                        errors.append(f"{name}カラムが商品テーブルに見つかりませんでした\mactivehashを用いる場合、同じ都道府県情報を扱う以下二つのカラム名を同じにすると作成するモデルも一つにすることが可能です。\n・商品テーブルの発送元地域\n・配送先住所テーブルの都道府県")
                    if not "_id" in name: 
                        errors.append(f"{name}のカラム名に_idが見つかりませんでした\m{name}カラムが都道府県カラムの場合、activehashを用いた実装になるためactivehashのルールに沿ったカラム名と型にしましょう。\
                                                                    Activehashにつきましては以下カリキュラムをご参考ください。\n\n\
                                                                    Lesson1 最終課題補足カリキュラム\
                                                                    カテゴリーの選択を工夫しよう")
                    if (name[-4] == "s") and (not "status_id" in name) and (not "address_id" in name):
                        errors.append(f"{name}カラムが複数形_idになっている可能性があります\m{name}カラムがActivehashを用いるカラムの場合、Activehashのルールに沿って「単数形_id」にしましょう。")
                    if not type == "integer":
                        errors.append(f"{name}カラムは数値型の方が適切な可能性があります\m{name}カラムがActivehashを用いるカラムの場合、Activehashのルールに沿って数値型にしましょう。")
                    continue
                if ("building" in name or "apart" in name) and "null:" in option and not "true" in option:
                    errors.append(f"{name}カラムにNOTNULL制約が見つかりました\m{name}カラムが建物名カラムの場合、NOTNULL制約を外しましょう。\n\n■理由\n実装要件において入力任意となっているためです。")
                    continue
                if (("order" in name) or ("purchase" in name) or ("buy" in name) or ("record" in name) or ("tran" in name) or ("manage" in name)):
                    if "_id" in name:
                        errors.append(f"{name}カラムのカラム名に_idが見つかりました\m{name}カラムのカラム名から_idを削除しましょう。\n\n■理由\nreferences型を用いる場合カラム名に_idが自動で付与されるため、DB設計では_idの記載が不要になります。")
                    if not type == "references": 
                        errors.append(f"外部キーカラムがreferences型ではありません\m{name}カラムが外部キーカラムの場合、型をreferences型にしましょう。")
                    if not "foreign_key" in option: 
                        errors.append(f"外部キーカラムに外部キー制約が付与されていません\m{name}カラムが外部キーカラムの場合、オプションに外部キー制約を付与しましょう。")
                    continue
                elif "_id" in name:
                    errors.append(f"{name}カラムのカラム名に_idが見つかりました\m{name}カラムのカラム名から_idを削除しましょう。\n（都道府県カラムの場合はそのままで問題ありません）\n\n■理由\nreferences型を用いる場合、DB設計では_idの記載が不要になるためです。")
        except:
            errors.append("上から"+str(check_num)+"番目のカラムのチェック中にエラーが発生しました。\m"+str(check_num)+"行目付近のマークダウンに不備がないか確認してください")
    return [errors, warnings]

def check_others(driver):
    errors = []
    warnings = []
    try:
        driver.find_element(By.XPATH, "//a[contains(@title,'db/migrate/')]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
    except:
        pass
    else:
        errors.append("マイグレーションファイルの変更点が見つかりました\m現時点でDB設計以外の実装をしてしまうと今後差分を作ることができなくなってしまうため、本ブランチからDB設計以外の実装を削除しましょう。\n（素材ファイルの設置のみであれば問題ありません）")
    
    return [errors,warnings]
