from selenium.webdriver.common.by import By
from lib.modules.common import get_file_text

def check_c(driver):
    errors = []
    warnings = []
    try:
        url = driver.find_element(By.XPATH, "//a[contains(@title,'app/controllers/calendars_controller.rb')]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
        file_text = get_file_text(url,driver)
    except:
        errors.append("ファイルが見つかりませんでした\mコントローラーのファイル名や位置を変更していないか確認しましょう。")
    else:
        if "binding.pry" in file_text: 
            errors.append("binding.pryが見つかりました\mデバッグ用のbinding.pryは削除しましょう。")
        if not file_text.count("get_week") == 2: 
            errors.append("コンフリクトが発生している可能性があります\mプルリクエストにおいてコンフリクトが発生していないか、またissue1-3の内容を差し戻していないかを確認しましょう。")
        file_text = file_text.replace("\n","")
        wday_num_flg = False
        if_flg = False
        days_flg = False
        if not "defplan_paramsparams.require(:plan).permit(:date,:plan)end" in file_text: 
            errors.append("plan_paramsメソッドが正しく修正されていない可能性があります(issue4)\m改めてplanの保存ができるかを確認し、もし保存ができない場合はplan_paramsメソッドを見直しましょう。")
        if not ("wday_num=@todays_date.wday+x" in file_text or "wday_num=Date.today.wday+x" in file_text or "wday_num=(@todays_date+x).wday" in file_text or "wday_num=(Date.today+x).wday" in file_text or "wday_num=@todays_date.wdaywday_num+=x" in file_text or "wday_num=Date.today.wdaywday_num+=x" in file_text) and not "wdays[(@todays_date+x).wday]" in file_text: 
            wday_num_flg = True
        if not ("ifwday_num>=7wday_num=wday_num-7end" in file_text or "ifwday_num>=7wday_num-=7end" in file_text): 
            if not "wdays[(@todays_date+x).wday]" in file_text:
                if_flg = True
        if not ("wdays[wday_num]" in file_text or "wdays[(@todays_date+x).wday]" in file_text): days_flg = True
        message = ''
        if wday_num_flg or if_flg or days_flg:
            if wday_num_flg: message+= "wday_numの定義式,"
            if if_flg: message+= "wday_numが7以上にならないようにする条件式,"
            if days_flg: message+= "daysの:wdayに対する値"
            message += "に誤りがある可能性があります(issue6)"
            errors.append(message+"\m改めてブラウザで曜日表示が期待通り行われているか確認し、行われていない場合はコントローラのwday_num関連の記述を見直しましょう。")
        if "=>" in file_text: 
            errors.append("変数daysの定義式にハッシュロケットが存在しています\m変数daysの定義式においてissue1で解消したハッシュロケットが元に戻っておりますので、改めてシンボルに修正しましょう。")
    return [errors,warnings]

def check_v(driver):
    errors = []
    warnings = []
    try:
        url = driver.find_element(By.XPATH, "//a[contains(@title,'app/views/calendars/index.html.erb')]/../../following-sibling::div/div/details/details-menu/a").get_attribute("href")
        file_text,raw_text = get_file_text(url,driver,True)
    except:
        errors.append("ファイルが見つかりませんでした\mビューファイルのファイル名や位置を変更していないか確認しましょう。")
    else:
        file_text = file_text.replace("\n","")
        if not "<%=day[:month]%>/<%=day[:date]%><%=day[:wday]%>" in file_text:
            if "<%=day[:month]%>/<%=day[:date]%>/<%=day[:wday]%>" in file_text:
                warnings.append("日付と曜日の間に/が見つかりました\m日付と曜日の間の/は削除しておいた方が一般的な表記になりユーザー目線分かりやすくなります。")
            else:
                errors.append("日付の表示、または曜日の表示が期待通りに実装されていません(issue5,6)\m改めてブラウザで日付及び曜日が期待通り表示されているかを確認し、表示されていない場合は表示箇所の記述を見直しましょう。")
        if file_text.count("<divclass='calendar'>") > 1: 
            errors.append("calendarクラスのdivタグが二つ以上見つかりました\mビューファイルにおいて記述の重複がないか確認し、不要な記述があれば削除しましょう。")
        if "<div>" in file_text: 
            errors.append("コンフリクトが発生している可能性があります\mプルリクエストにおいてコンフリクトが発生していないか、またissue1-3の内容を差し戻していないかを確認しましょう。")
    return [errors,warnings]