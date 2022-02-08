# import mysql.connector
from flask import Flask, jsonify, request
import mysql.connector as db

# def test():
#     conn = db.connect(
#             host="db_server",
#             port=3306,
#             user="root",#ユーザidの記入
#             password="pass",#パスワードの記入
#             database="loveP"#データベースの名前を記入
#         )
#     return conn

def test():
    conn = db.connect(
            host="133.125.60.167",
            port=3307,
            user="root",#ユーザidの記入
            password="pass",#パスワードの記入
            database="loveP"#データベースの名前を記入
        )
    return conn

app = Flask(__name__, static_folder='static')
app.config['JSON_AS_ASCII'] = False

@app.route('/', methods=['GET', 'POST'])
def add_girl():
    if request.method == 'POST':
        conn=test()
        print(conn)
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
        print(conn)
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

@app.route('/user_registration', methods=['GET', 'POST'])
def user_registration():
    if request.method == 'POST':
        conn=test()
        print(conn)
        cursor = conn.cursor()
        user_registration = request.form
        user_id = user_registration['user_id']
        u_pass = user_registration['user_pass']
        email = user_registration['user_email']
        #ここで一度重複チェックを行う必要がある.
        sql = "INSERT INTO user (user_id , user_name, display_name, pass, email,flag,profile) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        data = [(None, str(user_id),None,str(u_pass),str(email),0,None)]
        cursor.executemany(sql, data)
        conn.commit()
        cursor.close()
        #ここでtokenを発行してreturnで返す
        #ここでもう一回書き込みを行う.
        #tokenを取得してから
        return 'data OK'
    else:
        conn=test()
        print(conn)
        return 'data NG'


if __name__ == "__main__":
    # webサーバー立ち上げ
    '''
    どうしてここをコメントアウトしているか考えてください！
    '''
    #開発用
    app.run(host='0.0.0.0',debug=True,port=5001)
    # app.run(host='localhost',debug=True,port=5001)
    #app.run()
