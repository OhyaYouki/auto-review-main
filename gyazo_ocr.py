###########################################################
#gyazoの文字起こしを行うツールです
#「GyazoURL」にgyazoのURLを入力して開始ボタンを押すことで、gyazo内の文字が出力されます
#「#文」のチェックをつけると#を含んだ文も出力されます（コメントアウト記述が不要な場合は外しておいた方が綺麗です）
###########################################################
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkFont
import threading
import pyperclip
import os
import pyocr
from PIL import Image
import requests
import cv2
import re

#プルダウンの編集
GPT_QUESTION = {'なし':'',\
                'ruby質問文':'上記rubyのエラーの解決方法を教えてください。\n考えられる原因を箇条書きで挙げた後、それぞれの原因の確認方法を説明してください。',\
                'rails質問文':'上記railsのエラーの解決方法を教えてください。\n考えられる原因を箇条書きで挙げた後、それぞれの原因の確認方法を説明してください。',\
                'ターミナル質問文':'上記ターミナルのエラーの解決方法を教えてください。\n考えられる原因を箇条書きで挙げた後、それぞれの原因の確認方法を説明してください。',\
                '誤字脱字評価文':'上記文章に誤字脱字がないかを確認してください。\n考えられる原因を箇条書きで挙げた後、それぞれの原因の確認方法を説明してください。'}

#文字起こしを行うメソッド
def gyazo_ocr(gyazo_url):
    #画像の読み込み
    image = os.path.dirname(__file__) + "/gyazo.png"
    with open(image, "wb") as f:
        f.write(requests.get(gyazo_url).content)
    tool = pyocr.get_available_tools()[0]
    img = cv2.imread(image)
    
    #画像処理
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(image,img)
    
    #文字起こし
    res = tool.image_to_string(
        Image.open(image)
        ,lang="eng")
    os.remove(image)
    
    #出力結果を整える
    ans = ''
    res = res.replace("\n\n","\n")
    raws = res.split('\n')
    for raw in raws:
        ans += re.sub(r'^\d+','',raw)+'\n'
    ans = ans.replace("\n\n","\n")
    
    #GUIに出力
    output1.insert('end',ans,'info')

#URLがgyazoのものか確認するメソッド
def check_url(gyazo_url):
    if "gyazo.com" in gyazo_url:
        return True
    else:
        return False
    
#開始ボタンを押した時のメソッド
def gyazo_check():
    try:
        button1.configure(state="disable")
        output1.delete(1.0,'end')
        gyazo_url = entry1.get()
        if gyazo_url == "":
            gyazo_url = pyperclip.paste()
            entry1.insert('end',gyazo_url)
        if not ".png" in gyazo_url: gyazo_url += ".png"
        if check_url(gyazo_url): 
            gyazo_ocr(gyazo_url)
            output1.insert('end','\n\n'+GPT_QUESTION[combo.get()])
        else:
            output1.insert('end','URLに誤りがあります','error')
    except Exception as e:
        output1.insert('end','処理中にエラーが発生しました。URLを確認してください','error')
        print(str(type(e)))
        print(str(e.args))
        print(e.message)
    button1.configure(state="normal")
    entry1.delete(0,'end')

###これ以降はGUI用の記述###

#エンターキーで開始ボタンが反応するためのメソッド1
def press_enter(event):
    root.nametowidget(str(event.widget)+"-submit").invoke()

#エンターキーで開始ボタンが反応するためのメソッド2
def set_entry_bind(entry):
    entry.bind("<KeyPress-Return>",press_enter)
    
#文字のスタイルを設定するメソッド
def set_tag_config(output):
    output.tag_config('title', foreground="black",font=tkFont.Font(weight="bold",size=16))
    output.tag_config('info', foreground="black",font=tkFont.Font(weight="bold"))
    output.tag_config('error', foreground="red")

def callback(target):
    th = threading.Thread(target=eval(target+"_check"))
    th.start()
    
def combo_selected(event):
    combo.selection_clear()

#rootフレームの設定
root = tk.Tk()
root.title("gyazo文字起こしアプリ")
root.geometry("500x400")

#入力欄の設定
frame1 = tk.Frame(root)
frame1.pack(pady=(10,0))
label1 = tk.Label(frame1,font=("",14,'bold'),text="GyazoURL")
label1.pack(side="left",padx=(13,0),anchor='center')
entry1 = tk.Entry(frame1,font=("",14),width=30,bd=1,relief="solid",name="entry")
set_entry_bind(entry1)
entry1.pack(side="left",anchor='center')
button1 = tk.Button(frame1,text="開始",font=("",14),padx=10,bg="gray",command=lambda:callback("gyazo"),name="entry-submit")
button1.pack(side="left",padx=(10,27),anchor='center')

#プルダウンの設定
frame2 = tk.Frame(root)
frame2.pack(pady=(5,20))
module = list(GPT_QUESTION.keys())
combo = ttk.Combobox(frame2,width=18, state="readonly", values=module)
combo.set('なし')
combo.bind('<<ComboboxSelected>>', combo_selected)
combo.pack(side="left")

#出力欄の設定
frame3 = tk.Frame(root)
frame3.pack()
label2 = tk.Label(frame3,font=("",14,'bold'),text="文字起こし結果")
label2.pack()
output1 = tk.Text(frame3,font=("",14),width=500,height=1000,highlightbackground="black",highlightthickness=1)
set_tag_config(output1)
output1.pack(ipady=100,padx=10,pady=(0,10))

#起動時の説明文
output1.insert('end','◎使い方\n','title')
output1.insert('end','①上のGyazoURL入力欄にgyazoのURLを入力して開始をクリック\n','info')
output1.insert('end','*URLをコピーしていれば入力欄が空でも開始できます\n\n')
output1.insert('end','②この欄に文字起こし結果が表示されるので、対応やChatGPTに用いる\n','info')
output1.insert('end','*文字起こし結果は編集可能なので、')
output1.insert('end','必要に応じて個人情報を削除してください\n','error')
output1.insert('end','*必要に応じてウィンドウサイズを調整してください\n\n\n')
output1.insert('end','◎オプション\n','title')
output1.insert('end','GyazoURL入力欄下のプルダウンを変更することで、文字起こし結果末尾に\nChatGPT用質問文が追加されます\n\n')

root.mainloop()