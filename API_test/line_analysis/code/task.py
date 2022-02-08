from flask import Flask, jsonify, request
import string
import random
import os

from ..lib import create_action_table
from ..lib import love_scores

app = Flask(__name__, static_folder='static')
app.config['JSON_AS_ASCII'] = False

@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        data = request.form
        data = data.to_dict(flat=False)
        data = data['text1'][0]
        data = data.replace(', ', '')
        test=GetRandomStr(5)
        f = open(test, 'w', encoding='UTF-8')
        f.write(data)
        f.close()
        try:
            # 引数7は、分析する期間（day)
            line_df=create_action_table.make_dataframe(test, 7)
            os.remove(test)
            #TODO:一時ファイルを消す処理が入る
            action_df = create_action_table.make_cluster_df(line_df)
            dict = action_df.to_json(orient='records', force_ascii=False)
            return dict
        except:
            os.remove(test)
            return 'not analytics'
    else:
        a = 'not analytics'
        return a

def GetRandomStr(num):
    # 英数字をすべて取得
    dat = string.digits + string.ascii_lowercase + string.ascii_uppercase
    # 英数字からランダムに取得
    return ''.join([random.choice(dat) for i in range(num)])
