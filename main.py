###########################################################
#レビュー依頼をGUIアプリ上で自動チェックするツールです
###########################################################
from lib.output_to_gui import *
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkFont
import threading
import re
import pyperclip

def check_url(pull_url,output,entry):
    if re.match(r'\Ahttps://github.com/.+/pull/\d{1,2}\Z', pull_url):
        return True
    else:
        output.insert('end','URLに誤りがあります','error')
        entry.delete(0,"end")
        return False

def db_check_start():
    button1.configure(state="disable")
    output1.delete(1.0,'end')
    pull_url = entry1.get()
    if pull_url == "":
        pull_url = pyperclip.paste()
        entry1.insert('end',pull_url)
    pull_url = pull_url.replace('/files','')
    if check_url(pull_url,output1,entry1): db.output(pull_url,output1)
    button1.configure(state="normal")
    entry1.delete(0,'end')

def user_check_start():
    button2.configure(state="disable")
    output2.delete(1.0,'end')
    pull_url = entry2.get()
    if pull_url == "":
        pull_url = pyperclip.paste()
        entry2.insert('end',pull_url)
    pull_url = pull_url.replace('/files','')
    if check_url(pull_url,output2,entry2): user.output(pull_url,output2)
    button2.configure(state="normal")
    entry2.delete(0,'end')

def new_item_check_start():
    button3.configure(state="disable")
    output3.delete(1.0,'end')
    pull_url = entry3.get()
    if pull_url == "":
        pull_url = pyperclip.paste()
        entry3.insert('end',pull_url)
    pull_url = pull_url.replace('/files','')
    if check_url(pull_url,output3,entry3): new_item.output(pull_url,output3)
    button3.configure(state="normal")
    entry3.delete(0,'end')

def index_item_check_start():
    button4.configure(state="disable")
    output4.delete(1.0,'end')
    pull_url = entry4.get()
    if pull_url == "":
        pull_url = pyperclip.paste()
        entry4.insert('end',pull_url)
    pull_url = pull_url.replace('/files','')
    if check_url(pull_url,output4,entry4): index_item.output(pull_url,output4)
    button4.configure(state="normal")
    entry4.delete(0,'end')

def show_item_check_start():
    button5.configure(state="disable")
    output5.delete(1.0,'end')
    pull_url = entry5.get()
    if pull_url == "":
        pull_url = pyperclip.paste()
        entry5.insert('end',pull_url)
    pull_url = pull_url.replace('/files','')
    if check_url(pull_url,output5,entry5): show_item.output(pull_url,output5)
    button5.configure(state="normal")
    entry5.delete(0,'end')

def edit_item_check_start():
    button6.configure(state="disable")
    output6.delete(1.0,'end')
    pull_url = entry6.get()
    if pull_url == "":
        pull_url = pyperclip.paste()
        entry6.insert('end',pull_url)
    pull_url = pull_url.replace('/files','')
    if check_url(pull_url,output6,entry6): edit_item.output(pull_url,output6)
    button6.configure(state="normal")
    entry6.delete(0,'end')

def destroy_item_check_start():
    button7.configure(state="disable")
    output7.delete(1.0,'end')
    pull_url = entry7.get()
    if pull_url == "":
        pull_url = pyperclip.paste()
        entry7.insert('end',pull_url)
    pull_url = pull_url.replace('/files','')
    if check_url(pull_url,output7,entry7): destroy_item.output(pull_url,output7)
    button7.configure(state="normal")
    entry7.delete(0,'end')

def purchase_item_check_start():
    button8.configure(state="disable")
    output8.delete(1.0,'end')
    pull_url = entry8.get()
    if pull_url == "":
        pull_url = pyperclip.paste()
        entry8.insert('end',pull_url)
    pull_url = pull_url.replace('/files','')
    if check_url(pull_url,output8,entry8): purchase_item.output(pull_url,output8)
    button8.configure(state="normal")
    entry8.delete(0,'end')

def issue1_3_check_start():
    button9.configure(state="disable")
    output9.delete(1.0,'end')
    pull_url = entry9.get()
    if pull_url == "":
        pull_url = pyperclip.paste()
        entry9.insert('end',pull_url)
    pull_url = pull_url.replace('/files','')
    if check_url(pull_url,output1,entry9): issue1_3.output(pull_url,output9)
    button9.configure(state="normal")
    entry9.delete(0,'end')

def issue4_6_check_start():
    button10.configure(state="disable")
    output10.delete(1.0,'end')
    pull_url = entry10.get()
    if pull_url == "":
        pull_url = pyperclip.paste()
        entry10.insert('end',pull_url)
    pull_url = pull_url.replace('/files','')
    if check_url(pull_url,output1,entry10): issue4_6.output(pull_url,output10)
    button10.configure(state="normal")
    entry10.delete(0,'end')

def callback(target):
    th = threading.Thread(target=eval(target+"_check_start"))
    th.start()
    
def entry_focus(event):
    entry = root.nametowidget(nb.select()+".!frame.entry")
    entry.focus_set()

def press_enter(event):
    root.nametowidget(str(event.widget)+"-submit").invoke()

def press_escape(event):
    event.widget.delete(0,"end")

def set_tag_config(output):
    output.tag_config('info', foreground="black",font=tkFont.Font(weight="bold"))
    output.tag_config('ok', foreground="green",font=tkFont.Font(weight="bold"))
    output.tag_config('error', foreground="red")
    output.tag_config('warning', foreground="orange")

def set_entry_bind(entry):
    entry.bind("<KeyPress-Return>",press_enter)
    entry.bind("<Escape>",press_escape,"+")

# rootフレームの設定
root = tk.Tk()
root.title("レビュー自動チェックアプリ")
root.geometry("500x500")

tab_style = ttk.Style()
tab_style.theme_use("clam")
tab_style.map(
    "example.TNotebook.Tab",
    foreground=[
        ('active', 'red'),
        ('disabled', 'red'),
        ('selected', 'red'),
    ]
)

# ノートブック
nb = ttk.Notebook(width=500, height=300,style="example.TNotebook")

# タブの作成
tab1 = tk.Frame(nb, name="frame1")
tab2 = tk.Frame(nb, name="frame2")
tab3 = tk.Frame(nb, name="frame3")
tab4 = tk.Frame(nb, name="frame4")
tab5 = tk.Frame(nb, name="frame5")
tab6 = tk.Frame(nb, name="frame6")
tab7 = tk.Frame(nb, name="frame7")
tab8 = tk.Frame(nb, name="frame8")
tab9 = tk.Frame(nb, name="frame9")
tab10 = tk.Frame(nb, name="frame10")
nb.add(tab1, text='DB', padding=2)
nb.add(tab2, text='ユーザー', padding=2)
nb.add(tab3, text='出品', padding=2)
nb.add(tab4, text='一覧', padding=2)
nb.add(tab5, text='詳細', padding=2)
nb.add(tab6, text='編集', padding=2)
nb.add(tab7, text='削除', padding=2)
nb.add(tab8, text='購入', padding=2)
nb.add(tab9, text='発展1-3', padding=2)
nb.add(tab10, text='発展4-6', padding=2)
nb.enable_traversal()
nb.bind("<<NotebookTabChanged>>", entry_focus)
nb.pack(expand=1, fill='both')

## DBタブ
### 入力欄の設定
frame1_1 = tk.Frame(tab1,pady=10)
frame1_1.pack(anchor="w")
label1_1 = tk.Label(frame1_1,font=("",14),text="プルリクエストURL")
label1_1.pack(side="left",padx=(13,0))
entry1 = tk.Entry(frame1_1,font=("",14),width=27,name="entry")
set_entry_bind(entry1)
entry1.pack(side="left")
button1 = tk.Button(frame1_1,text="開始",font=("",14),width=5,bg="gray",command=lambda:callback("db"),name="entry-submit")
button1.pack(side="left")
### 出力欄の設定
frame1_2 = tk.Frame(tab1)
frame1_2.pack(pady=(0,10))
label1_2 = tk.Label(frame1_2,font=("",14),text="DB 自動チェック結果")
label1_2.pack()
output1 = tk.Text(frame1_2,font=("",14),highlightbackground="black",highlightthickness=1)
set_tag_config(output1)
output1.pack(ipady=100,padx=10)

## ユーザータブ
### 入力欄の設定
frame2_1 = tk.Frame(tab2,pady=10)
frame2_1.pack(anchor="w")
label2_1 = tk.Label(frame2_1,font=("",14),text="プルリクエストURL")
label2_1.pack(side="left",padx=(13,0))
entry2 = tk.Entry(frame2_1,font=("",14),width=27,name="entry")
set_entry_bind(entry2)
entry2.pack(side="left")
button2 = tk.Button(frame2_1,text="開始",font=("",14),width=5,bg="gray",command=lambda:callback("user"),name="entry-submit")
button2.pack(side="left")
### 出力欄の設定
frame2_2 = tk.Frame(tab2)
frame2_2.pack(pady=(0,10))
label2_2 = tk.Label(frame2_2,font=("",14),text="ユーザー 自動チェック結果")
label2_2.pack()
output2 = tk.Text(frame2_2,font=("",14),highlightbackground="black",highlightthickness=1)
set_tag_config(output2)
output2.pack(ipady=100,padx=10)

## 出品タブ
### 入力欄の設定
frame3_1 = tk.Frame(tab3,pady=10)
frame3_1.pack(anchor="w")
label3_1 = tk.Label(frame3_1,font=("",14),text="プルリクエストURL")
label3_1.pack(side="left",padx=(13,0))
entry3 = tk.Entry(frame3_1,font=("",14),width=27,name="entry")
set_entry_bind(entry3)
entry3.pack(side="left")
button3 = tk.Button(frame3_1,text="開始",font=("",14),width=5,bg="gray",command=lambda:callback("new_item"),name="entry-submit")
button3.pack(side="left")
### 出力欄の設定
frame3_2 = tk.Frame(tab3)
frame3_2.pack(pady=(0,10))
label3_2 = tk.Label(frame3_2,font=("",14),text="出品 自動チェック結果")
label3_2.pack()
output3 = tk.Text(frame3_2,font=("",14),highlightbackground="black",highlightthickness=1)
set_tag_config(output3)
output3.pack(ipady=100,padx=10)

## 一覧タブ
### 入力欄の設定
frame4_1 = tk.Frame(tab4,pady=10)
frame4_1.pack(anchor="w")
label4_1 = tk.Label(frame4_1,font=("",14),text="プルリクエストURL")
label4_1.pack(side="left",padx=(13,0))
entry4 = tk.Entry(frame4_1,font=("",14),width=27,name="entry")
set_entry_bind(entry4)
entry4.pack(side="left")
button4 = tk.Button(frame4_1,text="開始",font=("",14),width=5,bg="gray",command=lambda:callback("index_item"),name="entry-submit")
button4.pack(side="left")
### 出力欄の設定
frame4_2 = tk.Frame(tab4)
frame4_2.pack(pady=(0,10))
label4_2 = tk.Label(frame4_2,font=("",14),text="一覧 自動チェック結果")
label4_2.pack()
output4 = tk.Text(frame4_2,font=("",14),highlightbackground="black",highlightthickness=1)
set_tag_config(output4)
output4.pack(ipady=100,padx=10)

## 詳細タブ
### 入力欄の設定
frame5_1 = tk.Frame(tab5,pady=10)
frame5_1.pack(anchor="w")
label5_1 = tk.Label(frame5_1,font=("",14),text="プルリクエストURL")
label5_1.pack(side="left",padx=(13,0))
entry5 = tk.Entry(frame5_1,font=("",14),width=27,name="entry")
set_entry_bind(entry5)
entry5.pack(side="left")
button5 = tk.Button(frame5_1,text="開始",font=("",14),width=5,bg="gray",command=lambda:callback("show_item"),name="entry-submit")
button5.pack(side="left")
### 出力欄の設定
frame5_2 = tk.Frame(tab5)
frame5_2.pack(pady=(0,10))
label5_2 = tk.Label(frame5_2,font=("",14),text="詳細 自動チェック結果")
label5_2.pack()
output5 = tk.Text(frame5_2,font=("",14),highlightbackground="black",highlightthickness=1)
set_tag_config(output5)
output5.pack(ipady=100,padx=10)

## 編集タブ
### 入力欄の設定
frame6_1 = tk.Frame(tab6,pady=10)
frame6_1.pack(anchor="w")
label6_1 = tk.Label(frame6_1,font=("",14),text="プルリクエストURL")
label6_1.pack(side="left",padx=(13,0))
entry6 = tk.Entry(frame6_1,font=("",14),width=27,name="entry")
set_entry_bind(entry6)
entry6.pack(side="left")
button6 = tk.Button(frame6_1,text="開始",font=("",14),width=5,bg="gray",command=lambda:callback("edit_item"),name="entry-submit")
button6.pack(side="left")
### 出力欄の設定
frame6_2 = tk.Frame(tab6)
frame6_2.pack(pady=(0,10))
label6_2 = tk.Label(frame6_2,font=("",14),text="編集 自動チェック結果")
label6_2.pack()
output6 = tk.Text(frame6_2,font=("",14),highlightbackground="black",highlightthickness=1)
set_tag_config(output6)
output6.pack(ipady=100,padx=10)

## 削除タブ
### 入力欄の設定
frame7_1 = tk.Frame(tab7,pady=10)
frame7_1.pack(anchor="w")
label7_1 = tk.Label(frame7_1,font=("",14),text="プルリクエストURL")
label7_1.pack(side="left",padx=(13,0))
entry7 = tk.Entry(frame7_1,font=("",14),width=27,name="entry")
set_entry_bind(entry7)
entry7.pack(side="left")
button7 = tk.Button(frame7_1,text="開始",font=("",14),width=5,bg="gray",command=lambda:callback("destroy_item"),name="entry-submit")
button7.pack(side="left")
### 出力欄の設定
frame7_2 = tk.Frame(tab7)
frame7_2.pack(pady=(0,10))
label7_2 = tk.Label(frame7_2,font=("",14),text="削除 自動チェック結果")
label7_2.pack()
output7 = tk.Text(frame7_2,font=("",14),highlightbackground="black",highlightthickness=1)
set_tag_config(output7)
output7.pack(ipady=100,padx=10)

## 購入タブ
### 入力欄の設定
frame8_1 = tk.Frame(tab8,pady=10)
frame8_1.pack(anchor="w")
label8_1 = tk.Label(frame8_1,font=("",14),text="プルリクエストURL")
label8_1.pack(side="left",padx=(13,0))
entry8 = tk.Entry(frame8_1,font=("",14),width=27,name="entry")
set_entry_bind(entry8)
entry8.pack(side="left")
button8 = tk.Button(frame8_1,text="開始",font=("",14),width=5,bg="gray",command=lambda:callback("purchase_item"),name="entry-submit")
button8.pack(side="left")
### 出力欄の設定
frame8_2 = tk.Frame(tab8)
frame8_2.pack(pady=(0,10))
label8_2 = tk.Label(frame8_2,font=("",14),text="購入 自動チェック結果")
label8_2.pack()
output8 = tk.Text(frame8_2,font=("",14),highlightbackground="black",highlightthickness=1)
set_tag_config(output8)
output8.pack(ipady=100,padx=10)

## 発展1-3タブ
### 入力欄の設定
frame9_1 = tk.Frame(tab9,pady=10)
frame9_1.pack(anchor="w")
label9_1 = tk.Label(frame9_1,font=("",14),text="プルリクエストURL")
label9_1.pack(side="left",padx=(13,0))
entry9 = tk.Entry(frame9_1,font=("",14),width=27,name="entry")
set_entry_bind(entry9)
entry9.pack(side="left")
button9 = tk.Button(frame9_1,text="開始",font=("",14),width=5,bg="gray",command=lambda:callback("issue1_3"),name="entry-submit")
button9.pack(side="left")
### 出力欄の設定
frame9_2 = tk.Frame(tab9)
frame9_2.pack(pady=(0,10))
label9_2 = tk.Label(frame9_2,font=("",14),text="発展1-3 自動チェック結果")
label9_2.pack()
output9 = tk.Text(frame9_2,font=("",14),highlightbackground="black",highlightthickness=1)
set_tag_config(output9)
output9.pack(ipady=100,padx=10)

## 発展4-6タブ
### 入力欄の設定
frame10_1 = tk.Frame(tab10,pady=10)
frame10_1.pack(anchor="w")
label10_1 = tk.Label(frame10_1,font=("",14),text="プルリクエストURL")
label10_1.pack(side="left",padx=(13,0))
entry10 = tk.Entry(frame10_1,font=("",14),width=27,name="entry")
set_entry_bind(entry10)
entry10.pack(side="left")
button10 = tk.Button(frame10_1,text="開始",font=("",14),width=5,bg="gray",command=lambda:callback("issue4_6"),name="entry-submit")
button10.pack(side="left")
### 出力欄の設定
frame10_2 = tk.Frame(tab10)
frame10_2.pack(pady=(0,10))
label10_2 = tk.Label(frame10_2,font=("",14),text="発展4-6 自動チェック結果")
label10_2.pack()
output10 = tk.Text(frame10_2,font=("",14),highlightbackground="black",highlightthickness=1)
set_tag_config(output10)
output10.pack(ipady=100,padx=10)

# メインループ
root.mainloop()