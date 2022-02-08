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

# def test():
#     conn = db.connect(
#             host="",
#             port=3307,
#             user="root",#ユーザidの記入
#             password="pass",#パスワードの記入
#             database="loveP"#データベースの名前を記入
#         )
#     return conn

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
        dic =  {"user_id" : user_information[1] ,"display_name" : user_information[2], "user_email" : user_information[4],"img" : user_information[7],'style':user_information[9]}
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

@app.route('/get_user_name', methods=['GET', 'POST'])
def get_user_name():
    if request.method == 'POST':
        user_info = request.json
        user_name=user_info['user_name']
        user_email=user_info['user_email']
        conn = test()
        cur = conn.cursor(dictionary=True)
        print(user_name)
        print(user_email)
        sql = 'select * from user WHERE user_name='+'"'+str(user_name)+'"'+';'
        cur.execute(sql)
        user_name_info = cur.fetchall()
        cur.close()
        conn.close()
        print(len(user_name_info))
        if len(user_name_info)!=0:
            return '1'
        else:
            conn = test()
            cur = conn.cursor(dictionary=True)
            sql = 'select * from user WHERE email='+'"'+str(user_email)+'"'+';'
            cur.execute(sql)
            user_email_info = cur.fetchall()
            cur.close()
            conn.close()
            if len(user_email_info)!=0:
                return '2'
            else:
                return "0"
    else:
        return 'no data'
    

@app.route('/token', methods=['GET', 'POST'])
def token():
    if request.method == 'POST':
        conn = test()
        cur = conn.cursor(dictionary=True)
        user_info = request.json
        token=user_info['token']
        sql = 'select * from user_a WHERE user_url ='+'"'+str(token)+'"'+';'
        cur.execute(sql)
        user_token= cur.fetchall()
        cur.close()
        conn.close()
        # print(list(user_token))
        if len(user_token)==0:
            return '1'
        else:
            qq=list(user_token)
            print(qq[0]['user_name'])
            return str(qq[0]['user_name'])
    else:
        return 'no data'

@app.route('/user_ans_flag', methods=['GET', 'POST'])
def user_ans_flag():
    if request.method == 'POST':
        conn = test()
        cur = conn.cursor(dictionary=True)
        user_info = request.json
        token=user_info['user_id']
        sql = 'select ans_flag from user WHERE user_id ='+'"'+str(token)+'"'+';'
        cur.execute(sql)
        user_token= cur.fetchall()
        cur.close()
        conn.close()
        dic =  {"ans_flag" :user_token[0]['ans_flag']}
        print(dic)
        return dic
    else:
        return 'no data'

@app.route('/girls_id_count', methods=['GET', 'POST'])
def girls_id_count():
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
        if len(user_girl_name)>0:
            return '1'
        else:
            return '0'
    else:
        user_girl_name = '0'
    return user_girl_name

@app.route('/get_girls_id_img', methods=['GET', 'POST'])
def get_girls_id_img():
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
        dic =  {"girls_img" :user_girl_list[0]['img']}
        return dic
    else:
        user_girl_name = '0'
    return user_girl_name

@app.route('/get_girls_suggest', methods=['GET', 'POST'])
def get_girls_suggest():
    print(request)
    if request.method == 'POST':
        user_girl_list = request.json
        #SQLを叩く
        conn = test()
        cur = conn.cursor(dictionary=True)
        sql = 'select * from total_score_girls WHERE girls_id ='+'"'+str(user_girl_list['girls_id'])+'"'+';'
        cur.execute(sql)
        user_girl_list = cur.fetchall()
        #女の子のlistが取れる
        print(user_girl_list)
        user_girl_name=json.dumps(user_girl_list, ensure_ascii=False)
        cur.close()
        conn.close()
        return user_girl_name
    else:
        user_girl_name = '0'
    return user_girl_name

@app.route('/get_girls_suggest_contents', methods=['GET', 'POST'])
def get_girls_suggest_contents():
    print(request)
    if request.method == 'POST':
        user_girl_list = request.json
        print(user_girl_list)
        #SQLを叩く
        conn = test()
        cur = conn.cursor(dictionary=True)
        sql = '('+'SELECT * FROM total_score_girls WHERE user_id ='+'"'+str(user_girl_list['user_id'])+'"'+ 'and girls_id ='+'"'+str(user_girl_list['girls_id'])+'"'+'and slag = '+ '"'+str(user_girl_list['slag'])+'"'+')'
        # sql = '('+'SELECT * FROM total_score_girls WHERE user_id ='+'"'+str(user_girl_list['user_id'])+'"'+ 'and girls_id ='+'"'+str(user_girl_list['girls_id'])+'"'+'and slag = '+ '"'+str(user_girl_list['slag'])+'"'+"ORDER BY slag DESC"+')'

        cur.execute(sql)
        user_girl_list = cur.fetchall()
        user_girl_name=json.dumps(user_girl_list, ensure_ascii=False)
        cur.close()
        conn.close()
        return user_girl_name
    else:
        return '0'

@app.route('/score_transition', methods=['GET', 'POST'])
def score_transition():
    print(request)
    if request.method == 'POST':
        user_girl_list = request.json
        print(user_girl_list)
        #SQLを叩く
        conn = test()
        cur = conn.cursor(dictionary=True)
        # sql = '('+'SELECT * FROM total_score_girls WHERE user_id ='+'"'+str(user_girl_list['user_id'])+'"'+ 'and girls_id ='+'"'+str(user_girl_list['girls_id'])+'"'+'and slag = '+ '"'+str(user_girl_list['slag'])+'"'+')'
        sql = '('+'SELECT date,score FROM total_score_girls WHERE user_id ='+'"'+str(user_girl_list['user_id'])+'"'+ 'and girls_id ='+'"'+str(user_girl_list['girls_id'])+'"'+" ORDER BY id DESC limit 5"+')'
        cur.execute(sql)
        user_girl_list = cur.fetchall()
        user_girl_name=json.dumps(user_girl_list, ensure_ascii=False)
        cur.close()
        conn.close()
        return user_girl_name
    else:
        return '0'

if __name__ == "__main__":
    # webサーバー立ち上げ
    '''
    どうしてここをコメントアウトしているか考えてください!
    '''
    #開発用
    app.run(host='0.0.0.0',debug=True,port=5002)
    # app.run(host='localhost',debug=True,port=5002)
    #app.run()
