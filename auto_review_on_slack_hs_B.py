###########################################################
# 高校生教育_コードレビュー_月水クラスチャンネルの投稿を自動レビューします
###########################################################
from settings import *
from datetime import datetime,timedelta
import traceback

# チェックするslackチャンネルのID
CHECK_CHANNEL_ID = 'C083L065YPQ' #高校生教育_コードレビュー_月水クラス

# チェック結果の送信先slackチャンネルのID
SEND_CHANNEL_ID = 'C083L065YPQ' #高校生教育_コードレビュー_月水クラス

# 何日前の22:00の投稿からチェックするか
START_DAY = 1

# チェック開始時間
START_TIME =  datetime(int((datetime.now() - timedelta(START_DAY)).year) \
            ,int((datetime.now() - timedelta(START_DAY)).month) \
            ,int((datetime.now() - timedelta(START_DAY)).day) \
            ,22 \
            ,0 \
            ).strftime('%s')

def __oldest_to_strftime(oldest):
    text = datetime.fromtimestamp(float(oldest)).strftime('%m月%d日%H:%M')
    if text[0] == "0": text = text[1:]
    return text


def review_check(oldest):
    while True:
        try:
            print(__oldest_to_strftime(oldest) + "以降のレビュー依頼をチェックします")
            reviews = CLIENT.conversations_history(channel=CHECK_CHANNEL_ID, oldest=oldest)['messages']
            if len(reviews) > 0:
                reviews.reverse()
                for review in reviews:
                    oldest = review['ts']
                    print("チェック開始:" + __oldest_to_strftime(oldest))
                    try: 
                        replies = CLIENT.conversations_replies(channel=CHECK_CHANNEL_ID, ts=oldest)['messages']
                    except:
                        continue
                    reactions_check = review.get('reactions') and review['reactions'][0].get('name') == '重複'
                    attachments_check = 'attachments' not in review
                    replies_check = len(replies) > 1
                    if reactions_check or attachments_check or replies_check:
                        continue
                    fallback_lines = review['attachments'][0].get('fallback', '').split('\n')
                    pull_url = fallback_lines[-1][20:-1].split('#')[0].split('commits')[0].split('/files')[0]
                    if pull_url.endswith("/"):
                        pull_url = pull_url[:-1]
                    print(pull_url)
                    if re.match(r'\Ahttps://github.com/.+/pull/\d{1,2}\Z', pull_url):
                        error = ''
                        warning = ''
                        driver = driver_init(pull_url)
                        function = check_function(driver)
                        options = {
                            'DB': db,
                            'ユーザー': user,
                            '出品': new_item,
                            '一覧': index_item,
                            '詳細': show_item,
                            '編集': edit_item,
                            '削除': destroy_item,
                            '購入': purchase_item,
                            'Issue1-3': issue1_3,
                            'Issue4-6': issue4_6
                        }

                        task = options.get(function)

                        if task is not None:
                            error, warning = task.output(driver)
                            driver.quit()
                        else:
                            error,warning = '機能を特定できませんでした。\n手動で確認をお願いします。\n\n','\n\n'
                            driver.quit()
                        if error.count('\n') == 2:
                            if warning.count('\n') == 2:
                                error += '`LGTM`です。\nコンフリクトが起きていないかの確認だけお願いします。'
                            else:
                                error += '`LGTM`です。\n以下の要確認項目とコンフリクトが起きていないかの確認だけお願いします。'
                        if SEND_CHANNEL_ID == CHECK_CHANNEL_ID:
                            CLIENT.chat_postMessage(channel=SEND_CHANNEL_ID, thread_ts=oldest, text=error, icon_emoji=':robot_face:', username='自動レビューbot')
                            if warning.count('\n') != 2:
                                time.sleep(1)
                                CLIENT.chat_postMessage(channel=SEND_CHANNEL_ID, thread_ts=oldest, text=warning, icon_emoji=':robot_face:', username='自動レビューbot')
                        else:
                            CLIENT.chat_postMessage(channel=SEND_CHANNEL_ID, text=error, icon_emoji=':robot_face:', username='自動レビューbot')
                            time.sleep(1)
                            CLIENT.chat_postMessage(channel=SEND_CHANNEL_ID, text=warning, icon_emoji=':robot_face:', username='自動レビューbot')
        except:
            print(sys.exc_info())
            try:
                # CLIENT.chat_postMessage(channel=SEND_CHANNEL_ID, thread_ts=oldest, text="自動チェック中にエラーが発生しました", icon_emoji=':robot_face:', username='自動レビューbot')
                error_details = f"自動チェック中にエラーが発生しました\n```\nエラー種別: {type(sys.exc_info()[1]).__name__}\nエラー内容: {str(sys.exc_info()[1])}\nURL: {pull_url if 'pull_url' in locals() else 'URL取得前'}\n発生箇所: {traceback.format_exc().split('File')[-1].strip()}\n```"
                CLIENT.chat_postMessage(channel=SEND_CHANNEL_ID, thread_ts=oldest, text=error_details, icon_emoji=':robot_face:', username='自動レビューbot')
                driver.quit()
            except:
                continue
        time.sleep(INTERVAL)

review_check(START_TIME)