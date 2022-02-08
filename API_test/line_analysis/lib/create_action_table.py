import pandas
import re
from datetime import date, datetime, timedelta
import emoji

# これらの辞書を使って、talksにこれらの単語が含まれていたら1をカウントする。
# どんなに多く入っていてもmaxを1としてカウントしていく

thanks_dict = ["ありがとう", "ありがと", "ありが", "あざまる", "あざま", "あざ", "ありがたし", "感謝", "あざす", "てんきゅ", "てんきゅん", "さんきゅ", "あり", "thanks", "thank you", "ありがつ", "助かる", "だんけ", "ダンケ", "Danke"]
apology_dict = ["ごめん", "ごめんなさい", "ごめす", "申し訳ない", "申し訳", "ごめちょ", "すみません", "すまそ", "すまん", "すんません"]
question_dict = ["?", "？", "なんで", "なぜ", "どうして", "どうやって", "どこで", "何を", "誰が"]
love_dict = ["すき", "あいしてる", "らぶゆ", "好き", "愛してる", "love"]
complement_dict = ["かっこいい","格好いい","格好良い","イケメン","かわいい","可愛い","綺麗","美しい","美人","美形", "素敵", "すてき", "ステキ"]

def make_dataframe(csv, date_range):
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

    before_n_days = line_df['time'][len(line_df)-1].replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=date_range-1)
    line_df = line_df[line_df['time'] > before_n_days]

    line_df.reset_index(drop=True, inplace=True)
    
    return line_df


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
    l_talk_finish = [0]
    l_resep_mins = [0]

    for i in range(1, len(line_df)):
        # 話者が変わっていない時は、返信時間としない
        if line_df['user'][i] == line_df['user'][i-1]:
            l_resep_mins.append(0)
        else:
            l_resep_mins.append(line_df['response_time'][i].seconds / 60)
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

def make_cluster_df(line_df):
    set_param_to_df(line_df)
    user1=line_df['user'].unique()[0]
    user2=line_df['user'].unique()[1]
    print("user1 : ", user1)
    print("user2 : ", user2)
    line_df['time'] = line_df['time'].dt.strftime('%Y/%m/%d')

    cluster_df = pandas.DataFrame()

    # add parameter
    print("user1 : ", user1)
    print("user2 : ", user2)
    for date in line_df.groupby("time").count().index:
        temp_new_df = pandas.DataFrame()
        u1_df = line_df[(line_df['time']==date) & (line_df['user']==user1)]
        u2_df = line_df[(line_df['time']==date) & (line_df['user']==user2)]
        temp_new_df['date']  = [date]
        temp_new_df['u1_ave_response_time'] = [(sum(u1_df['response_mins']) / len(u1_df)) if len(u1_df)>0 else 0]
        temp_new_df['u2_ave_response_time'] = [(sum(u2_df['response_mins']) / len(u2_df)) if len(u2_df)>0 else 0]
        temp_new_df['u1_pic'] = [sum(u1_df['is_pic']) if len(u1_df)>0 else 0]
        temp_new_df['u2_pic'] = [sum(u2_df['is_pic']) if len(u2_df)>0 else 0]
        temp_new_df['u1_mov'] = [sum(u1_df['is_mov']) if len(u1_df)>0 else 0]
        temp_new_df['u2_mov'] = [sum(u2_df['is_mov']) if len(u2_df)>0 else 0]
        temp_new_df['u1_stamp'] = [sum(u1_df['is_stamp']) if len(u1_df)>0 else 0]
        temp_new_df['u2_stamp'] = [sum(u2_df['is_stamp']) if len(u2_df)>0 else 0]
        temp_new_df['u1_emoji'] = [sum(u1_df['emoji_count']) if len(u1_df)>0 else 0]
        temp_new_df['u2_emoji'] = [sum(u2_df['emoji_count']) if len(u2_df)>0 else 0]
        temp_new_df['u1_call_total_time'] = [sum(u1_df['call_time']) if len(u1_df)>0 else 0]
        temp_new_df['u2_call_total_time'] = [sum(u2_df['call_time']) if len(u2_df)>0 else 0]
        temp_new_df['u1_thanks'] = [sum(u1_df['is_thanks']) if len(u1_df)>0 else 0]
        temp_new_df['u2_thanks'] = [sum(u2_df['is_thanks']) if len(u2_df)>0 else 0]
        temp_new_df['u1_apology'] = [sum(u1_df['is_apology']) if len(u1_df)>0 else 0]
        temp_new_df['u2_apology'] = [sum(u2_df['is_apology']) if len(u2_df)>0 else 0]
        temp_new_df['u1_question'] = [sum(u1_df['is_question']) if len(u1_df)>0 else 0]
        temp_new_df['u2_question'] = [sum(u2_df['is_question']) if len(u2_df)>0 else 0]
        temp_new_df['u1_complement'] = [sum(u1_df['is_complement']) if len(u1_df)>0 else 0]
        temp_new_df['u2_complement'] = [sum(u2_df['is_complement']) if len(u2_df)>0 else 0]
        temp_new_df['u1_love'] = [sum(u1_df['is_affection']) if len(u1_df)>0 else 0]
        temp_new_df['u2_love'] = [sum(u2_df['is_affection']) if len(u2_df)>0 else 0]
        temp_new_df['u1_total_words_count'] = [sum(u1_df['words_count']) if len(u1_df)>0 else 0]
        temp_new_df['u2_total_words_count'] = [sum(u2_df['words_count']) if len(u2_df)>0 else 0]
        temp_new_df['u1_min_response'] = [min(u1_df['response_mins']) if len(u1_df)>0 else 0]
        temp_new_df['u2_min_response'] = [min(u2_df['response_mins']) if len(u2_df)>0 else 0]
        temp_new_df['u1_max_response'] = [max(u1_df['response_mins']) if len(u1_df)>0 else 0]
        temp_new_df['u2_max_response'] = [max(u2_df['response_mins']) if len(u2_df)>0 else 0]

        cluster_df = pandas.concat([cluster_df,temp_new_df])
    cluster_df.reset_index(drop=True, inplace=True)
    line_df = line_df.drop(range(len(line_df)))
    return cluster_df