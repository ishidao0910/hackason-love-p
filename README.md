# Hackathon_v12
## 技術スタック
<img width="791" alt="スクリーンショット 2021-12-20 21 12 35" src="https://user-images.githubusercontent.com/45090872/146765563-84b5cebf-fc0b-441b-bf36-aa880ab812a3.png">

## アーキテクチャー図
<img width="1037" alt="スクリーンショット 2022-03-06 17 14 04" src="https://user-images.githubusercontent.com/73809994/156914895-cbec2394-85f6-48cc-ac60-a202120dd7ba.png">


## 開発環境
### node.js

production APIに叩く場合

```
node-dev s_app_production.js
```

port:8081が埋まっている時の対処
```
lsof -i :8081
kill -9 PID
```

DEV APIに叩く場合

```
node-dev s_app_dev.js
```
### flask(API)
```
python line_analysis.py
python user.py
python add_db_instart.py
```
### docker
### マイクロサービスで立ち上がるもの(フロントを含む)
* user.py
* add_db_instart.py
* app.js（フロント）

```
$ cd API
$ docker-compose up -d
```
node.jsアクセス<br>
http://localhost:82
### マイクロサービスで立ち上がるもの(APIのみ)
* user.py
* add_db_instart.py

```
$ cd API
$ docker-compose -f docker-compose-1.yml up -d
```
### マイクロサービスに必要なDB構成

プロダクション同様にマイクロサービス立ち上げ時にDBを作る<br>
133.125.60.167:3307
>loveP参照


