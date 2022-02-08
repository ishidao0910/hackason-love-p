#!/usr/bin/env python
# coding: utf-8

# In[45]:


get_ipython().system(' pip install emoji --upgrade')


# In[8]:


# 全期間での日べつの時系列DFを返そう
# パラメータは、u1, u2というマークをつける。


# In[1]:


import pandas
import re
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
import emoji
import statistics


# In[2]:


# これらの辞書を使って、talksにこれらの単語が含まれていたら1をカウントする。
# どんなに多く入っていてもmaxを1としてカウントしていく

thanks_dict = ["ありがとう", "ありがと", "ありが", "あざまる", "あざま", "あざ", "ありがたし", "感謝", "あざす", "てんきゅ", "てんきゅん", "さんきゅ", "あり", "thanks", "thank you", "ありがつ", "助かる", "だんけ", "ダンケ", "Danke"]
apology_dict = ["ごめん", "ごめんなさい", "ごめす", "申し訳ない", "申し訳", "ごめちょ", "すみません", "すまそ", "すまん", "すんません"]
question_dict = ["?", "？", "なんで", "なぜ", "どうして", "どうやって", "どこで", "何を", "誰が"]
love_dict = ["すき", "あいしてる", "らぶゆ", "好き", "愛してる", "love"]
complement_dict = ["かっこいい","格好いい","格好良い","イケメン","かわいい","可愛い","綺麗","美しい","美人","美形", "素敵", "すてき", "ステキ"]


# In[19]:


line_df = pandas.read_csv("[LINE] Hayatoとのトーク.txt", sep='\n') 
line_df


# In[3]:


def make_dataframe(csv):
    """
    データフレーム作るモジュール
    """
    # まずテキストファイルを読み込んでカラム名を変更する
    line_df = pandas.read_csv(csv, sep='\n') 
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
    
    return line_df


# In[4]:


line_df = make_dataframe("[LINE] Hayatoとのトーク.txt")
line_df


# In[5]:


# これで絵文字の削除ができる。
# 返り値で絵文字を省いたテキストを返す。
def extract_emoji(s):
    return ''.join(c for c in s if c in emoji.UNICODE_EMOJI['en'])


# In[6]:


def extract_text(s):
    return ''.join(c for c in s if not c in emoji.UNICODE_EMOJI['en'])


# In[7]:


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
    l_talk_finish = [0]
    l_resep_mins = [0]

    for i in range(1, len(line_df)):
        # 話者が変わっていない時は、返信時間としない
        if line_df['user'][i] == line_df['user'][i-1]:
            l_resep_mins.append(0)
        else:
            l_resep_mins.append(line_df['response_time'][i].seconds / 60)
    line_df['response_mins'] = l_resep_mins


# In[8]:


def add_MPS(line_df):
    """
    画像、動画、スタンプの有無を判断するフラグをデータフレームに追加する
    """
    #動画、写真、スタンプを送った総数を話者ごとにカウントするためのカラムを作る
    line_df['is_mov'] = [1 if "[動画]" in talk else 0 for talk in line_df['talk']]
    line_df['is_pic'] = [1 if "[写真]" in talk else 0 for talk in line_df['talk']]
    line_df['is_stamp'] = [1 if "[スタンプ]" in talk else 0 for talk in line_df['talk']]


# In[9]:


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


# In[10]:


def add_emoji_len(line_df):
    """
    絵文字ののべ使用数を追加
    及び、テキストから絵文字の消去
    """
    line_df['emoji_count'] = [len(extract_emoji(talk)) for talk in line_df['talk']]
    line_df['talk'] = [extract_text(talk) for talk in line_df['talk']]


# In[11]:


def add_TACQL(line_df):
    """
    感謝、謝罪、賞賛、質問、愛情
    それぞれの辞書登録されている単語の数をトークの中からカウントする
    """
    thanks_l = []
    apology_l = []
    complement_l = []
    question_l = []
    love_l = []
    for talk in line_df['talk']:
        # 登録辞書の単語が、トークの中にいくつ含まれているかをチェック
        thanks = [1 if talk.count(ele)>0 else 0 for ele in thanks_dict]
        apology = [1 if talk.count(ele)>0 else 0 for ele in thanks_dict]
        complement = [1 if talk.count(ele)>0 else 0 for ele in thanks_dict]
        question = [1 if talk.count(ele)>0 else 0 for ele in thanks_dict]
        love = [1 if talk.count(ele)>0 else 0 for ele in thanks_dict]
        
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


# In[14]:


def set_param_to_df(line_df):
    """
    実行することで、ここに登録してあるモジュールが実行される仕様
    全体制御にする
    """
    
    add_response_mins(line_df)
    add_MPS(line_df)
    add_call(line_df)
    add_emoji_len(line_df)
    add_TACQL(line_df)


# In[15]:


set_param_to_df(line_df)


# In[16]:


line_df


# In[5]:


guest1 = line_df[line_df["user"] == line_df['user'].unique()[0]]
guest2 = line_df[line_df["user"] == line_df['user'].unique()[1]]
a_thanks, a_apologize, a_complement, a_affection = guest1.sum()["is_thanks"], guest1.sum()["is_apology"], guest1.sum()["is_complement"], guest1.sum()["is_affection"]
b_thanks, b_apologize, b_complement, b_affection = guest2.sum()["is_thanks"], guest2.sum()["is_apology"], guest2.sum()["is_complement"], guest2.sum()["is_affection"]

# user_name
user1=line_df['user'].unique()[0]
user2=line_df['user'].unique()[1]


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


# In[97]:


line_df.tail(30)


# In[7]:


line_df['call_time'][8861]


# In[153]:


count1 = 0
for i in guest1['call_time']:
    if(i):
        count1 = count1 + 1


# In[154]:


count1


# In[147]:



sum(s.startswith('通話') for s in guest1['talk'].to_list())


# In[17]:


import datetime
tstr = '2012-12-29 13:49:37'
tdatetime = datetime.datetime.strptime(tstr, '%Y-%m-%d %H:%M:%S')
tdate = datetime.date(tdatetime.year, tdatetime.month, tdatetime.day)


# In[18]:


str = '1:20:38'
str2 = '0:38'
str3 = '1:10'
dte = datetime.datetime.strptime(str, '%H:%M:%S')
type(dte)
# print(dte.total_seconds())


# In[19]:


dte = datetime.datetime.strptime(str3, '%M:%S')


# In[20]:


dte.time().hour*60, dte.time().minute,  dte.time().second/60


# In[21]:


dte.time().hour*60 + dte.time().minute + dte.time().second/60


# In[22]:


line_df


# In[7]:


import datetime

total_time = []
user1_call = []
user2_call = []
for time, user in zip(line_df['call_time'], line_df['user']):
    if(time):
        if(user == user1):
            user1_call.append(1)
            user2_call.append(0)
        elif(user == user2):
            user1_call.append(0)
            user2_call.append(1)
        try:
            dte = datetime.datetime.strptime(time, '%M:%S')
            total_time.append(dte.time().hour*60 + dte.time().minute + dte.time().second/60)
        except:
            continue
    else:
        user1_call.append(0)
        user2_call.append(0)
        
for time in line_df['call_time']:
    try:
        dte = datetime.datetime.strptime(time, '%H:%M:%S')
        print(dte)
        total_time.append(dte.time().hour*60 + dte.time().minute + dte.time().second/60)
    except:
        continue


# In[11]:


dte = datetime.datetime.strptime('0:28', '%M:%S')
dte


# In[8]:


total_time


# In[8]:


平均通話時間 = sum(total_time) / len(total_time)


# In[9]:


平均通話時間


# In[11]:


line_df['user1_call'] = user1_call
line_df['user2_call'] = user2_call


# In[12]:


line_df


# In[10]:


line_df


# In[13]:


guest1['talk']


# In[14]:


test_l = []
for i in guest1['time']:
    test_l.append(i.date())
# test_l

test_l2 = []
for i in guest2['time']:
    test_l2.append(i.date())
# test_l2

guest1['time'] = test_l
guest2['time'] = test_l2


# In[15]:


guest1['time'] = test_l
guest2['time'] = test_l2


# In[161]:


len(guest1.groupby(["time"], as_index=False).sum())


# In[171]:


len(guest2.groupby(["time"], as_index=False).sum())


# In[16]:


guest1


# In[164]:


guest1


# In[176]:


def func1(lst, value):
    return [i for i, x in enumerate(lst) if x == value]

lst = ["test", "take","test01"]
idx = func1(lst, "take")
idx


# In[178]:


type(idx[0])


# In[13]:


len(guest1[guest1['is_night_over']==1])


# In[22]:


line_df[line_df['response_mins'] < 5.0]


# In[86]:


line_df


# In[59]:


# new_line_dfを作ろう
# スイッチで話者が変わったらchangeする
# speaker switch
# hoge_switch
# if change hoge_switch, the number increases
speaker = user1
hoge_switch = []
incre = 0
flag = True
for i in range(len(line_df)):
    if(line_df['user'][i] == speaker):
        if(flag == False):
            incre = incre + 1
            hoge_switch.append(incre)
            flag = True
        else:
            hoge_switch.append(incre)
            flag = True
    else:
        if(flag == True):
            incre = incre + 1
            hoge_switch.append(incre)
            flag = False
        else:
            hoge_switch.append(incre)


# In[60]:


line_df['who_talking'] = hoge_switch


# In[61]:


line_df[['user', 'who_talking']].head(30)


# In[68]:


new_line_df = line_df.groupby(['who_talking', 'user'], as_index=False).sum()


# In[69]:


new_line_df


# In[77]:


new_line_df[(new_line_df['is_night_over']==0) & (new_line_df['user']==user1)]['response_mins'].sum()/len(new_line_df[(new_line_df['is_night_over']==0) & (new_line_df['user']==user1)]['response_mins'])


# In[80]:


new_line_df[(new_line_df['is_night_over']==0) & (new_line_df['user']==user2)]['response_mins'].sum()/len(new_line_df[(new_line_df['is_night_over']==0) & (new_line_df['user']==user2)]['response_mins'])


# In[83]:


len(new_line_df[(new_line_df['is_night_over']==1) & (new_line_df['user']==user1)]['response_mins'])


# In[84]:


len(new_line_df[(new_line_df['is_night_over']==1) & (new_line_df['user']==user2)]['response_mins'])


# In[92]:


new_line_df[(new_line_df['is_night_over']==0) & (new_line_df['response_mins']<=5.0) & (new_line_df['user']==user1)]['response_mins'].sum() / len(new_line_df[(new_line_df['is_night_over']==0) & (new_line_df['response_mins']<=5.0) & (new_line_df['user']==user1)]['response_mins'])


# In[14]:


for i in range(4):
    print(i)


# In[ ]:




