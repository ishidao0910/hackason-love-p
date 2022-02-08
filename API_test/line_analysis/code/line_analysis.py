# import mysql.connector
from flask import Flask, jsonify, request
import json
import requests
from pandas import json_normalize
import pandas
import re
import emoji
import statistics
import random
import string
import os
from datetime import datetime, timedelta
# ↓この辺整理します。
import matplotlib.pyplot as plt
import matplotlib


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
            a=make_dataframe(test)
            os.remove(test)
            #TODO:一時ファイルを消す処理が入る
            return a
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

# これで絵文字の削除ができる。
# 返り値で絵文字を省いたテキストを返す。
def extract_emoji(s):
    return ''.join(c for c in s if c in emoji.UNICODE_EMOJI['en'])

def extract_text(s):
    return ''.join(c for c in s if not c in emoji.UNICODE_EMOJI['en'])

def make_dataframe(input_text):
    #input_text ⇨ 
    """
    ラインの設定からテキストファイルを送ってもらい、それを整形
    して分析しやすいデータフレームにして返す。
    
    Parameters
    ---------------
    talk_text : text file
        LINE/TALK/MENU/SETTING/トーク履歴を送信　で取得したテキストファイルをInputで入手
        
    Returns
    ---------------
    line_df: pandas.core.frame.DataFrame
        言語処理に必要な特徴量をそれぞれもった整形済みのデータフレーム
    """

    # これらの辞書を使って、talksにこれらの単語が含まれていたら1をカウントする。
    # どんなに多く入っていてもmaxを1としてカウントしていく

    thanks_dict = ["ありがとう", "ありがと", "ありが", "あざまる", "あざま", "あざ", "ありがたし", "感謝", "あざす", "てんきゅ", "てんきゅん", "さんきゅ", "あり", "thanks", "thank you", "ありがつ", "助かる"]
    apology_dict = ["ごめん", "ごめんなさい", "ごめす", "申し訳ない", "申し訳", "ごめちょ", "すみません", "すまそ", "すまん", "すんません"]
    question_dict = ["?", "？", "なんで", "なぜ", "どうして", "どうやって", "どこで", "何を", "誰が"]
    love_dict = ["すき", "あいしてる", "らぶゆ", "好き", "愛してる", "love"]
    complement_dict = ["かっこいい","格好いい","格好良い","イケメン","かわいい","可愛い","綺麗","美しい","美人","美形", "素敵", "すてき", "ステキ"]
    # まずテキストファイルを読み込んでカラム名を変更する
    #一旦一時的にファイルを保存する？
    line_df = pandas.read_csv(input_text, sep='\n')
    line_df = line_df.rename(columns={line_df.columns[0]:'talks'})
    line_df = line_df[1:]
    # 正規表現でトークから日付を取得し新しいカラムとして結合する
    date_list = []
    date_pattern = '(\d+)/(\d+)/\d+\(.?\)'
    for talk in line_df['talks']:
        result = re.match(date_pattern, talk)
        if result:
            date_t = result.group()
            date_list.append(date_t)
        else:
            date_list.append(date_t)
            
    line_df['date'] = date_list

    # talksにおいて日付のカラムはもう必要ないので、そこがTrueのものをisin関数で消す
    flag = line_df['talks'].isin(line_df['date'])
    line_df = line_df[~flag]
    line_df.dropna(inplace=True)    

    # # talks内を、時間、話者、トーク内容で分ける(ここ結構ガバガバ)
    # # str.splitを使うと、データフレームの列を区切り文字で区切って新しいデータフレームを返す
    time_l = []
    user_l = []
    talk_l = []
    date_l = []
    count = 0
    for date, talk in zip(line_df['date'], line_df['talks']):
        # もし正規表現で時間が取れたらスプリットして3つに分ける
        if(re.match('(\d+):(\d+)', talk)):
            try:
                if(len(talk.split('\t')[0]) == 5):
                    date_l.append(date)
                    time_l.append(talk.split('\t')[0])
                    user_l.append(talk.split('\t')[1])
                    talk_l.append(talk.split('\t')[2])
                    count = count + 1
                else:
                    continue
            except:
                talk_l.append("メッセージの送信取り消し")
                count = count + 1
        else:
            talk_l[count-1] = talk_l[count-1] + talk
            
    # if(user_l != date_l):
    #     user_l.append(user1)
            
    line_df = pandas.DataFrame({"date" : date_l,
                            "time" : time_l,
                            "user" : user_l,
                            "talk" : talk_l})

    date_l = []
    for date in line_df['date']:
        date_l.append(date[:-3])
    line_df['date'] = date_l

    # datetime型で時間の経過を計算するために、日付と時間をくっつけとく
    line_df['time'] = line_df['date'].str.cat(line_df['time'], sep=' ')
    line_df.drop('date', axis=1, inplace=True)

    # datetime型に変換するところ。indexをリセットしておく。
    line_df['time'] = pandas.to_datetime(line_df['time'], format='%Y/%m/%d %H:%M')
    line_df.reset_index(drop=True, inplace=True)

    # 返信にかかる時間を設定する
    line_df['response_time'] = 0
    for i in range(len(line_df)):
        try:
            line_df['response_time'][i+1] = line_df['time'][i+1] - line_df['time'][i]
        except:
            continue

    # timedelta型には、日付、秒数、マイクロ秒数しか取得することができないため、
    # ６０でうまいこと商を取ることでかかる分数と、日を跨いだかを判定する列を追加する
    # ここで、is_night_overは8時間トークが空いたら、トークは一旦終わっていると判断する。
    l_talk_finish = []
    l_resep_mins = []
    for i in range(len(line_df)):
        if i == 0:
            l_talk_finish.append(0)
            l_resep_mins.append(0)
        else:
            l_resep_mins.append(line_df['response_time'][i].seconds / 60)
            if line_df['response_time'][i] / timedelta (hours=1) < 8:
                l_talk_finish.append(0)
            else:
                l_talk_finish.append(1)
    line_df['response_mins'] = l_resep_mins
    line_df['is_night_over'] = l_talk_finish

    #動画、写真、スタンプを送った総数を話者ごとにカウントするためのカラムを作る
    l_mov = []
    l_pic = []
    l_stp = []

    for i in line_df['talk']:
        if i == "[動画]":
            l_mov.append(1)
        else:
            l_mov.append(0)
        if i == "[写真]":
            l_pic.append(1)
        else:
            l_pic.append(0)
        if i == "[スタンプ]":
            l_stp.append(1)
        else:
            l_stp.append(0)
    line_df['is_mov'], line_df['is_pic'], line_df['is_stamp'] = l_mov, l_pic, l_stp

    # トーク内容を少し分析していく
    thanks_l = []
    apology_l = []
    question_l = []
    complement_l = []
    love_l = []
    call_l = []
    call_time_l = []
    huzai_l = []

    call_pattern = '☎ 通話時間 (\d+):(\d+)'
    for talk in line_df['talk']:
        call = re.match(call_pattern, talk)
        if call:
            call_l.append(1)
            call_time_l.append(call.group()[-5:])
        else:
            call_l.append(0)
            call_time_l.append("")
            
    line_df['is_call'] = call_l
    line_df['call_time'] = call_time_l

    emoji_l = []
    text_l = []
    for talk in line_df['talk']:
        emoji_l.append(len(extract_emoji(talk)))
        text_l.append(extract_text(talk))

    for talk in line_df['talk']:
        # thanksに関しての処理
        thanks_flg = 0
        for ele in thanks_dict:
            thanks_count = talk.count(ele)
            if thanks_count != 0:
                thanks_flg = 1
        if thanks_flg == 1:
            thanks_l.append(1)
        else:
            thanks_l.append(0)

        # apologyに関しての処理
        apology_flg = 0
        for ele in apology_dict:
            apology_count = talk.count(ele)
            if apology_count != 0:
                apology_flg = 1
        if apology_flg == 1:
            apology_l.append(1)
        else:
            apology_l.append(0)

        # complementに関しての処理
        complement_flg = 0
        for ele in complement_dict:
            complement_count = talk.count(ele)
            if complement_count != 0:
                complement_flg = 1
        if complement_flg == 1:
            complement_l.append(1)
        else:
            complement_l.append(0)

        # questionに関しての処理
        question_flg = 0
        for ele in question_dict:
            question_count = talk.count(ele)
            if question_count != 0:
                question_flg = 1
        if question_flg == 1:
            question_l.append(1)
        else:
            question_l.append(0)

        # loveに関しての処理
        love_flg = 0
        for ele in love_dict:
            love_count = talk.count(ele)
            if love_count != 0:
                love_flg = 1
        if love_flg == 1:
            love_l.append(1)
        else:
            love_l.append(0)

    line_df['is_thanks'] = thanks_l
    line_df['is_apology'] = apology_l
    line_df['is_question'] = question_l
    line_df['is_complement'] = complement_l
    line_df['is_affection'] = love_l

    guest1 = line_df[line_df["user"] == line_df['user'].unique()[0]]
    guest2 = line_df[line_df["user"] == line_df['user'].unique()[1]]
    a_thanks, a_apologize, a_complement, a_affection = guest1.sum()["is_thanks"], guest1.sum()["is_apology"], guest1.sum()["is_complement"], guest1.sum()["is_affection"]
    b_thanks, b_apologize, b_complement, b_affection = guest2.sum()["is_thanks"], guest2.sum()["is_apology"], guest2.sum()["is_complement"], guest2.sum()["is_affection"]

    # user_name
    user1=line_df['user'].unique()[0]
    user2=line_df['user'].unique()[1]

    line_df['emoji_count'] = emoji_l
    line_df['talk'] = text_l

    temp_df1 = line_df[line_df['user']==user1]
    temp_df2 = line_df[line_df['user']==user2]
    # user1の各パラメータ取得
    # emoji
    user1_emoji = sum(temp_df1['emoji_count'])
    # スタンプ
    user1_stamp = sum(temp_df1['is_stamp'])
    # 画像
    user1_pic = sum(temp_df1['is_pic'])
    # 動画
    user1_mov = sum(temp_df1['is_mov'])
    # 電話回数
    # 不在着信数
    # 平均返信速度
    temp_df1_night = temp_df1[temp_df1['is_night_over']==0]
    user1_response = int(statistics.mean(temp_df1_night['response_mins']))

    # user2の各パラメータの取得
    # emoji
    user2_emoji = sum(temp_df2['emoji_count'])
    # スタンプ
    user2_stamp = sum(temp_df2['is_stamp'])
    # 画像
    user2_pic = sum(temp_df2['is_pic'])
    # 動画
    user2_mov = sum(temp_df2['is_mov'])
    # 電話回数
    # 不在着信数
    # 平均返信速度
    temp_df2_night = temp_df2[temp_df2['is_night_over']==0]
    user2_response = int(statistics.mean(temp_df2_night['response_mins']))

    import datetime
    total_time = []
    user1_call = []
    user2_call = []

    for time, user in zip(line_df['call_time'], line_df['user']):
        if(time):
            dte = datetime.datetime.strptime(time.strip(), '%M:%S')
            if(user == user1):
                user1_call.append(1)
                user2_call.append(0)
            elif(user == user2):
                user1_call.append(0)
                user2_call.append(1)
            try:
                # print(time)
                dte = datetime.datetime.strptime(time.strip(), '%M:%S')
                # print("dte is ")
                # print(dte)
                total_time.append(dte.time().hour*60 + dte.time().minute + dte.time().second/60)
            except:
                continue
        else:
            user1_call.append(0)
            user2_call.append(0)
            
    for time in line_df['call_time']:
        try:
            dte = datetime.datetime.strptime(time, '%H:%M:%S')
            # print(dte)
            total_time.append(dte.time().hour*60 + dte.time().minute + dte.time().second/60)
        except:
            continue

    line_df['user1_call'] = user1_call
    line_df['user2_call'] = user2_call
    try:
        ave_call_time = round((sum(total_time) / len(total_time)), 2)
    except:
        ave_call_time = 0

    user1_call = len(line_df[line_df['user1_call']==1])
    user2_call = len(line_df[line_df['user2_call']==1])
    test_l = []
    for i in guest1['time']:
        test_l.append(i.date())

    test_l2 = []
    for i in guest2['time']:
        test_l2.append(i.date())

    guest1['time'] = test_l
    guest2['time'] = test_l2
    extract_df = line_df.groupby("user").sum().iloc[0:2,2:]    
    user1 = extract_df.index[0]
    user2 = extract_df.index[1]
    df1 = line_df.groupby("user", as_index=False).sum().iloc[0:2,2:]
    df1['user'] = [user1, user2]
    dict = df1.to_json(orient='records', force_ascii=False)
    print(dict)
    return dict

if __name__ == "__main__":
    # webサーバー立ち上げ
    '''
    どうしてここをコメントアウトしているか考えてください！
    '''
    #本番用
    #app.run()
    #開発用
    app.run(host='0.0.0.0',debug=True,port=5003)
    #app.run()
