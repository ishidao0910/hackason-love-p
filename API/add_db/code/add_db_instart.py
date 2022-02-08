# import mysql.connector
from flask import Flask, jsonify, request
from werkzeug.datastructures import ContentSecurityPolicy
import mysql.connector as db
import base64
import numpy as np
from PIL import Image
import base64
from io import BytesIO
import cv2
import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
import random
import string
import os
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import urllib.request as urllib
from urllib.parse import urlencode
from urllib.error import HTTPError 

# #envファイルの読み込み
load_dotenv()
cred = credentials.Certificate('/code/code/test.json')
# cred = credentials.Certificate('test.json')
firebase_admin.initialize_app(cred, {'storageBucket': 'lovep-3ca51.appspot.com'})

def test():
    conn = db.connect(
            host="db_server",
            port=3306,
            user="root",#ユーザidの記入
            password="pass",#パスワードの記入
            database="loveP"#データベースの名前を記入
        )
    return conn

# def test():
#     conn = db.connect(
#             host="",
#             port=3307,
#             user="root",#ユーザidの記入
#             password="pass",#パスワードの記入
#             database="loveP"#データベースの名前を記入
#         )
#     return conn

def test2(user_id):
    conn=test()
    cursor = conn.cursor()
    token=GetRandomStr(5)
    sql = "INSERT INTO user_a (id ,user_name, user_url) VALUES (%s , %s , %s)"
    data = [(None,user_id,token)]
    cursor.executemany(sql, data)
    conn.commit()
    cursor.close()
    return token

def test3(user_id):
    conn=test()
    cursor = conn.cursor()
    token=GetRandomStr(5)
    sql = "INSERT INTO user_a (id ,user_name, user_url) VALUES (%s , %s , %s)"
    data = [(None,user_id,token)]
    cursor.executemany(sql, data)
    conn.commit()
    cursor.close()

def send_email(to_email,token):
    message = Mail(
    from_email='line.analysis1227@gmail.com',
    to_emails=to_email,
    subject='LovePアカウント仮登録完了のお知らせ',
    html_content='LovePの仮登録が完了しました<br>以下のURLを押して本登録を終了させてください<br>'+'http://ec2-13-113-183-219.ap-northeast-1.compute.amazonaws.com/sinup/'+str(token))
    try:
        sg = SendGridAPIClient(os.environ['KEY'])
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)

def GetRandomStr(num):
    # 英数字をすべて取得
    dat = string.digits + string.ascii_lowercase + string.ascii_uppercase
    # 英数字からランダムに取得
    return ''.join([random.choice(dat) for i in range(num)])

app = Flask(__name__, static_folder='static')
app.config['JSON_AS_ASCII'] = False

@app.route('/', methods=['GET', 'POST'])
def add_girl():
    if request.method == 'POST':
        conn=test()
        cursor = conn.cursor()
        girls_list = request.form
        user_id = girls_list['user_id']
        user_gn = girls_list['girls_name']
        sql = "INSERT INTO list_girl (id, user_id, user_gn, img, flag) VALUES (%s, %s, %s,%s, %s)"
        data = [(None, user_id, user_gn, None,1)]
        cursor.executemany(sql, data)
        conn.commit()
        cursor.close()
        return 'data OK'
    else:
        conn=test()
        return 'data NG'

@app.route('/profile_edit', methods=['GET', 'POST'])
def profile_edit():
    if request.method == 'POST':
        conn=test()
        cursor = conn.cursor()
        user_info = request.form
        sql = ('''
        UPDATE  user
        SET     user_name = %s , display_name = %s , email =%s
        WHERE   user_id = %s
        ''')
        data = [(user_info['user_name'], user_info['display_name'], user_info['user_email'], user_info['user_id'] )]
        cursor.executemany(sql, data)
        conn.commit()
        cursor.close()
        return 'data OK'
    else:
        return 'data NG'

#画像をアップロードする為の関数
@app.route('/profile_edit_1', methods=['GET', 'POST'])
def profile_edit_1():
    if request.method == 'POST':
        conn=test()
        base64image = request.form
        user_info = request.form
        base64image=base64image['image_data'].replace('data:image/png;base64,', '')
        textBytes = base64.b64decode(base64image.encode())
        encode=base64.b64encode(textBytes)
        img_binary = base64.b64decode(encode)
        jpg=np.frombuffer(img_binary,dtype=np.uint8)
        img = cv2.imdecode(jpg, cv2.IMREAD_COLOR)
        #TODO: ここは, randomの画像名を振る
        test1=GetRandomStr(5)
        image_file=str(test1)+".jpg"
        cv2.imwrite(image_file,img)
        bucket = storage.bucket()
        blob = bucket.blob(image_file)
        blob.upload_from_filename(image_file)
        blob.make_public()
        #処理フロー的にはこのblob.public_urlをDBのimgに埋め込む
        cursor = conn.cursor()
        sql = ('''
        UPDATE  user
        SET     user_name = %s , display_name = %s , email =%s ,img =%s
        WHERE   user_id = %s
        ''')
        data = [(user_info['user_name'], user_info['display_name'], user_info['user_email'],blob.public_url, user_info['user_id'] )]
        cursor.executemany(sql, data)
        conn.commit()
        cursor.close()
        #ここでデータを消す
        os.remove(image_file)
        return 'data OK'
    else:
        return 'data NG'

#画像をアップロードする為の関数
@app.route('/profile_edit_2', methods=['GET', 'POST'])
def profile_edit_2():
    if request.method == 'POST':
        conn=test()
        base64image = request.form
        girls_list = request.form
        base64image=base64image['image_data'].replace('data:image/png;base64,', '')
        textBytes = base64.b64decode(base64image.encode())
        encode=base64.b64encode(textBytes)
        img_binary = base64.b64decode(encode)
        jpg=np.frombuffer(img_binary,dtype=np.uint8)
        img = cv2.imdecode(jpg, cv2.IMREAD_COLOR)
        #TODO: ここは, randomの画像名を振る
        test1=GetRandomStr(5)
        image_file=str(test1)+".jpg"
        cv2.imwrite(image_file,img)
        bucket = storage.bucket()
        blob = bucket.blob(image_file)
        blob.upload_from_filename(image_file)
        blob.make_public()
        #処理フロー的にはこのblob.public_urlをDBのimgに埋め込む
        cursor = conn.cursor()
        user_id = girls_list['user_id']
        user_gn = girls_list['girls_name']
        sql = "INSERT INTO list_girl (id, user_id, user_gn, img, flag) VALUES (%s, %s, %s,%s, %s)"
        data = [(None, user_id, user_gn, blob.public_url,1)]
        cursor.executemany(sql, data)
        conn.commit()
        cursor.close()
        #ここでデータを消す
        os.remove(image_file)
        return 'data OK'
    else:
        return 'data NG'

@app.route('/user_registration', methods=['GET', 'POST'])
def user_registration():
    if request.method == 'POST':
        conn=test()
        cursor = conn.cursor()
        user_registration = request.json
        user_id = user_registration['user_id']
        u_pass = user_registration['user_pass']
        email = user_registration['user_email']
        #ここで一度重複チェックを行う必要がある.
        sql = "INSERT INTO user (user_id , user_name, display_name, pass, email,flag,profile) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        data = [(None, str(user_id),None,str(u_pass),str(email),0,None)]
        cursor.executemany(sql, data)
        conn.commit()
        cursor.close()
        token=test2(user_id)
        send_email(email,token)
        return 'data OK'
    else:
        conn=test()
        return 'data NG'

@app.route('/user_flag', methods=['GET', 'POST'])
def user_flag():
    if request.method == 'POST':
        conn=test()
        cursor = conn.cursor()
        user_info = request.json
        print(user_info)
        sql = ('''
        UPDATE  user
        SET     flag = %s
        WHERE   user_name = %s
        ''')
        data = [(1, user_info['user_name'])]
        cursor.executemany(sql, data)
        conn.commit()
        cursor.close()
        #DBから該当のデータを消す処理が加われば終了
        
        return 'data OK'
    else:
        return 'data NG'

@app.route('/style', methods=['GET', 'POST'])
def style():
    if request.method == 'POST':
        conn=test()
        cursor = conn.cursor()
        user_info = request.json
        print(user_info)
        sql = ('UPDATE user SET ans_flag = %s , style = %s WHERE user_id = %s')
        data = [(1,user_info['style'],user_info['username'])]
        cursor.executemany(sql, data)
        conn.commit()
        cursor.close()
        #DBから該当のデータを消す処理が加われば終了
        return 'data OK'
    else:
        return 'data NG'

@app.route('/suggest_push', methods=['GET', 'POST'])
def suggest_push():
    if request.method == 'POST':
        conn=test()
        cursor = conn.cursor()
        user_info = request.json
        #日付取得
        dt_now = datetime.datetime.now()
        date=dt_now.strftime('%Y-%m-%d')
        slag=dt_now.strftime('%Y%m%d%H%M%S')
        sql = ('INSERT INTO total_score_girls (id , date , user_id , girls_id , s1 , s2 , s1_score , s2_score , s2_value, slag,score)  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)')
        s1_user="'"+str(user_info['s1_user'])+"'"
        s2_user="'"+str(user_info['s2_user'])+"'"
        s1_user_score="'"+str(user_info['s1_user_score'])+"'"
        s2_user_score="'"+str(user_info['s2_user_score'])+"'"
        s2_user_value="'"+str(user_info['s2_user_value'])+"'"
        s1_user=s1_user.replace("'",'"')
        s1_user=s1_user.replace('"{',"{")
        s1_user=s1_user.replace('}"',"}")
        s2_user=s2_user.replace("'",'"')
        s2_user=s2_user.replace('"{',"{")
        s2_user=s2_user.replace('}"',"}")
        s1_user_score=s1_user_score.replace("'",'"')
        s1_user_score=s1_user_score.replace('"{',"{")
        s1_user_score=s1_user_score.replace('}"',"}")
        s2_user_score=s2_user_score.replace("'",'"')
        s2_user_score=s2_user_score.replace('"{',"{")
        s2_user_score=s2_user_score.replace('}"',"}")
        s2_user_value=s2_user_value.replace("'",'"')
        s2_user_value=s2_user_value.replace('"{',"{")
        s2_user_value=s2_user_value.replace('}"',"}")
        s2_user_value=s2_user_value.replace("}'","}")
        data = [(None, date, user_info['user_id'], user_info['girls_id'], s1_user , s2_user, s1_user_score, s2_user_score , s2_user_value ,str(slag),user_info['score'])]
        cursor.executemany(sql, data)
        conn.commit()
        cursor.close()
        #DBから該当のデータを消す処理が加われば終了
        return 'data OK'
    else:
        return 'data NG'

if __name__ == "__main__":
    # webサーバー立ち上げ
    '''
    どうしてここをコメントアウトしているか考えてください
    '''
    #開発用
    app.run(host='0.0.0.0',debug=True,port=5001)
    # app.run(host='localhost',debug=True,port=5001)
    #app.run()
