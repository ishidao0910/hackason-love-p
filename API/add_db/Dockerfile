# python v3.6 をベースにDockerイメージを作成
FROM python:3.8

# 作業ディレクトリを指定
WORKDIR /code

# カレントディレクトリのファイルをDockerコンテナの｢/app｣ ディレクトリにコピー
ADD . /code

# インストール
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y libgl1-mesa-dev
RUN pip install -r requirements.txt

# 外部に公開するポートを指定
EXPOSE 5001

# コンテナの実行コマンドを指定
CMD ["python", "code/add_db_instart.py"]