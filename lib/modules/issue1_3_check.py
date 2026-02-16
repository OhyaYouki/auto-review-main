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
        if not 'days={month:(@todays_date+x).month,date:(@todays_date+x).day,plans:today_plans}' in file_text: 
            errors.append("ハッシュロケットのシンボル化が正しく行われていない可能性があります(issue1)\missue1について、改めてハッシュロケットをシンボルに正しく置き換えられているか確認しましょう。")
        if file_text.count("get_week") != 2: errors.append("命名規則に沿ったメソッド名の修正が正しく行われていない可能性があります(issue2)\m改めて命名規則に沿ってメソッド名を修正できているか確認しましょう。\nメソッドの定義及びメソッドの呼び出しで合計二箇所修正が必要です。")
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
        error_flg = False
        if file_text.count("<div") != 3: 
            error_flg = True
        if file_text.count("</div") != 3: 
            if error_flg == True:
                errors.append("不要なタグの削除が正しく行われていません(issue3)\mビューファイルにおいて削除しても問題ないタグが残っていないか確認しましょう。")
            else:
                errors.append("divタグの開きと閉じの数があっていません(issue3)\mビューファイルにおいてdivタグの開きと閉じの数が合っているかを確認しましょう。")
            error_flg = True
        elif error_flg:
            errors.append("divタグの開きと閉じの数があっていません(issue3)\mビューファイルにおいてdivタグの開きと閉じの数が合っているかを確認しましょう。")
        file_text = file_text.replace("\n","")
        if not ("<%=form_withmodel:@plan,url:calendars_path,class:'form'do|f|%><%=f.label:日付を選択,class:'label'%><%=f.date_field:date,class:'date-select'%><%=f.label:予定を入力,class:'label'%><%=f.text_field:plan,class:'text-input'%><%=f.submit'保存'%><%end%>" in file_text and "<divclass='calendar'><%@week_days.eachdo|day|%><divclass='item'><divclass='date'><%day[:month]%>/<%day[:date]%></div><ulclass='content'><%ifday[:plans].length!=0%><%day[:plans].eachdo|plan|%><liclass='plan-list'>・<%=plan%></li><%end%><%end%></ul></div><%end%></div>" in file_text):
            errors.append("不要な変更が加えられている可能性があります(issue3)\mビューファイルにおいて不要なタグの削除以外の編集を加えていないか確認しましょう。")
        elif not error_flg:
            if not file_text == "<%=form_withmodel:@plan,url:calendars_path,class:'form'do|f|%><%=f.label:日付を選択,class:'label'%><%=f.date_field:date,class:'date-select'%><%=f.label:予定を入力,class:'label'%><%=f.text_field:plan,class:'text-input'%><%=f.submit'保存'%><%end%><divclass='calendar'><%@week_days.eachdo|day|%><divclass='item'><divclass='date'><%day[:month]%>/<%day[:date]%></div><ulclass='content'><%ifday[:plans].length!=0%><%day[:plans].eachdo|plan|%><liclass='plan-list'>・<%=plan%></li><%end%><%end%></ul></div><%end%></div>":
                errors.append("不要な変更が加えられている可能性があります(issue3)\mビューファイルにおいて不要なタグの削除以外の編集を加えていないか確認しましょう。")
        if file_text.count("<divclass='calendar'>") > 1: 
            errors.append("calendarクラスのdivタグが二つ以上見つかりました\mビューファイルにおいて記述の重複がないか確認し、不要な記述があれば削除しましょう。")
    return [errors,warnings]