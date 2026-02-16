from selenium.webdriver.common.by import By
from lib.modules.common import get_file_text, check_text, check_comment
import re

def check_app_c(driver):
    errors = []
    warnings = []
    # 不要な記述がされている場合の指摘
    UNNECESSARY_TEXT = {
        "binding.pry"       : {"error": True, "message": "binding.pryが見つかりました\mデバッグ用のbinding.pryメソッドは全て削除しましょう。"},
        "authenticate_user!": {"error": True, "message": "authenticate_user!メソッドが見つかりました\mapplicationコントローラーからauthenticate_user!メソッドを削除しましょう。\nユーザー管理機能の実装要件において、未ログイン時のページ遷移制限は求められていないためです。"}
    }
    
    # 必要な記述がされていない場合の指摘
    NECESSARY_TEXT = {
        "before_action:configure_permitted_parameters,if::devise_controller?": {"error": True, "message": "configure_permitted_parameterメソッドの呼び出し式が見つかりませんでした。\mbefore_actionでconfigure_permitted_parameterメソッドを呼び出しましょう。\ndeviseがデフォルトで用意していないカラムについてはストロングパラメータを設定しないと保存できないためです。"},
        "defconfigure_permitted_parameters" : {"error": True, "message": "configure_permitted_parameterメソッドの定義が見つかりませんでした。\mapplicationコントローラーにconfigure_permitted_parameterメソッドを定義しましょう。\ndeviseがデフォルトで用意していないカラムについてはストロングパラメータを設定しないと保存できないためです。"},
        "devise_parameter_sanitizer"        : {"error": True, "message": "devise_parameter_sanitizerメソッドが見つかりませんでした。\mdevise_parameter_sanitizerメソッドを使用してストロングパラメータの設定を行いましょう。\ndeviseがデフォルトで用意していないカラムについてはストロングパラメータを設定しないと保存できないためです。"}
    }
    
    # 記述の個数に誤りがある場合の指摘
    CHECK_NUM_TEXT = {
        "devise_parameter_sanitizer": {"error": True, "num":1, "method":"over", "message": "devise_parameter_sanitizerメソッドが二個以上見つかりました\mdevise_parameter_sanitizerメソッドを一つにまとめましょう。\n\n■理由\n重複した内容はリファクタリングされることが好ましいためです。"}
    }

    try:
        url = driver.find_element(By.XPATH, "//a[contains(@title,'app/controllers/application_controller.rb')]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
        file_text = get_file_text(url,driver)
    except:
        errors.append("差分が見つかりませんでした\mapplicationコントローラーの変更点をコミットプッシュできているか確認しましょう。")
    else:
        errors, warnings = check_text(file_text,UNNECESSARY_TEXT,NECESSARY_TEXT,CHECK_NUM_TEXT)

    return [errors, warnings]

def check_user_m(driver):
    errors = []
    warnings = []
    # 不要な記述がされている場合の指摘
    UNNECESSARY_TEXT = {
        "validates:email"                   : {"error": True, "message": "emailに対するバリデーションが見つかりました\memailに対するバリデーションを削除しましょう。\n\n■理由\ndeviseの機能によりデフォルトで設定されるためです。"},
        "validates:password_confirmation"   : {"error": True, "message": "password_confirmationに対するバリデーションが見つかりました\mpassword_confirmationに対するバリデーションを削除しましょう。\n\n■理由\ndeviseの機能によりデフォルトで設定されるためです。"},
        "has_many"                          : {"error": True, "message": "has_manyが見つかりました\mアソシエーションを削除しましょう。\n\n■理由\nユーザー管理機能の時点ではユーザーモデルしか作成せず、他モデルとのアソシエーションが不要になるためです。"},
        "has_one"                           : {"error": True, "message": "has_oneが見つかりました\mアソシエーションを削除しましょう。\n\n■理由\nユーザー管理機能の時点ではユーザーモデルしか作成せず、他モデルとのアソシエーションが不要になるためです。"},
        "belongs_to"                        : {"error": True, "message": "belongs_toが見つかりました\mアソシエーションを削除しましょう。\n\n■理由\nユーザー管理機能の時点ではユーザーモデルしか作成せず、他モデルとのアソシエーションが不要になるためです。"}
    }
    
    # 必要な記述がされていない場合の指摘
    NECESSARY_TEXT = {
        "devise:database_authenticatable,:registerable,\n:recoverable,:rememberable,:validatable": {"error": True, "message": "deviseの記述が見つかりませんでした\mモデルにdeviseの記述がないため、deviseの導入が正しく行われているかを確認しましょう。"}
    }
    
    # 記述の個数に誤りがある場合の指摘
    CHECK_NUM_TEXT = {}
    
    # その他の複雑な指摘
    PASSWORD_ERR_INVALID            = "passwordにwith:以外のバリデーションが見つかりました\mpasswordに不要なバリデーションが付与されていないか確認しましょう。\n空や6文字未満についてはデフォルトで制限されているためバリデーションは不要です。"
    NAME_REGEX_ERR_NOT_FOUND        = "氏名の正規表現/\A[ぁ-んァ-ヶ一-龥々ー]+\z/が見つかりませんでした\m要件に沿って氏名に対し全角のバリデーションが付与されているかを確認しましょう。"
    NAME_KANA_ERR_INCORRECT         = "氏名（カナ）の正規表現[ァ-ヶ一]の一が漢字の1です\m正規表現[ァ-ヶ一]の一が漢字の1になってますので、長音符のーに修正しましょう。"
    NAME_KANA_ERR_NOT_FOUND         = "氏名（カナ）の正規表現/\A[ァ-ヶー]+\z/が見つかりませんでした\m要件に沿って氏名（カナ）に対しカタカナのバリデーションが付与されているかを確認しましょう。"
    PASSWORD_MIXED_ERR_NOT_FOUND    = "パスワードの半角英数混合の正規表現/\A(?=.*?[a-z])(?=.*?[\d])[a-z\d]+\z/iが見つかりませんでした\m要件に沿ってパスワードに半角英数字混合のバリデーションが付与されているかを確認しましょう。"

    try:
        url = driver.find_element(By.XPATH, "//a[contains(@title,'app/models/user.rb')]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
        file_text = get_file_text(url,driver)
    except:
        errors.append("差分が見つかりませんでした\mユーザーモデルの変更点をコミットプッシュできているか確認しましょう。")
    else:
        errors, warnings = check_text(file_text,UNNECESSARY_TEXT,NECESSARY_TEXT,CHECK_NUM_TEXT)
        password_texts = re.findall("validates:password\,.+?\n",file_text)
        password_text = ''
        for text in password_texts:
            if text[-2] == ",":
                if re.search(text + ".+?\n", file_text).group()[-2] == ",":
                    text = re.search(text + ".+?\n.+?\n", file_text).group()
                else:
                    text = re.search(text + ".+?\n", file_text).group()
            password_text += text

        if password_text and password_text.count(",") > 1+password_text.count("message:"):
            errors.append(PASSWORD_ERR_INVALID)

        name_regexes = ["/\A[ぁ-んァ-ヶ一-龥々ー]+\z/", r"/\A(?:\p{Hiragana}|\p{Katakana}|[ー－]|[一-龠々])+\z/"]
        if not any(name_regex in file_text for name_regex in name_regexes):
            errors.append(NAME_REGEX_ERR_NOT_FOUND)

        name_kana_regexes = ["/\A[ァ-ヶー]+\z/", "/\A[ァ-ヶー－]+\z/", "/\A[ァ-ヴー]+\z/", "/\A[ァ-ヴー－]+\z/", r"/\A[\p{katakana}ー]+\z/",r"/\A[\p{katakana} ー－&&[^ -~｡-ﾟ]+\z/]", r"/\A[\p{katakana}\p{blank}ー－]+\z/"]
        if not any(regex in file_text for regex in name_kana_regexes):
            if "\A[ァ-ヶ一]+\z" in file_text:
                errors.append(NAME_KANA_ERR_INCORRECT)
            else:
                errors.append(NAME_KANA_ERR_NOT_FOUND)

        password_regexes = [ "/\A(?=.*?[a-z])(?=.*?[\d])[a-z\d]+\z/", "/\A(?=.*?[a-z])(?=.*?\d)[a-z\d]+\z/", "/\A(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z\d]+\z/"]
        if not any(regex in file_text for regex in password_regexes):
            errors.append(PASSWORD_MIXED_ERR_NOT_FOUND)

    return [errors,warnings]

def check_session_v(driver):
    errors = []
    warnings = []
    # 不要な記述がされている場合の指摘
    UNNECESSARY_TEXT = {
    }

    # 必要な記述がされていない場合の指摘
    NECESSARY_TEXT = {
        "model:@user"               : {"error": True, "message": "form_withのmodel指定が正しくない可能性があります\m改めてログインができるかを確認し、ログインができない場合はモデルオプションにインスタンス変数を設定できているか確認しましょう。"},
        "url:user_session_path"     : {"error": True, "message": "form_withのurl指定が正しくない可能性があります\m改めてログインができるかを確認し、ログインができない場合はurlオプションが設定できているか確認しましょう。"},
        "f.email_field:email"       : {"error": True, "message": "email入力欄のname属性が正しくない可能性があります\m改めてログインができるかを確認し、ログインができない場合はemailのname属性の記述を見直しましょう。"},
        "f.password_field:password" : {"error": True, "message": "password入力欄のname属性が正しくない可能性があります\m改めてログインができるかを確認し、ログインができない場合はpasswordのname属性の記述を見直しましょう。"}
    }
    #        "url:'/users/sign_in'"      : {"error": False, "message": "form_withのurl指定にprefixが用いられていません(修正任意)"}
    
    # 記述の個数に誤りがある場合の指摘
    CHECK_NUM_TEXT = {
        "form_with": {"error": True, "num":1, "method":"over", "message": "form_withが二つ以上見つかりました。\m改めてログインができるかを確認し、ログインができない場合は不要なform_withを削除しましょう。"}
    }
    
    try:
        url = driver.find_element(By.XPATH, "//a[contains(@title,'app/views/devise/sessions/new.html.erb')]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
        file_text,raw_text = get_file_text(url,driver,True)
    except:
        errors.append("ファイルが見つかりませんでした\mログインページのビューファイルの変更点をコミットプッシュできているか確認しましょう。")
    else:
        errors, warnings = check_text(file_text,UNNECESSARY_TEXT,NECESSARY_TEXT,CHECK_NUM_TEXT)
        errors = check_comment(raw_text,errors)

    return [errors, warnings]

def check_registration_v(driver):
    errors = []
    warnings = []
    # 不要な記述がされている場合の指摘
    UNNECESSARY_TEXT = {
    }

    # 必要な記述がされていない場合の指摘
    NECESSARY_TEXT = {
        "model:@user": {"error": True, "message": "form_withのmodel指定が正しくない可能性があります\m改めてユーザー登録できるかを確認し、登録できない場合はモデルオプションにインスタンス変数を設定できているか確認しましょう。"},
        "f.email_field:email": {"error": True, "message": "email入力欄のname属性が正しくない可能性があります\m改めてユーザー登録できるかを確認し、登録できない場合はemailのname属性の記述を修正しましょう。"},
        "f.password_field:password": {"error": True, "message": "password入力欄のname属性が正しくない可能性があります\m改めてユーザー登録できるかを確認し、登録できない場合はpasswordのname属性の記述を修正しましょう。"},
        "f.password_field:password_confirmation": {"error": True, "message": "password_confirmation入力欄のname属性が正しくない可能性があります\m改めてユーザー登録できるかを確認し、登録できない場合はpassword_confirmationのname属性の記述を修正しましょう。"}
    }
    
    # 記述の個数に誤りがある場合の指摘
    CHECK_NUM_TEXT = {
        "form_with": {"error": True, "num":1, "method":"over", "message": "form_withが二つ以上見つかりました。\m改めてユーザー登録できるかを確認し、登録できない場合は不要なform_withを削除しましょう。"}
    }
    
    # その他の複雑な指摘
    FORM_URL_ERR = "form_withのurl指定が正しくない可能性があります\m改めてユーザー登録できるかを確認し、登録できない場合はurlオプションが設定できているか確認しましょう。"
    # FORM_URL_WARN = "form_withのurl指定にprefixが用いられていません(修正任意)"
    RENDER_ERR_MSG_ERR = "エラーを表示する部分テンプレートの呼び出しが正しくない可能性があります\mユーザー登録失敗時にエラーメッセージが正しく表示されない場合、_error_messages.html.erbの呼び出しの記述を見直しましょう。"

    try:
        url = driver.find_element(By.XPATH, "//a[contains(@title,'app/views/devise/registrations/new.html.erb')]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
        file_text,raw_text = get_file_text(url,driver,True)
    except:
        errors.append("ファイルが見つかりませんでした\m登録ページのビューファイルの変更点をコミットプッシュできているか確認しましょう。")
    else:
        errors, warnings = check_text(file_text,UNNECESSARY_TEXT,NECESSARY_TEXT,CHECK_NUM_TEXT)
        errors = check_comment(raw_text,errors)
        if "url:user_registration_path" not in file_text:
            if "url:'/users'" in file_text:
                pass
                # warnings.append(FORM_URL_WARN)
            else:
                errors.append(FORM_URL_ERR)

        error_msg_renders = ["<%=render'shared/error_messages'", "<%=renderpartial:'shared/error_messages'"]
        if not any(render in file_text for render in error_msg_renders):
            errors.append(RENDER_ERR_MSG_ERR)
    return [errors,warnings]

def check_header_v(driver):
    errors = []
    warnings = []
    # 不要な記述がされている場合の指摘
    UNNECESSARY_TEXT = {
    }

    # 必要な記述がされていない場合の指摘
    NECESSARY_TEXT = {
        "<%ifuser_signed_in?%>"         : {"error": True, "message": "ログインの有無による条件分岐が正しくない可能性があります\mログインの有無によってヘッダーの表示が変わるかを確認し、変わらない場合は条件式を修正しましょう。"},
        "<%else%>"                      : {"error": True, "message": "ログインの有無による条件分岐が正しくない可能性があります\mログインの有無によってヘッダーの表示が変わるかを確認し、変わらない場合は条件式を修正しましょう。"},
        "<li><%=link_tocurrent_user."   : {"error": True, "message": "ログイン中のユーザー名の表示が正しくない可能性があります\mヘッダーにユーザーのニックネームが見本アプリ通りに表示されるかを確認し、表示されない場合はビューファイルの該当箇所を修正しましょう。"},
        "<li><%=link_to'ログアウト',destroy_user_session_path,": {"error": True, "message": "ログアウトボタンの表示かパスが正しくない可能性があります\mヘッダーにログアウトボタンが表示され、クリックすると正しくログアウトがされるかを確認してください。\nもし期待通りでない場合はビューファイルの該当箇所を修正しましょう。"}
    }
    
    # 記述の個数に誤りがある場合の指摘
    CHECK_NUM_TEXT = {}
    
    # その他の複雑な指摘
    LOGIN_PATH_ERR = "ログインボタンの表示かパスが正しくない可能性があります\mヘッダーにログインボタンが見本アプリ通りに表示され、クリックすると正しくログインページに遷移するかを確認してください。\nもし期待通りでない場合はビューファイルの該当箇所を修正しましょう。"
    SIGNUP_PATH_ERR = "新規登録ボタンの表示かパスが正しくない可能性があります\mヘッダーに新規登録ボタンが見本アプリ通りに表示され、クリックすると正しく新規登録ページに遷移するかを確認してください。\nもし期待通りでない場合はビューファイルの該当箇所を修正しましょう。"

    try:
        url = driver.find_element(By.XPATH, "//a[contains(@title,'app/views/shared/_header.html.erb')]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
        file_text,raw_text = get_file_text(url,driver,True)
    except:
        errors.append("ファイルが見つかりませんでした\mヘッダーのビューファイルの変更点をコミットプッシュできているか確認しましょう。")
    else:
        errors, warnings = check_text(file_text,UNNECESSARY_TEXT,NECESSARY_TEXT,CHECK_NUM_TEXT)
        errors = check_comment(raw_text,errors)
        
        login_path_texts = ["<li><%=link_to'ログイン',new_user_session_path", "<li><%=link_to'ログイン','/users/sign_in'"]
        if not any(text in file_text for text in login_path_texts):
            errors.append(LOGIN_PATH_ERR)

        signup_path_texts = ["<li><%=link_to'新規登録',new_user_registration_path", "<li><%=link_to'新規登録','/users/sign_up'"]
        if not any(text in file_text for text in signup_path_texts):
            errors.append(SIGNUP_PATH_ERR)
    return [errors,warnings]

# 現在はチェックしていない
def check_routes(driver):
    errors = []
    warnings = []
    # 不要な記述がされている場合の指摘
    UNNECESSARY_TEXT = {}

    # 必要な記述がされていない場合の指摘
    NECESSARY_TEXT = {
        "devise_for:users": {"error": True, "message": "devise_for:usersの変更点が見つかりません\mdeviseのルーティングを設定しましょう。\n\n■理由\ndeviseを用いたユーザー管理機能を実装するためです。\ndeviseを正しく導入することで専用のルーティングが自動生成されます。\ndeviseの導入が正しく行えているかどうかを確認してみましょう。"}
    }
    
    # 記述の個数に誤りがある場合の指摘
    CHECK_NUM_TEXT = {}

    try:
        url = driver.find_element(By.XPATH, "//a[contains(@title,'config/routes.rb')]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
        file_text = get_file_text(url,driver,False) #erbファイルの場合はFalseをTrueに変更
    except:
        errors.append("devise_for:usersの変更点が見つかりません\mdeviseのルーティングを設定しましょう。\n\n■理由\ndeviseを用いたユーザー管理機能を実装するためです。\ndeviseを正しく導入することで専用のルーティングが自動生成されます。\ndeviseの導入が正しく行えているかどうかを確認してみましょう。")
    else:
        errors, warnings = check_text(file_text,UNNECESSARY_TEXT,NECESSARY_TEXT,CHECK_NUM_TEXT)
    return [errors,warnings]

def check_user_mig(driver):
    errors = []
    warnings = []
    # 不要な記述がされている場合の指摘
    UNNECESSARY_TEXT = {}

    # 必要な記述がされていない場合の指摘
    NECESSARY_TEXT = {}
    
    # 記述の個数に誤りがある場合の指摘
    CHECK_NUM_TEXT = {
        "t.date:": {"error": True, "num":1, "method":"not_equal", "message": "date型のカラムの数が1個ではありませんでした\mDB設計に沿って正しくdate型のカラムを作成できているか確認しましょう。"},
        "t.string": {"error": True, "num":8, "method":"not_equal", "message": "string型のカラムの数が8個ではありませんでした\mDB設計に沿って正しくstring型のカラムを作成できているか確認しましょう。"},
        "null:false": {"error": True, "num":9, "method":"not_equal", "message": "null:falseの数が9個ではありませんでした\mDB設計に沿って正しくNOTNULL制約を付与できているか確認しましょう。"}
    }

    # その他の複雑な指摘
    ERROR_EMAIL_COLUMN_MISSING = "emailカラムの記述が見つかりませんでした\mDB設計に沿って正しくemailカラムを作成できているか確認しましょう。"
    ERROR_EMAIL_COLUMN_UNIQUE = "emailカラムに対するunique:trueが見つかりました\mdeviseがデフォルトでUNIQUE制約を付与しているため、emailカラムに対するunique:trueは削除して問題ございません。"

    try:
        url = driver.find_element(By.XPATH, "//a[contains(@title,'db/migrate') and contains(@title,'devise_create_users.rb')]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
        file_text = get_file_text(url,driver,False)
    except:
        errors.append("ファイルが見つかりませんでした\mマイグレーションファイルの変更点をコミットプッシュできているか確認しましょう。")
    else:
        errors, warnings = check_text(file_text,UNNECESSARY_TEXT,NECESSARY_TEXT,CHECK_NUM_TEXT)

        email_text = re.search("t.string:email.+?\n",file_text)
        if email_text == None:
            errors.append(ERROR_EMAIL_COLUMN_MISSING)
        else:
            email_text = email_text.group()
            if "unique:true" in email_text: errors.append(ERROR_EMAIL_COLUMN_UNIQUE)

    return [errors,warnings]

def check_user_f(driver):
    errors = []
    warnings = []
    # 不要な記述がされている場合の指摘
    UNNECESSARY_TEXT = {}

    # 必要な記述がされていない場合の指摘
    NECESSARY_TEXT = {
        "password{":                {"error": True, "message": "passwordが見つかりませんでした\mユーザーの作成に必要なpassword属性に対する値を用意できているか確認しましょう。"},
        "password_confirmation{" :  {"error": True, "message": "password_confirmationが見つかりませんでした\mユーザーの作成に必要なpassword_confirmation属性に対する値を用意できているか確認しましょう。"},
        "email{" :                  {"error": True, "message": "emailが見つかりませんでした\mユーザーの作成に必要なemail属性に対する値を用意できているか確認しましょう。"}
    }
    
    # 記述の個数に誤りがある場合の指摘
    CHECK_NUM_TEXT = {
        "{": {"error":True, "num":9, "method":"under", "message":"値が不足している可能性があります。\mユーザーの作成に必要な9個の属性に対する値を全て用意できているか確認しましょう。"}
    }

    
    # その他の複雑な指摘
    # NICKNAME_MISSING = "nicknameが見つかりません\mnicknameカラムを追加しましょう。\n現状、nicknameのfactoryが存在しない、もしくは正しく実装されていないご状況です。"
    WAR_EMAIL_FAKER = "email属性の値にFakerが用いられていない可能性があります\memailカラムにはUNIQUE制約が付与されているため、Fakerを用いて毎回異なる値になるようにしましょう。"
    # PASS_MISSING = "passwordが見つかりません\mpasswordカラムを追加しましょう。\n現状、passwordのfactoryが存在しない、もしくは正しく実装されていないご状況です。"
    PASS_INCOLLECT = "password属性の値がFakerのみで構成されている可能性があります\mFakerのみですと英字のみや数字のみのpasswordが生成されてしまう可能性があります。\npassword {Fakerによって生成された文字列+'1a'}のように'1a'を足すことで必ず半角英数字混合になるようにしましょう。"
    PASS_CONFIRM = "password_confirmationの値がpasswordと一致していない可能性があります\mpasswordとpassword_confirmationの値が等しくない場合は、要件に沿って両者の値を等しくしましょう。"
    try:
        url = driver.find_element(By.XPATH, "//a[contains(@title,'spec/factories/users.rb')]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
        file_text = get_file_text(url,driver,False)
    except:
        errors.append("ファイルが見つかりませんでした\mfactorybotファイルの変更点をコミットプッシュできているか確認しましょう。")
    else:
        errors, warnings = check_text(file_text,UNNECESSARY_TEXT,NECESSARY_TEXT,CHECK_NUM_TEXT)
        
        # nickname_texts = ["nickname{","name{"]
        # if not any(text in file_text for text in nickname_texts):
        #     errors.append(NICKNAME_MISSING)

        faker_texts = ["Faker::Internet.free_email", "Faker::Internet.unique.email", "Faker::Internet.email"]
        if not any(text in file_text for text in faker_texts):
            errors.append(WAR_EMAIL_FAKER)

        password_text = re.search('password\{.+?\}',file_text)
        if password_text == None:
            # errors.append(PASS_MISSING)
            pass
        else:
            password_text = password_text.group()
            if "Faker" in password_text and not "+" in password_text:
                if not "min_alpha" in password_text or not "min_numeric" in password_text: errors.append(PASS_INCOLLECT)
        
        password_conf_texts = ["{password}","=password"]
        if not any(text in file_text for text in password_conf_texts):
            errors.append(PASS_CONFIRM)
    return [errors,warnings]

def check_user_t(driver):
    errors = []
    warnings = []
    # 不要な記述がされている場合の指摘
    UNNECESSARY_TEXT = {}

    # 必要な記述がされていない場合の指摘
    NECESSARY_TEXT = {}
    
    # 重複した記述がある場合の指摘
    CHECK_NUM_TEXT = {
        "FactoryBot.build": {"error": True, "num":2, "method":"over", "message": "FactoryBot.buildが3つ以上見つかりました\mユーザーを作成する処理をbeforeブロックにまとめられているか確認しましょう。"}
    }

    try:
        url = driver.find_element(By.XPATH, "//a[contains(@title,'spec/models/user_spec.rb')]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
        file_text = get_file_text(url,driver,False) #erbファイルの場合はFalseをTrueに変更
    except:
        errors.append("ファイルが見つかりませんでした\m単体テストファイルの変更点をコミットプッシュできているか確認しましょう。")
    else:
        errors, warnings = check_text(file_text,UNNECESSARY_TEXT,NECESSARY_TEXT,CHECK_NUM_TEXT)
        file_text = re.sub('\n','',file_text)
        before_text = re.search('beforedo.+?end',file_text)
        if before_text == None: 
            errors.append('beforeの記述が見つかりませんでした\mbeforeブロックを正しい位置に作成できているかを確認しましょう。')
        else:
            before_text = before_text.group()
            if not '@user=FactoryBot.build(:user)' in before_text: errors.append('before内にfactorybotを用いたユーザーの定義が見つかりませんでした\mbeforeブロック内でユーザーをfactorybotで作成できているかを確認しましょう。')
            file_text = file_text[len(before_text):]
        
        valid_text = re.search('context.+?できる.+?endend',file_text)
        if valid_text == None:
            valid_text = re.search('context.+?正常.+?endend',file_text)

        if valid_text == None: 
            errors.append('正常系テストのcontextが見つかりませんでした\m過去アプリと同様に正常系テストをcontextでグループ分けできているかを確認しましょう。')
        else:
            valid_text = valid_text.group()
            if not 'expect(@user).tobe_valid' in valid_text: 
                errors.append('be_validのテストが見つかりませんでした\mbe_validマッチャを用いて正常系テストを実装できているかを確認しましょう。')
            # if valid_text.count('expect') > 1: errors.append('正常系テストの数が多いです')
            file_text = file_text[len(valid_text):]

        invalid_text = re.search('context.+?できない.+?endend',file_text)
        if invalid_text == None:
            invalid_text = re.search('context.+?異常.+?endend',file_text)
        invalid_count = 8
        if invalid_text: 
            invalid_text = invalid_text.group()
            error_flg = False
            if invalid_text.count("can'tbeblank") < 8: 
                errors.append("異常系テスト-空が"+ str(invalid_text.count("can'tbeblank"))+"個しか見つかりませんでした\m空では登録できないテストを8カラムに対して実装できているか、またinclude()内に期待されるエラーメッセージを入れているかを確認しましょう。")
                error_flg = True
            if not 'Emailhasalreadybeentaken' in invalid_text: 
                errors.append('異常系テスト-emailの重複が見つかりませんでした\m重複したemailでは登録できないテストを実装できているか、またinclude()内に期待されるエラーメッセージを入れているかを確認しましょう。')
                error_flg = True
            if not 'Emailisinvalid' in invalid_text: 
                errors.append('異常系テスト-emailの@無しが見つかりませんでした\m@を含まないemailでは登録できないテストを実装できているか、またinclude()内に期待されるエラーメッセージを入れているかを確認しましょう。')
                error_flg = True
            if not 'Passwordistooshort(minimumis6characters)' in invalid_text: 
                errors.append('異常系テスト-passwordの6文字未満が見つかりませんでした\m6文字未満のpasswordでは登録できないテストを実装できているか、またinclude()内に期待されるエラーメッセージを入れているかを確認しましょう。')
                error_flg = True
            if invalid_text.count('Passwordisinvalid') < 3: 
                errors.append('異常系テスト-passwordの異常値が3個見つかりませんでした\m(数字のみ/英字のみ/全角を含む)パスワードでは登録できないテストを全て実装できているか、またinclude()内に期待されるエラーメッセージを入れているかを確認しましょう。')
                error_flg = True
            if not "Passwordconfirmationdoesn'tmatchPassword" in invalid_text: 
                errors.append('異常系テスト-password_confirmationの不一致が見つかりませんでした\mpaasswordと一致していないpassword_confirmationでは登録できないテストを実装できているか、またinclude()内に期待されるエラーメッセージを入れているかを確認しましょう。')
                error_flg = True
            invalid_count -= 3 - invalid_text.count('Passwordisinvalid')
            invalid_count -= 1 - invalid_text.count('Emailisinvalid')
            if invalid_text.count('invalid') < invalid_count and not "Full-width characters" in invalid_text: 
                errors.append('異常系テスト-名前の異常値が4個見つかりませんでした\m異常値を含む名前（姓/名/姓(カナ)/名(カナ)）では登録できないテストを全て実装できているか、またinclude()内に期待されるエラーメッセージを入れているかを確認しましょう。')
                error_flg = True
            if invalid_text.count("expect") < 19: 
                errors.append('異常系テストが'+str(invalid_text.count('expect'))+'個しか見つかりませんでした\m要件に沿って以下の項目全ての異常系テストを実装できているかを確認してください。\n \
・nicknameが空では登録できない\n \
・メールアドレスが空では登録できない\n \
・重複したメールアドレスは登録できない\n \
・メールアドレスに@を含まない場合は登録できない\n \
・パスワードが空では登録できない\n \
・パスワードが6文字未満では登録できない\n \
・英字のみのパスワードでは登録できない\n \
・数字のみのパスワードでは登録できない\n \
・全角文字を含むパスワードでは登録できない\n \
・パスワードとパスワード（確認用）が不一致だと登録できない\n \
・姓（全角）が空だと登録できない\n \
・姓（全角）に半角文字が含まれていると登録できない\n \
・名（全角）が空だと登録できない\n \
・名（全角）に半角文字が含まれていると登録できない\n \
・姓（カナ）が空だと登録できない\n \
・姓（カナ）にカタカナ以外の文字（平仮名・漢字・英数字・記号）が含まれていると登録できない\n \
・名（カナ）が空だと登録できない\n \
・名（カナ）にカタカナ以外の文字（平仮名・漢字・英数字・記号）が含まれていると登録できない\n \
・生年月日が空だと登録できない\n')
            elif error_flg:
                errors.append('↑↑異常系テストの数は足りているので、問題ない可能性が高いです↑↑')
        else:
            errors.append('異常系テストのcontextが見つかりませんでした\m過去アプリと同様に異常系テストをcontextでグループ分けできているかを確認しましょう。')
            if file_text.count("can'tbeblank") < 8: 
                errors.append("異常系テスト-空が"+ str(file_text.count("can'tbeblank"))+"個しか見つかりませんでした\m空では登録できないテストを8カラムに対して実装できているか、またinclude()内に期待されるエラーメッセージを入れているかを確認しましょう。")
            if not 'Emailhasalreadybeentaken' in file_text: 
                errors.append('異常系テスト-emailの重複が見つかりませんでした\m重複したemailでは登録できないテストを実装できているか、またinclude()内に期待されるエラーメッセージを入れているかを確認しましょう。')
            if not 'Emailisinvalid' in file_text: 
                errors.append('異常系テスト-emailの@無しが見つかりませんでした\m@を含まないemailでは登録できないテストを実装できているか、またinclude()内に期待されるエラーメッセージを入れているかを確認しましょう。')
            if not 'Passwordistooshort(minimumis6characters)' in file_text: 
                errors.append('異常系テスト-passwordの6文字未満が見つかりませんでした\m6文字未満のpasswordでは登録できないテストを実装できているか、またinclude()内に期待されるエラーメッセージを入れているかを確認しましょう。')
            if file_text.count('Passwordisinvalid') < 3: 
                errors.append('異常系テスト-passwordの異常値が3個見つかりませんでした\m(数字のみ/英字のみ/全角を含む)パスワードでは登録できないテストを全て実装できているか、またinclude()内に期待されるエラーメッセージを入れているかを確認しましょう。')
            if not "Passwordconfirmationdoesn'tmatchPassword" in file_text: 
                errors.append('異常系テスト-password_confirmationの不一致が見つかりませんでした\mpaasswordと一致していないpassword_confirmationでは登録できないテストを実装できているか、またinclude()内に期待されるエラーメッセージを入れているかを確認しましょう。')
            invalid_count -= 3 - file_text.count('Passwordisinvalid')
            invalid_count -= 1 - file_text.count('Emailisinvalid')
            if file_text.count('invalid') < invalid_count and not "Full-width characters" in file_text: 
                errors.append('異常系テスト-名前の異常値が4個見つかりませんでした\m異常値を含む名前（姓/名/姓(カナ)/名(カナ)）では登録できないテストを全て実装できているか、またinclude()内に期待されるエラーメッセージを入れているかを確認しましょう。')
                error_flg = True
        include_texts = re.findall('include.+?\n',file_text)
        cant_texts = []
        for include_text in include_texts:
            if include_text.count(",") > 0 and include_text.count("'") >=4: 
                errors.append(include_text.replace("\n","")+'のinclude内にエラーメッセージが二つ見つかりました。\mエラーメッセージは適切な内容を一つのみ記載することが好ましいため、不要なエラーメッセージを削除しましょう。')
            if "can'tbeblank" in include_text:
                cant_texts.append(include_text)
        dup = [x for x in set(cant_texts) if cant_texts.count(x) > 1]
        if len(dup) > 0:
            for text in dup:
                warnings.append(text.replace('\n','')+"のエラーメッセージが別々のinclude内で2回以上使用されています")
    return [errors,warnings]

def check_others(driver):
    errors = []
    warnings = []
    try:
        url = driver.find_element(By.XPATH, "//a[contains(@title,'app/models') and (contains(@title,'item.rb') or contains(@title,'product.rb'))]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
    except:
        pass
    else:
        errors.append("商品モデルが作成されています\m商品モデルを削除しましょう。\nユーザー管理機能では商品モデルは不要で、現時点で実装すると他機能のブランチにおいて差分を作れなくなってしまうためです。")
    return [errors,warnings]