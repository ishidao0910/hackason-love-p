# import mysql.connector
from flask import Flask, request
import warnings
import pandas
import re
import emoji
import random
import string
import os
from datetime import datetime, timedelta
warnings.simplefilter('ignore')


app = Flask(__name__, static_folder='static')
app.config['JSON_AS_ASCII'] = False

@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        try:
            data = request.form
            data = data.to_dict(flat=False)
            data = data['text1'][0]
            data = data.replace(', ', '')
            test=GetRandomStr(5)
            f = open(test, 'w', encoding='UTF-8')
            f.write(data)
            f.close()
            try:
                print("start")
                line_df, user1=make_dataframe(test)
                print("user1 : ", user1)
                set_param_to_df(line_df)
                print("set_param done")
                # print(line_df)
                a = make_api_df(line_df, user1)
                os.remove(test)
                line_df = pandas.DataFrame()
                #TODO:一時ファイルを消す処理が入る
                return a
            except:
                import traceback
                traceback.print_exc()
                os.remove(test)
                return 'not analytics'
        except: 
                return "not analysis"
    else:
        a = 'not analytics'
        return a

def get_talk_user(line_df):
    """
    ユーザーを明確に区別して、トーク相手の名前を返す関数
    """
    user1 = str(line_df.columns[0]).replace("[LINE] ", "").replace("とのトーク履歴", "")
    return user1

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

def make_dataframe(csv):
    """
    データフレーム作るモジュール
    
    csv : 読み込むテキストファイル
    date_range : 分析する期間
    """
    # まずテキストファイルを読み込んでカラム名を変更する
    try:
        line_df = pandas.read_csv(csv, sep='\n')
    except:
        line_df = pandas.read_csv(csv, sep='\n', engine='python')
    user1 = get_talk_user(line_df)
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

    delete_list  = [ele for ele in line_df['user'].unique() if "送信を取り消しました" in ele]
    for target in delete_list:
        line_df = line_df[line_df['user'] != target]

    line_df = line_df[line_df['user']!=""]

#     日付で調整入れるときはここを使う
#     before_n_days = line_df['time'][len(line_df)-1].replace(hour=0, minute=0, second=0, microsecond=0)- timedelta(days=date_range-1)
#     line_df = line_df[line_df['time'] > before_n_days]

    line_df.reset_index(drop=True, inplace=True)
    return line_df, user1

# これで絵文字の削除ができる。
# 返り値で絵文字を省いたテキストを返す。
def extract_emoji(s):
    return ''.join(c for c in s if c in emoji.UNICODE_EMOJI['en'])

def extract_text(s):
    return ''.join(c for c in s if not c in emoji.UNICODE_EMOJI['en'])

def add_response_mins(line_df):
    """
    返信にかかる時間をカラムに追加する
    """
    # 返信にかかる時間を設定する
    line_df['response_time'] = 0
    for i in range(len(line_df)):
        try:
            line_df['response_time'][i+1] = line_df['time'][i+1] - line_df['time'][i]
        except:
            continue
            
    # timedelta型には、日付、秒数、マイクロ秒数しか取得することができないため、
    # l_talk_finish = [0]
    l_resep_mins = [0]

    for i in range(1, len(line_df)):
        # 話者が変わっていない時は、返信時間としない
        if line_df['user'][i] == line_df['user'][i-1]:
            l_resep_mins.append(0)
        else:
            l_resep_mins.append(int(line_df['response_time'][i].seconds / 60))
    line_df['response_mins'] = l_resep_mins
    
    # 16時間以上返信が空いているのは、もう会話していないと判断する。
    line_df['response_mins'] = [x if x < 960 else 0 for x in line_df['response_mins']]

def add_MPS(line_df):
    """
    画像、動画、スタンプの有無を判断するフラグをデータフレームに追加する
    """
    #動画、写真、スタンプを送った総数を話者ごとにカウントするためのカラムを作る
    line_df['is_mov'] = [1 if "[動画]" in talk else 0 for talk in line_df['talk']]
    line_df['is_pic'] = [1 if "[写真]" in talk else 0 for talk in line_df['talk']]
    line_df['is_stamp'] = [1 if "[スタンプ]" in talk else 0 for talk in line_df['talk']]
    
def add_call(line_df):
    """
    電話の有無フラグの追加
    及び、電話をしていた場合、その時間を抽出
    """
    call_pattern = '☎ 通話時間 (\d+):(\d+)'
    call_l = [1 if re.match(call_pattern, talk) else 0 for talk in line_df['talk']]
    call_time_l = [re.match(call_pattern, talk).group()[-5:] if re.match(call_pattern, talk) else "" for talk in line_df['talk']]
    line_df['is_call'] = call_l
    line_df['call_time'] = call_time_l
    
def arrange_call_time(line_df):
    """
    line_dfのcall_timeを、文字列から計算可能な数値型に変更するモジュール
    """
    import datetime
    line_df['call_time'] = [time.replace(" ", "") for time in line_df['call_time']]
    total_time = []
    for time in line_df['call_time']:
        if(time.count(":") == 1):
            dte = datetime.datetime.strptime(time, '%M:%S')
            total_time.append(dte.time().hour*60 + dte.time().minute + dte.time().second/60)
        elif(time.count(":") == 2):
            dte = datetime.datetime.strptime(time, '%H:%M:%S')
            total_time.append(dte.time().hour*60 + dte.time().minute + dte.time().second/60)
        else:
            total_time.append(0)
    line_df['call_time'] = total_time
    
def add_emoji_len(line_df):
    """
    絵文字ののべ使用数を追加
    及び、テキストから絵文字の消去
    """
    line_df['emoji_count'] = [len(extract_emoji(talk)) for talk in line_df['talk']]
    line_df['talk'] = [extract_text(talk) for talk in line_df['talk']]
    
def add_TACQL(line_df):
    """
    感謝、謝罪、賞賛、質問、愛情
    それぞれの辞書登録されている単語の数をトークの中からカウントする
    """
    thanks_dict = ["ありがとう", "ありがと", "ありが", "あざまる", "あざま", "あざ", "ありがたし", "感謝", "あざす", "てんきゅ", "てんきゅん", "さんきゅ", "あり", "thanks", "thank you", "ありがつ", "助かる"]
    apology_dict = ["ごめん", "ごめんなさい", "ごめす", "申し訳ない", "申し訳", "ごめちょ", "すみません", "すまそ", "すまん", "すんません"]
    question_dict = ["?", "？", "なんで", "なぜ", "どうして", "どうやって", "どこで", "何を", "誰が"]
    love_dict = ["すき", "あいしてる", "らぶゆ", "好き", "愛してる", "love"]
    complement_dict = ["かっこいい","格好いい","格好良い","イケメン","かわいい","可愛い","綺麗","美しい","美人","美形", "素敵", "すてき", "ステキ"]

    thanks_l = []
    apology_l = []
    complement_l = []
    question_l = []
    love_l = []
    for talk in line_df['talk']:
        # 登録辞書の単語が、トークの中にいくつ含まれているかをチェック
        thanks = [1 if talk.count(ele)>0 else 0 for ele in thanks_dict]
        apology = [1 if talk.count(ele)>0 else 0 for ele in apology_dict]
        complement = [1 if talk.count(ele)>0 else 0 for ele in complement_dict]
        question = [1 if talk.count(ele)>0 else 0 for ele in question_dict]
        love = [1 if talk.count(ele)>0 else 0 for ele in love_dict]
        
        # 含まれていたら、トークの中身に感情表現があったことを示すフラグを追加
        thanks_l.append(1 if sum(thanks)>0 else 0)
        apology_l.append(1 if sum(apology)>0 else 0)
        complement_l.append(1 if sum(complement)>0 else 0)
        question_l.append(1 if sum(question)>0 else 0)
        love_l.append(1 if sum(love)>0 else 0)
        
    line_df['is_thanks'] = thanks_l
    line_df['is_apology'] = apology_l
    line_df['is_question'] = question_l
    line_df['is_complement'] = complement_l
    line_df['is_affection'] = love_l
    
def add_words_count(line_df):
    line_df["words_count"] = line_df['talk'].apply(lambda x: len(x))
    line_df.drop("talk", axis=1, inplace=True)

def set_param_to_df(line_df):
    """
    実行することで、ここに登録してあるモジュールが実行される仕様
    全体制御にする
    """
    add_response_mins(line_df)
    add_MPS(line_df)
    add_call(line_df)
    arrange_call_time(line_df)
    add_emoji_len(line_df)
    add_TACQL(line_df)
    add_words_count(line_df)
    print("words done")

def get_chat_score(chat_count):
    """
    チャットの送信回数が1000回以上で満点になるように調整
    10点以上は全て10点に丸める
    """
    chat_score = chat_count//100
    if chat_score > 10: chat_score = 10
    else: pass
    return chat_score

def get_response_time_score(ave_response_time):
    """
    9分までで10点
    10分から9点
    55分から0点
    """
    response_score = 10 - ave_response_time//5 + 1
    if response_score < 0: response_score = 0
    elif response_score > 10: response_score = 10
    else: pass
    return response_score

def get_pms_score(count):
    """
    picとmovは、加点方式にします。
    これが0でも100点取ることはできるけど、あると加点されるから楽
    """
    score = count//10
    if score > 10: score = 10
    else: pass
    return score

def get_emoji_score(count):
    """
    500個で10点
    """
    score = count//50
    if score > 10: score = 10
    else: pass
    return score

def get_call_count_score(call_count):
    """
    100回で10点
    """
    call_count_score = call_count // 10
    if call_count_score > 10: call_count_score = 10
    else: pass
    return call_count_score

def get_call_time_score(call_time):
    """
    1500分で10点
    """
    call_score = call_time//150
    if call_score > 10: call_score = 10
    else: pass
    return call_score

def get_emotion_score(count):
    """
    感情のスコアリング
    """
    emotion_score = count//5
    if emotion_score > 10: emotion_score = 10
    return emotion_score

def get_word_count_score(count):
    """
    10000文字で10点
    """
    score = count//1000
    if score > 10: score = 10
    else: pass
    return score

def get_str_emotion(count):
    if count > 50: 
        str = "A"
    elif (count > 35) & (count<=50): 
        str = "B"
    elif (count > 20) & (count<=35): 
        str = "C"
    else: 
        str = "D"
    return str

def make_api_df(line_df, user1):
    if (user1 == line_df['user'].unique()[0]):
        user2 = line_df['user'].unique()[1]
    else:
        user2 = line_df['user'].unique()[0]
    print("user1 : ", user1)
    print("user2 : ", user2)
    # if (len(line_df.groupby("user", as_index=False).sum()))==3:
    #     temp_df = line_df.groupby("user", as_index=False).sum().iloc[1:3, :]
    #     temp_df = temp_df.reset_index()
    # else:
    temp_df = line_df.groupby("user", as_index=False).sum().iloc[:2, :]
    user1_index = temp_df[temp_df['user']==user1].index[0]
    user2_index = temp_df[temp_df['user']==user2].index[0]
    temp_df = temp_df.reindex([user1_index, user2_index], axis=0) # DFの順番固定
    temp_df['chat_count'] = [len(line_df[line_df['user']==user1]), len(line_df[line_df['user']==user2])]
    temp_df['ave_response_mins'] = temp_df['response_mins'] / temp_df['chat_count']
    temp_df = temp_df.astype({'ave_response_mins':'int64', 'call_time':'int64'})
    temp_df.drop(['response_mins'], axis = 1, inplace=True)
    
    temp_new_df = temp_df.copy()
    for i in range(len(temp_new_df)):
        temp_new_df["user"][i] = temp_df['user'][i] + "_score"
        temp_new_df["is_mov"][i] = get_pms_score(temp_df['is_mov'][i]) * 10
        temp_new_df["is_pic"][i] = get_pms_score(temp_df['is_pic'][i]) * 10
        temp_new_df["is_stamp"][i] = get_pms_score(temp_df['is_stamp'][i]) * 10
        temp_new_df["is_call"][i] = get_call_count_score(temp_df['is_call'][i]) * 10
        temp_new_df["call_time"][i] = get_call_time_score(temp_df['call_time'][i]) * 10
        temp_new_df["emoji_count"][i] = get_emoji_score(temp_df['emoji_count'][i]) * 10
        temp_new_df["is_thanks"][i] = get_emotion_score(temp_df['is_thanks'][i]) * 10
        temp_new_df["is_apology"][i] = 0 # 特に考慮しない
        temp_new_df["is_question"][i] = get_emotion_score(temp_df['is_question'][i]) * 10
        temp_new_df["is_complement"][i] = get_emotion_score(temp_df['is_complement'][i]) * 10
        temp_new_df["is_affection"][i] = get_emotion_score(temp_df['is_affection'][i]) * 10
        temp_new_df["words_count"][i] = get_word_count_score(temp_df['words_count'][i]) * 10
        temp_new_df["chat_count"][i] = get_chat_score(temp_df['chat_count'][i]) * 10
        temp_new_df['ave_response_mins'][i] = get_response_time_score(temp_df['ave_response_mins'][i]) * 10
        num1 = temp_df['is_thanks'][i]
        num2 = temp_df['is_apology'][i]
        num3 = temp_df['is_question'][i]
        num4 = temp_df['is_complement'][i]
        num5 = temp_df['is_affection'][i]
    temp_df = pandas.concat([temp_df, temp_new_df]) 
    temp_df = temp_df.append({'user':"ABCD_score", "is_mov":0, "is_pic":0, "is_stamp":0, "is_call":0, "call_time":0, "emoji_count":0, "is_thanks":get_str_emotion(num1),"is_apology":get_str_emotion(num2),"is_question":get_str_emotion(num3),"is_complement":get_str_emotion(num4),"is_affection":get_str_emotion(num5), "words_count":0, "chat_count":0, "ave_response_mins":0 }, ignore_index=True)
    dict = temp_df.to_json(orient='records', force_ascii=False)
    print(dict)
    return dict

@app.route('/style_suggest', methods=['GET', 'POST'])
def style_suggest():
    print(request)
    if request.method == 'POST':
        style_suggest = request.json
        print('愛着スタイル : ', style_suggest['style'])
        # print('s1_user')
        # print(style_suggest['s1_user'])
        # print('s2_user')
        # print(style_suggest['s2_user'])
        suggest_contents = get_suggest_contents(style_suggest['style'], style_suggest['s1_user'], style_suggest['s2_user'])
        print(suggest_contents)
        dic = {"contents":suggest_contents}
        return dic
    else:
        return 'no data'

def get_suggest_contents(style, s1_user_dict, s2_user_dict):
    """
    僕だってこんな関数作りたくないんです。
    pythonが可哀想。

    input 
        style int :
            style1~4の愛着スタイル
        s1_user_dict dict: 
            相手のテキスト分析結果
        s2_user_dict dict:
            自分のテキスト分析結果
    output : スタイル別のアクションサジェスト
    """
    suggest_contents = []
    if style==1:
        suggest_contents.append("あなたはとらわれ型であり、相手に執着する傾向があります。\n相手との関係性を大事にしたいのであれば、自分のことも同じように大切にしてあげましょう。\n")
        if (s1_user_dict['is_question'] >= s2_user_dict['is_question']*0.9): suggest_contents.append("もっと質問して相手のことを知りましょう。\n")
        else: pass
        if (s1_user_dict['is_thanks'] >= s2_user_dict['is_thanks']*0.9): suggest_contents.append("感謝の言葉を頻繁に伝えるのも、回り回って自分のためになります。\n")
        else: pass
        if ((s1_user_dict['is_stamp'] > s2_user_dict['is_stamp']*0.7) | (s1_user_dict['is_stamp'] < s2_user_dict['is_stamp']*0.7)): suggest_contents.append("スタンプの使い方も、相手に合わせてみるといいかもしれません。\n")
        else: pass
        if ((s1_user_dict['chat_count'] > s2_user_dict['chat_count']*0.7) | (s1_user_dict['chat_count'] < s2_user_dict['chat_count']*0.7)): suggest_contents.append("自分のチャットの数を相手のチャット数に合わせてみるのも一つの手です。\n")
        else: pass
        
    elif style==2:
        suggest_contents.append("あなたは回避型であり、相手を好きになるのを怖がる傾向があります。\nこれは言い換えると、相手からの好感度UPを妨げているのは自分自身とも言えます。\n")
        if (s1_user_dict['is_question'] >= s2_user_dict['is_question']*0.9): suggest_contents.append("もっと質問して相手のことを知りましょう。\n")
        else: pass
        if (s1_user_dict['is_thanks'] >= s2_user_dict['is_thanks']*0.9): suggest_contents.append("感謝の言葉を頻繁に伝えるのも、回り回って自分のためになります。\n")
        else: pass
        if (s1_user_dict['is_call'] >= s2_user_dict['is_call']*2): suggest_contents.append("自分から能動的に電話をかけてみるもの1つの手です。\n")
        else: pass
        if (s1_user_dict['is_stamp'] > s2_user_dict['is_stamp']): suggest_contents.append("相手がスタンプを使うタイミングに合わせて、スタンプで返信するのもありです。\n")
        else: pass
        if (s1_user_dict['ave_response_mins'] < s2_user_dict['ave_response_mins']): suggest_contents.append("相手からのチャットは、すぐに返信しても大丈夫そうです。駆け引きとか考える必要ありません。\n")
        else: pass
    elif style==3:
        suggest_contents.append("あなたは安定型であり、相手との関係を良好に築ける傾向があります。\nあなたが安定しているので、あなた自身の行動を大きく変える必要はありません。ですが、安定のしすぎも物足りない場合があるので、\n")
        if ((s1_user_dict['is_affection'] > s2_user_dict['is_affection']*0.9) | (s1_user_dict['is_affection'] < s2_user_dict['is_affection']*0.9)): suggest_contents.append("相手と愛情表現の回数を合わせる努力をする。\n")
        else: pass
        if ((s1_user_dict['is_question'] > s2_user_dict['is_question']*0.9) | (s1_user_dict['is_question'] < s2_user_dict['is_question']*0.9)): suggest_contents.append("質問の量を合わせに行ってみる。\n")
        else: pass
        if ((s1_user_dict['is_thanks'] > s2_user_dict['is_qis_thanksuestion']*0.9) | (s1_user_dict['is_thanks'] < s2_user_dict['is_thanks']*0.9)): suggest_contents.append("感謝には感謝で返す。\n")
        else: pass
        suggest_contents.append("\n等の変化を加えてみてもいいかもしれません。")
    elif style==4:
        suggest_contents.append("あなたは恐怖型であり、相手に嫌われるのを極端に恐れがちな傾向があります。\nもし現状に不満があるようなら、以下のようなアクションをとってみるといいかもしれません。\n")
        if ((s1_user_dict['is_question'] > s2_user_dict['is_question']*0.8) | (s1_user_dict['is_question'] < s2_user_dict['is_question']*0.8)): suggest_contents.append("・疑問の回数を相手に合わせる。\n")
        else: pass
        if ((s1_user_dict['is_thanks'] > s2_user_dict['is_thanks']*0.8) | (s1_user_dict['is_thanks'] < s2_user_dict['is_thanks']*0.8)): suggest_contents.append("・感謝の言葉の頻繁を相手に合わせる。\n")
        else: pass
        if (s1_user_dict['is_call'] >= s2_user_dict['is_call']*2): suggest_contents.append("自分から能動的に電話をかけてみるもの1つの手です。\n")
        else: pass
        if ((s1_user_dict['is_stamp'] > s2_user_dict['is_stamp']*0.8) | (s1_user_dict['is_stamp'] < s2_user_dict['is_stamp']*0.8)): suggest_contents.append("・スタンプの使い方を、相手に合わせてみる。\n")
        else: pass
        if ((s1_user_dict['chat_count'] > s2_user_dict['chat_count']*0.8) | (s1_user_dict['chat_count'] < s2_user_dict['chat_count']*0.8)): suggest_contents.append("・相手のチャット数に合わせてみる。\n")
        else: pass
    else:
        pass
    suggest_contents = "".join(suggest_contents)
    return suggest_contents



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
