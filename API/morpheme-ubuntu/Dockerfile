FROM ubuntu:20.04

# 日本設定
ENV TZ Asia/Tokyo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
ENV LANG ja_JP.UTF-8

# パッケージインストール
RUN apt update -yqq && \
    apt install -y --no-install-recommends \
    build-essential curl ca-certificates \
    file git locales sudo \
    mecab libmecab-dev mecab-ipadic-utf8 && \
    locale-gen ja_JP.UTF-8 && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

# mecab-ipadic-neologdインストール
WORKDIR /tmp
RUN git clone --depth 1 https://github.com/neologd/mecab-ipadic-neologd.git && \
    ./mecab-ipadic-neologd/bin/install-mecab-ipadic-neologd -n -y && \
    sudo mv /usr/lib/x86_64-linux-gnu/mecab/dic/mecab-ipadic-neologd /var/lib/mecab/dic/ && \
    sed -i 's/debian/mecab-ipadic-neologd/' /etc/mecabrc && \
    rm -rf ./mecab-ipadic-neologd && \
    echo "完了"