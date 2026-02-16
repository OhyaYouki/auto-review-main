###########################################################
#設定用ファイルです
###########################################################
from datetime import datetime
from slack_sdk import WebClient
from lib.modules.common import driver_init, check_function
from lib.output_to_slack import *
import time
import sys
import re
import csv
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append("../lib")

###########################################################
# 特別対応の受講生名
###########################################################
ALERT_LIST = [
]
###########################################################
# 設定
###########################################################
# 自動チェックの間隔(秒)
# INTERVAL = 10
INTERVAL = 30

# slackトークン
SLACK_ACCESS_TOKEN = 'xoxb-81666833746-4624845687671-q1QzkopazUpAOjDzpVakJaCU'
CLIENT = WebClient(SLACK_ACCESS_TOKEN)
