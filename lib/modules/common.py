from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome import service as fs
from selenium.webdriver.common.by import By
import re

def driver_init(url):
	options = Options()
	options.add_experimental_option("detach", True)
	options.add_experimental_option('excludeSwitches', ['enable-logging'])
	options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
	options.use_chromium = True
	options.add_argument('--headless')
	chrome_service = fs.Service(executable_path=ChromeDriverManager().install())
	driver = webdriver.Chrome(service=chrome_service, options=options)
	driver.implicitly_wait(2)
	driver.get(url)
	return driver

def check_function(driver):
    # txt = driver.find_element(By.CLASS_NAME, 'js-issue-title').text
    import time
    
    # レート制限チェック
    page_title = driver.title
    if "Too many requests" in page_title or "Rate limit" in page_title:
        time.sleep(30)
        driver.refresh()
        time.sleep(5)
        if "Too many requests" in driver.title:
            return 'レート制限'
    
    # 要素取得
    try:
        time.sleep(2)
        txt = driver.find_element(By.CSS_SELECTOR, '.markdown-title').text
    except:
        try:
            txt = driver.find_element(By.TAG_NAME, 'h1').text
            if "Too many requests" in txt:
                return 'レート制限'
        except:
            return '特定不可'
    if "DB" in txt or "ER" in txt or "設計" in txt or "データ" in txt or "README" in txt or "readme" in txt:
        return 'DB'
    if "ユーザー" in txt or "User" in txt or "user" in txt:
        return 'ユーザー'
    if "出品" in txt or "New" in txt or "new" in txt or "Create" in txt or "create" in txt:
        return '出品'
    if "一覧" in txt or "Index" in txt or "index" in txt: 
        return '一覧'
    if "詳細" in txt or "Show" in txt or "show" in txt:
        return '詳細'
    if "編集" in txt or "Edit" in txt or "edit" in txt or "Update" in txt or "update" in txt:
        return '編集'
    if "削除" in txt or "Destroy" in txt or "destroy" in txt or "Delete" in txt or "delete" in txt:
        return '削除'
    if "購入" in txt or "Purchase" in txt or "purchase" in txt or "Order" in txt or "order" in txt:
        return '購入'
    if "Issue1" in txt or "issue１" in txt or "issue1" in txt or "lssue1" in txt or "first_training" in txt:
        return 'Issue1-3'
    if "Issue4" in txt or "issue4" in txt or "issue４" in txt or "lssue4" in txt or "second" in txt or "Second" in txt:
        return 'Issue4-6'
    return '特定不可'

def conversation_check(driver,gyazo_required_num=0,need_whatwhy=True):
    errors = []
    warnings = []
    try:
        pull_text = driver.find_element(By.CSS_SELECTOR,".comment-body").text.lower()
    except:
        errors.append("プルリクエストURLが無効です")
    else:
        if len(driver.find_elements(By.ID,"pull-requests-repo-tab-count")) > 0:
            pull_tab_count = int(driver.find_element(By.ID,"pull-requests-repo-tab-count").get_attribute("title"))
            if pull_tab_count > 1: warnings.append("プルリクエストが二つ以上開かれています（誤ったプルリクエストをレビューしていないか、またレビュー依頼が重複していないかを確認してください）")
        last_text = driver.find_elements(By.CLASS_NAME, "timeline-comment-group")[-1].text.lower()
        if gyazo_required_num:
            gyazo_num = pull_text.count("gyazo") + pull_text.count(".mp4") + len(driver.find_elements(By.TAG_NAME, "animated-image")) + len(driver.find_elements(By.XPATH, "//a[contains(@href,'gyazo.com')]"))
            if gyazo_num < gyazo_required_num: 
                errors.append("gyazoが最低"+str(gyazo_required_num)+"個必要なのに対し"+str(gyazo_num)+"個しか見つかりませんでした")
        if need_whatwhy:
            if not "what"   in pull_text: errors.append("Whatが見つかりませんでした")
            if not "why"    in pull_text: errors.append("Whyが見つかりませんでした")
        if "merged"     in pull_text: errors.append("既にマージされています")  
        if "reviewed"  in last_text: errors.append("前回のレビュー以降の差分が見つかりませんでした")
    return [errors,warnings]

def append_message(error,warning,head,messages):
    add_errors = messages[0]
    add_warnings = messages[1]
    if len(add_errors) != 0:
        error += '*' + head + '*' + '\n'
        for add_error in add_errors:
            text = add_error.split('\m')
            error += '`' + text[0] + '`' + '\n'
            if len(text)==2: error += '```' + text[1] + '```' + '\n'
            error += '\n'
    if len(add_warnings) != 0:
        warning += '*' + head + '*' + '\n'
        for add_warning in add_warnings:
            text = add_warning.split('\m')
            warning += '`' + text[0] + '`' + '\n'
            if len(text)==2: warning += '```' + text[1] + '```' + '\n'
            warning += '\n'
    return error,warning

def output_error(output,messages):
    add_errors = messages[0]
    add_warnings = messages[1]
    if len(add_errors) == 0:
        output.insert('end','--OK','ok')
    else:
        for error in add_errors:
            text = error.split('\m')
            output.insert('end','\n'+text[0],'error')
    if not len(add_warnings) == 0:
        for warning in add_warnings:
            text = warning.split('\m')
            output.insert('end','\n'+text[0],'warning')

def get_file_text(url,driver,erb_flg=False,js_flg=False,no_space_flg=False):
    driver.execute_script("window.open('" + url + "')")
    driver.switch_to.window(driver.window_handles[-1])
    raw_text = driver.find_elements(By.TAG_NAME, "textarea")[-1].text
    raw_split_text = raw_text.replace(' ','').replace('\"','\'').split('\n')
    file_texts = []
    for row in raw_split_text:
        file_text = ''
        if erb_flg:
            file_text = re.sub('<%#.+%>', '',row)
        elif js_flg:
            file_text = re.sub('//.+', '',row)
        else:
            file_text = re.sub('#.+', '',row)
        if not file_text == '':
            file_texts.append(file_text)
    driver.switch_to.window(driver.window_handles[0])
    if erb_flg:
        return '\n'.join(file_texts),raw_text
    elif no_space_flg:
        return '\n'.join(file_texts),raw_text.replace(' ','').replace('\"','\'')
    else:
        return '\n'.join(file_texts)
    
def check_text(file_text,unnecessary_text,necessary_text,check_num_text):
    errors=[]
    warnings=[]
    for text, infos in unnecessary_text.items():
        if text in file_text:
            if infos["error"]:
                errors.append(infos["message"])
            else:
                warnings.append(infos["message"])

    for text, infos in necessary_text.items():
        if text not in file_text:
            if infos["error"]:
                errors.append(infos["message"])
            else:
                warnings.append(infos["message"])
    
    for text, infos in check_num_text.items():
        if infos["method"] == "over":
            if file_text.count(text) > infos["num"]:
                if infos["error"]:
                    errors.append(infos["message"])
                else:
                    warnings.append(infos["message"])
        elif infos["method"] == "under":
            if file_text.count(text) < infos["num"]:
                if infos["error"]:
                    errors.append(infos["message"])
                else:
                    warnings.append(infos["message"])
        elif infos["method"] == "not_equal":
            if file_text.count(text) != infos["num"]:
                if infos["error"]:
                    errors.append(infos["message"])
                else:
                    warnings.append(infos["message"])
    
    return errors,warnings

def check_comment(raw_text,errors):
    if "しょう" in raw_text : 
        errors.append("実装案内コメント（〜しましょう）が残っています\m「〜しましょう」で終わる実装案内コメントは実装完了後に削除しましょう。\n企業提出時に実装案内コメントが残っていないようにするためです。")
    return errors

def auth_check(file_text,action,errors,warnings):
    auth_text = re.search('before_action:authenticate_user!.+?\n',file_text)
    if auth_text == None:
        if re.search('before_action:authenticate_user!\n',file_text):
            errors.append("authenticate_user!が全てのアクションに適応されています")
        elif "user_signed_in?" in file_text:
            warnings.append(f"user_signed_in?が{action}アクションに適応されているか確認してください")
        else:
            errors.append("authenticate_user!及びuser_signed_in?が見つかりませんでした")
    else:
        auth_text = auth_text.group()
        if "only:" in auth_text:
            if not action in auth_text: errors.append(f"authenticate_user!メソッドのonlyに{action}が含まれていません\m◎未ログイン時のページ遷移制限を追加しましょう。\n\n■理由\n実装要件において未ログイン時のページ遷移制限が求められている為です。")
        if "except:" in auth_text:
            if action in auth_text: errors.append(f"authenticate_user!メソッドのexceptに{action}が含まれています")
        if "new_user_session_path" in file_text:
            warnings.append(f"authenticate_user!メソッドとnew_user_session_pathがどちらも使用されているため、処理の重複がないか確認してください")
