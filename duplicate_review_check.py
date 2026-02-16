###########################################################
#前日22時以降からプログラム実行時までの間に重複レビューがないかを確認するツールです
#スタンプがついていないレビュー依頼のみをチェックします
###########################################################
from settings import *
from datetime import datetime,timedelta

# チェックするslackチャンネルのID
CHECK_CHANNEL_ID = 'C02QGBZMXH9' #reviews14-22

# チェック結果の送信先slackチャンネルのID
SEND_CHANNEL_ID = 'C02QGBZMXH9' #reviews14-22

START_TIME =  datetime(int((datetime.now() - timedelta(1)).year) \
            ,int((datetime.now() - timedelta(1)).month) \
            ,int((datetime.now() - timedelta(1)).day) \
            ,22 \
            ,0 \
            ).strftime('%s')

def duplication_check(oldest):
    reviews = CLIENT.conversations_history(channel=CHECK_CHANNEL_ID, oldest=oldest)['messages']
    name_list = []
    dupli_name_list = []
    if len(reviews) > 0:
        reviews.reverse()
        for review in reviews:
            try:
                if 'attachments' in review and not "reactions" in review:
                    if 'レビュー依頼が来ましたよ！' in review['attachments'][0]['text']:
                        name = review['attachments'][0]['fallback'].split('\n')[0][4:].replace("\u3000","")
                        if name in name_list:
                            ts = review['ts']
                            dupli_name_list.append(name)
                            CLIENT.reactions_add(channel=CHECK_CHANNEL_ID,timestamp=ts,name='重複')
                        else:
                            name_list.append(name)
            except:
                pass
    if len(dupli_name_list) > 0:
        dupli_name_list = list(dict.fromkeys(dupli_name_list))
        dupli_name_list = list(map(lambda name: '*'+name+'*', dupli_name_list))
        message = '🚨以下の受講生のレビュー依頼が重複しています🚨\n' + '\n'.join(dupli_name_list)
    else:
        message = '重複はありませんでした'
    CLIENT.chat_postMessage(channel=SEND_CHANNEL_ID,text=message, icon_emoji=':robot_face:', username='レビュー重複チェックbot（杉山の手動実行）')

duplication_check(START_TIME)
