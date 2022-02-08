from flask import Flask, jsonify, request
import json
import pandas

def get_quadrant(inti_score, relat_score):
    """
    4象限に分ける関数。
    inti_score,　relat_scoreがそれぞれ、
    ++ : 1象限
    +- : 2象限
    -+ : 3象限
    -- : 4象限
    (0は計算上あり得ないので考慮しない)
    param:
        inti_score : 親密性回避スコア
        relat_score : 関係不安スコア
        
    output:
        quadrant : 4象限のどこに位置するか
    """
    
    if (inti_score > 0) & (relat_score > 0):
        test=1
    elif (inti_score > 0) & (relat_score < 0):
        test=2
    elif (inti_score < 0) & (relat_score > 0):
        test=3
    elif (inti_score < 0) & (relat_score < 0):
        test=4
    return test

def get_suggest_type(quadrant):
    if quadrant == 1:
        return "とらわれ型"
    elif quadrant == 2:
        return "回避型"
    elif quadrant == 3:
        return "安定型"
    elif quadrant == 4:
        return "恐怖型"
    else:
        return "NO ４象限"

def get_suggest(quadrant):
    if quadrant == 1:
        return "相手に執着する傾向があります"
    elif quadrant == 2:
        return "相手を好きになるのを怖がる必要があります"
    elif quadrant == 3:
        return "相手との関係を良好に築ける傾向があります"
    elif quadrant == 4:
        return "相手に嫌われるのを恐れがちな傾向があります"
    else:
        return "NO ４象限"

app = Flask(__name__, static_folder='static')
app.config['JSON_AS_ASCII'] = False

@app.route('/', methods=['GET', 'POST'])
def que():
    if request.method == 'POST':
        ans_list = []
        intimacy_avoidance = float('0.00')
        relationship_insecurity = float('0.00')
        ans_info = request.json
        df_s = ans_info['ans_info']
        for val in df_s.values():
            ans_list.append(val)
        print(ans_list)
        ans_ans_list=[0.77,0.76,0.76,0.73,0.72,0.71,0.69,0.67,0.66,0.66,0.63,0.57,0.54,0.5,0.48,-0.08,0.19,0.1,0.1,-0.25,-0.19,-0.16,0.01,0.16,0.15,-0.18,-0.02,0.2,0.32,-0.28]
        ans_ans_list1 = [0.13,0.02,-0.04,0.12,0.04,-0.07,0.12,0.11,-0.31,-0.08,0.03,-0.02,-0.04,0.15,-0.24,0.82,0.72,0.71,0.69,0.69,0.69,0.62,0.61,0.6,0.58,0.58,0.48,0.47,0.44,0.4]
        for i in range(len(ans_list)):
            print(i)
            if ans_list[i]=='+':
                intimacy_avoidance=intimacy_avoidance+ans_ans_list[i]
                relationship_insecurity=relationship_insecurity+ans_ans_list1[i]
            else:
                intimacy_avoidance=intimacy_avoidance-ans_ans_list[i]
                relationship_insecurity=relationship_insecurity-ans_ans_list1[i]
        print(intimacy_avoidance)
        print(relationship_insecurity)
        quadrant=0
        quadrant = get_quadrant(int(intimacy_avoidance), int(relationship_insecurity))
        print(quadrant)
        return str(quadrant)
    else:
        return 'no data'

@app.route('/style', methods=['GET', 'POST'])
def style():
    if request.method == 'POST':
        style_num = request.json
        # print("style : ", style_num['style'])
        # print("type style", type(style_num['style']))
        style = get_suggest_type(style_num['style'])
        print("love style : ", style)
        style_text = get_suggest(style_num['style'])
        print("tendency : ", style_text)
        dic = {"style":style, "style_text":style_text}
        print("dic", dic)
        return dic
    else:
        return 'no data'

if __name__ == "__main__":
    # webサーバー立ち上げ
    '''
    どうしてここをコメントアウトしているか考えてください!
    '''
    #開発用
    app.run(host='0.0.0.0',debug=True,port=5004)
    # app.run(host='localhost',debug=True,port=5004)
    #app.run()
