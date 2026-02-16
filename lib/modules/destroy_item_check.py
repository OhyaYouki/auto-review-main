from selenium.webdriver.common.by import By
from lib.modules.common import get_file_text
import re

def check_items_c(driver):
    errors = []
    warnings = []
    try:
        url = driver.find_element(By.XPATH, "//a[contains(@title,'app/controllers/') and contains(@title,'_controller.rb') and (contains(@title,'item') or contains(@title,'product'))]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
        file_text = get_file_text(url,driver,False) #erbファイルの場合はFalseをTrueに変更
    except:
        errors.append("ファイルが見つかりませんでした")
    else:
        if "logger" in file_text: errors.append("Rails.logger.debugが見つかりました\mデバッグ用のRails.logger.debugは削除しましょう。")
        if "binding.pry" in file_text: errors.append("binding.pryの記載があります")
        auth_text = re.search('before_action:authenticate_user!.+?\n',file_text)
        if auth_text == None:
            if re.search('before_action:authenticate_user!\n',file_text):
                errors.append("authenticate_user!が全てのアクションに適応されています")
            elif "user_signed_in?" in file_text:
                warnings.append("user_signed_in?がdestroyアクションに適応されているか確認してください")
            else:
                errors.append("authenticate_user!及びuser_signed_in?が見つかりませんでした")
        else:
            auth_text = auth_text.group()
            if "only:" in auth_text:
                if not ":destroy" in auth_text: errors.append("authenticate_user!メソッドのonlyにdestroyが含まれていません\m◎未ログイン時のページ遷移制限を追加しましょう。\n\n■理由\n商品削除機能の実装要件において未ログイン時のページ遷移制限が求められている為です。")
            if "except:" in auth_text:
                if ":destroy" in auth_text: errors.append("authenticate_user!メソッドのexceptにdestroyが含まれています\m◎未ログイン時のページ遷移制限を追加しましょう。\n\n■理由\n商品削除機能の実装要件において未ログイン時のページ遷移制限が求められている為です。")
        file_text = re.sub('\n','',file_text)
        #destroyの中にifありなしがあるのでprivateまで持ってきてます
        destroy_text = re.search('defdestroy.+?private',file_text)
        if destroy_text == None: 
            errors.append('destroyアクションが定義されていません\m◎destroyアクションが見当たらない為追加しましょう。\n\n■理由\n商品削除機能に必要なアクションの為です。')
        else:
            destroy_text = destroy_text.group()
            destroy_text  = destroy_text.replace("defdestroy","") #頭のアクション名を削除
            destroy_text  = destroy_text.replace("private","") #末尾のprivateを削除
            destroy_text  = re.sub('def.+', '', destroy_text)#他のアクションの記述を全て削除
            destroy_text  = destroy_text[:-3] #defdestroyに対するendを削除
            if re.search('\@.+=.+\.find\(params\[:id]\)',destroy_text) : errors.append("destroyアクション内にインスタンス変数の定義があります（findメソッドがまとめられていません）\m◎findメソッドが複数箇所で使用されている為、beforeアクションでまとめましょう。\n\n■理由\n可読性向上の為です。\nまた保守（修正作業など）が発生した際も手を加えやすくなります。")
            if 'return' in destroy_text: warnings.append('return文が見つかりました（どの条件においてもredirect_toroot_pathが動くかを確認してください）\m◎redirect_toの記述を確認しましょう。\n\n■理由\nreturnに該当しなかったユーザーの遷移先が存在しない可能性がある為です。')
            #商品削除の確認（.destroyがあるかチェック）
            if not ('.destroy' in destroy_text): errors.append('商品を削除している処理が見つかりません\m◎商品を削除できているか確認しましょう。\n\n■理由\n「ログイン状態の場合にのみ、自身が出品した商品情報を削除できること。」という実装条件を満たす為です。')
            #削除機能の中にトップページに遷移する記述があるか確認
            if not ('redirect_toroot_path' in destroy_text or 'redirect_toaction::index' in destroy_text): 
                errors.append('トップページへ遷移するパスが見つかりません\m◎削除が完了した際の遷移先を確認しましょう。\n\n■理由\n「削除が完了したら、トップページに遷移すること。」という実装条件を満たす為です。')
            else:
                #redirect_toがifやunlessの外にあることを確認する
                ifend_text = re.search('if.+?end',destroy_text)
                if ifend_text == None: 
                    pass
                else:
                    ifend_text = ifend_text.group()
                    if ('redirect_toroot_path' in ifend_text or 'redirect_toaction::index' in ifend_text): 
                        if destroy_text.count('redirect_toroot_path') > 1 or destroy_text.count('redirect_toaction::index') > 1:
                            warnings.append('if-end内にトップページに戻る記述が含まれています（redirect_toが二つ以上あるため問題ない可能性が高いです）')
                        else:
                            errors.append('if-end内にトップページに戻る記述が含まれています（destroyアクション内で処理が止まる可能性があります）\mredirect_toの記述を条件式の外に出しましょう。\nまたは条件がFalseになる場合の処理（else文）を記載しましょう。\n\n■理由\n条件式の中に遷移処理を含めていると、何らかのトラブルで条件がFalseになった際に遷移先が存在せず処理が止まってしまうためです。')
                unlessend_text = re.search('unless.+?end',destroy_text)
                if unlessend_text == None: 
                    pass
                else:
                    unlessend_text = unlessend_text.group()
                    if ('redirect_toroot_path' in unlessend_text or 'redirect_toaction::index' in unlessend_text): 
                        if destroy_text.count('redirect_toroot_path') > 1 or destroy_text.count('redirect_toaction::index') > 1:
                            warnings.append('unless-end内にトップページに戻る記述が含まれています（redirect_toが二つ以上あるため問題ない可能性が高いです）')
                        else:
                            errors.append('unless-end内にトップページに戻る記述が含まれています\m◎redirect_toの記述が条件式の範囲外にあることを確認しましょう。\n\n■理由\n条件内に含んでしまっている場合、出品者以外のユーザーが削除しようとしたときの遷移先が存在しない可能性がある為です。')
                #出品者かどうかの条件分岐があるかを確認する
                if not (re.search('if.+?==.+?',destroy_text)\
                    or re.search('if.+?!=.+?else',destroy_text)\
                    or re.search('unless.+?!=.+?',destroy_text)\
                    or re.search('unless.+?==.+?else',destroy_text)\
                        ): 
                    private_text = re.search('private.+',file_text)
                    if private_text:
                        private_text = private_text.group()
                        if  re.search('if.+?!=.+?',private_text)\
                            or re.search('if.+?==.+?else',private_text)\
                            or re.search('returnif.+?==.+?',private_text)\
                            or re.search('unless.+?==.+?',private_text)\
                            or re.search('unless.+?!=.+?else',private_text):
                            warnings.append('privateメソッド内にある出品者かどうかを判別する条件式がdestroyアクションにも適応されているか確認してください\m◎出品者かどうかを判別する条件式がdestroyアクションにも適応されているか確認しましょう。\n\n■理由\n「「ログイン状態の場合にのみ、自身が出品した商品情報を削除できること」とは、詳細ページにおける「削除」ボタンの表示・非表示に加え、コントローラー側でも条件を設けることを指す」という実装条件を満たす為です。')
                        else:
                            errors.append('destroyアクション内に出品者かどうかを判断する条件式が見つかりません\m◎出品者かどうかを判別する条件式がdestroyアクションにも適応されているか確認しましょう。\n\n■理由\n「「ログイン状態の場合にのみ、自身が出品した商品情報を削除できること」とは、詳細ページにおける「削除」ボタンの表示・非表示に加え、コントローラー側でも条件を設けることを指す」という実装条件を満たす為です。')
                    else:
                        errors.append('destroyアクション内に出品者かどうかを判断する条件式が見つかりません\m◎出品者かどうかを判別する条件式がdestroyアクションにも適応されているか確認しましょう。\n\n■理由\n「「ログイン状態の場合にのみ、自身が出品した商品情報を削除できること」とは、詳細ページにおける「削除」ボタンの表示・非表示に加え、コントローラー側でも条件を設けることを指す」という実装条件を満たす為です。')
                # if destroy_text.count('redirect_toroot_path') >= 2 : errors.append("パスのリファクタリングが可能そうです。任意で指摘しましょう")
                # if not ("if" in destroy_text or "unless" in destroy_text):
                #     errors.append("destroyアクション内に出品者かどうかを判断する条件式が見つかりません（before_actionで実装している可能性もあります）")
                # else:
                #     if re.search('if@(item|product)\.destroy',destroy_text): 
                #         errors.append('destroyメソッドに対するエラーハンドリングが見つかりました')
    return [errors,warnings]

def check_show_v(driver):
    errors = []
    warnings = []
    try:
        url = driver.find_element(By.XPATH, "//a[contains(@title,'app/views/') and contains(@title,'show.html.erb') and (contains(@title,'/items/') or contains(@title,'/products/'))]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
        file_text,raw_text = get_file_text(url,driver,True)
    except:
        errors.append("ファイルが見つかりませんでした")
    else:
        if "<%= link_to'削除','#',method::delete,class:'item-destroy'%>" in file_text: errors.append("詳細ページの削除ボタンのリンクが実装されていません\m◎詳細ページの「削除」ボタンのリンク先を実装できているか確認しましょう。\n\n■理由\n「ログイン状態の出品者のみ、詳細ページの削除ボタンを押すと、出品した商品を削除できる」という実装条件を満たす為です。")
    return [errors,warnings]

def check_routes(driver):
    errors = []
    warnings = []
    try:
        url = driver.find_element(By.XPATH, "//a[contains(@title,'config/routes')]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
        file_text = get_file_text(url,driver,False)
    except:
        warnings.append("削除のルーティングの変更点が見つかりません")
    else:
        if not ("resources:items" in file_text or "resources:products" in file_text): errors.append("削除のルーティングの変更点が見つかりません\m◎destroyのルーティングがあるか確認しましょう。\n\n■理由\nコントローラやビューを使用できるようにするためです。")
        else:
            if "only:" in file_text and not ":destroy" in file_text: errors.append("削除に対するルーティングが見つかりません\m◎destroyのルーティングがあるか確認しましょう。\n\n■理由\nコントローラやビューを使用できるようにするためです。")

    return [errors,warnings]
