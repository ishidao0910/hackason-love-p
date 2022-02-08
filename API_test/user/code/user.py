# import mysql.connector
from flask import Flask, jsonify, request
import json
import mysql.connector as db


def test():
    conn = db.connect(
            host="db_server",
            port=3306,
            user="root",#ユーザidの記入
            password="pass",#パスワードの記入
            database="loveP"#データベースの名前を記入
        )
    return conn

app = Flask(__name__, static_folder='static')
app.config['JSON_AS_ASCII'] = False

@app.route('/', methods=['GET', 'POST'])
def User_login():
    print(request)
    if request.method == 'POST':
        user_login = request.json
        user_name = request.json['user_name']
        print(user_login)
        conn = test()
        cur = conn.cursor()
        sql = 'select * from user WHERE user_name='+'"'+user_name+'"'+' and flag=1 ;'
        cur.execute(sql)
        user_name_load = cur.fetchall()
        print(user_name_load)
        user_name_load=list(user_name_load[0])
        print(user_name_load)
        cur.close()
        conn.close()
        if user_name_load[3]==user_login['pass']:
            print('OK')
            dic =  {"login_user" : user_name_load[0] , "flag" : "true"}
            
        else:
            dic =  {"login_user" : user_name_load[0] , "flag" : "flase"}
    else:
        dic = 'no data'
    return dic

@app.route('/user_information', methods=['GET', 'POST'])
def User_information():
    print(request)
    if request.method == 'POST':
        user_information = request.json
        print(user_information['user_id'])
        #SQLを叩く
        conn = test()
        cur = conn.cursor()
        sql = 'select * from user WHERE user_id='+'"'+str(user_information['user_id'])+'"'+' and flag=1 ;'
        cur.execute(sql)
        user_information = cur.fetchall()
        #user情報が取れる
        print(user_information)
        user_information=list(user_information[0])
        dic =  {"user_id" : user_information[1] ,"display_name" : user_information[2], "user_email" : user_information[4]}
        cur.close()
        conn.close()
    else:
        dic = 'data ng'
    return dic

@app.route('/girls_list', methods=['GET', 'POST'])
def girls_list():
    print(request)
    if request.method == 'POST':
        user_girl_list = request.json
        print(user_girl_list['user_id'])
        #SQLを叩く
        conn = test()
        cur = conn.cursor(dictionary=True)
        sql = 'select * from list_girl WHERE user_id='+'"'+str(user_girl_list['user_id'])+'"'+';'
        cur.execute(sql)
        user_girl_list = cur.fetchall()
        #女の子のlistが取れる
        user_girl_list=json.dumps(user_girl_list, ensure_ascii=False)
        print(user_girl_list)
        cur.close()
        conn.close()
    else:
        user_girl_list = 'data ng'
    return user_girl_list

@app.route('/girls_name', methods=['GET', 'POST'])
def girls_name():
    print(request)
    if request.method == 'POST':
        user_girl_list = request.json
        #SQLを叩く
        conn = test()
        cur = conn.cursor(dictionary=True)
        sql = 'select * from list_girl WHERE id ='+'"'+str(user_girl_list['girls_id'])+'"'+';'
        cur.execute(sql)
        user_girl_list = cur.fetchall()
        #女の子のlistが取れる
        user_girl_name=json.dumps(user_girl_list, ensure_ascii=False)
        print(user_girl_name)
        cur.close()
        conn.close()
    else:
        user_girl_name = 'data ng'
    return user_girl_name

@app.route('/girls_suggest_score', methods=['GET', 'POST'])
def girls_suggest():
    if request.method == 'POST':
        user_girl_score = request.json
        print(user_girl_score)
        print(user_girl_score['user_id'])
        #SQLを叩く
        conn = test()
        cur = conn.cursor(dictionary=True)
        sql = 'select * from total_score_girls WHERE user_id='+'"'+str(user_girl_score['user_id'])+'"'+'and girls_id='+str(user_girl_score['girls_id'])+';'
        cur.execute(sql)
        user_girl_score = cur.fetchall()
        user_girl_score = json.dumps(user_girl_score, ensure_ascii=False)
        print(user_girl_score)
        cur.close()
        conn.close()
    else:
        user_girl_score = 'data ng'
    return user_girl_score

if __name__ == "__main__":
    # webサーバー立ち上げ
    '''
    どうしてここをコメントアウトしているか考えてください！
    '''
    #開発用
    app.run(host='0.0.0.0',debug=True,port=5002)
    #app.run()
