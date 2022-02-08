'use strict';
//モジュール読み込み
var express = require('express');
var { connect } = require('http2');
var passport = require('passport');
var LocalStrategy = require('passport-local').Strategy;
var session = require('express-session');
var cookieParser = require("cookie-parser");
var request = require('request');
var expressSanitizer = require('express-sanitizer');
var sgMail = require('@sendgrid/mail');
const multer = require('multer')
const upload = multer({ dest: 'uploads/' })
var app = express();
var bodyParser = require('body-parser');
app.use(bodyParser.urlencoded({ extended: true }));
require('dotenv').config();

app.use(express.static('public'))
var user_project_flag=0

//定義
app.set('view engine', 'ejs');
app.use(session({
  secret: 'test',
  name:'test',
  cookie:{
    httpOnly: false,
    secure: false,
    }
  }));

//TODO:本番運用をするときはセキュリティ周りの設定を行う必要あり
//宣言周り
app.use(expressSanitizer());

//順番を間違えるとログイン認証がされない
app.use(passport.initialize());

app.use(passport.session());

app.use(cookieParser());

require('date-utils');

// 8081番ポートで待ちうける
const PORT = 8081;
const HOST = '0.0.0.0';
app.listen(PORT, HOST);
console.log(`Running on http://${HOST}:${PORT}`);

passport.serializeUser(function(username, done) {
  done(null, username);
});
passport.deserializeUser(function (username, done) {
  done(null, username);
});

//ログイン周り
passport.use(new LocalStrategy({
  usernameField: "username",
  passwordField: "password",
},
  function(username, password, done){
    var options1 = {
      uri: "http://localhost:82/web2",
      headers: {
        "Content-type": "application/json",
      },
      json: {
        "user_name": username,
        "pass": password
      }
    };
    request.post(options1, function(error, response, body){
      console.log(body.flag)
      if (body.flag=='true'){
        return done(null, body.login_user);
      }else{
        return done(null, false);
      }
    });
}));


//メインページ
  app.get('/', (req,res) => {
    var fl = 0
    var a=''
    console.log(req.isAuthenticated())
    if (req.isAuthenticated()==true){
      fl=1
      res.render("index", {fl,a});
    }else{
      res.render("index", {fl,a});
    }
  });

//ログアウトページ
app.get('/logout', function(req, res){
  req.logout();
  //ログインページに戻る
  res.redirect('/')
});

app.get('/girls/:user_id/:girls_id', (req,res) => {
  if (req.isAuthenticated()==true){
    if(req.params.user_id==req.user){
    var options1 = {
      uri: "http://localhost:82/web2/girls_suggest_score",
      headers: {
        "Content-type": "application/json",
      },
      json: {
        "user_id": req.user,
        "girls_id": req.params.girls_id
      }
    };
    var options = {
      uri: "http://localhost:82/web2/girls_name",
      headers: {
        "Content-type": "application/json",
      },
      json: {
        "girls_id": req.params.girls_id
      }
    };
    request.post(options1, function(error1, response1, body){
      request.post(options, function(error, response, body1){
      console.log(body)
      var girls_id = req.params.girls_id
      //bodyで取れる情報は女の子の基本情報
      res.render("girls", {body,body1,girls_id});
  })
})
}else{
  //エラーページに飛ばすけどまだエラーページがない
}
}else{
  res.redirect('/login')
}
});


//mypage
app.get('/mypage', (req,res) => {
  console.log(req.user)
  if (req.isAuthenticated()==true){
  var options1 = {
    uri: "http://localhost:82/web2/user_information",
    headers: {
      "Content-type": "application/json",
    },
    json: {
      "user_id": req.user
    }
  };
  var options2 = {
    uri: "http://localhost:82/web2/girls_list",
    headers: {
      "Content-type": "application/json",
    },
    json: {
      "user_id": req.user
    }
  };
  request.post(options1, function(error, response, body){
    console.log(body)
    request.post(options2, function(error1, response1, body1){
    if (body==undefined){
        body=''
    }
    console.log(body1)
    res.render("mypage", {body,body1});
    })
  })
}else{
  res.redirect('/login')
}
});

//分析ページ
app.get('/analysis/:girls_id', function(req, res){
    var options2 = {
      uri: "http://localhost:82/web2/girls_name",
      headers: {
        "Content-type": "application/json",
      },
      json: {
        "girls_id": req.params.girls_id
      }
    };
    
    request.post(options2, function(error1, response1, body1){
    if (req.isAuthenticated()==true){
    console.log(body1)
    var user_name=body1[0].user_gn
    res.render("analysis", {user_name});
    }else{
    res.redirect('/')
    }
  })
});

//データの追加
app.get('/add_girl', function(req, res){
  if (req.isAuthenticated()==true){
  res.render("add_girl", {});
  }else{
  res.redirect('/')
  }
});

app.post('/add_girl', function(req, res){
  if (req.isAuthenticated()==true){
    console.log(req.body)
    var girl_name = req.body.name
    //ここでAPIに送る処理を書く
    var options = {
      uri: "http://localhost:82/web1",
      headers: {
        "Content-type": "application/json",
      },
      form: {
        "user_id":req.user,
        "girls_name": girl_name

      }
    };
    console.log(options)
    request.post(options, function(error1, response1, body1){
    res.redirect('/mypage')
    })
  }else{
    //エラーページ
  }
});

//プロフィール編集
app.get('/profile_edit', function(req, res){
    //ここでAPIに送る処理を書く
    var options = {
      uri: "http://localhost:82/web2/user_information",
      headers: {
        "Content-type": "application/json",
      },
      json: {
        "user_id": req.user
      }
    };
  if (req.isAuthenticated()==true){
  request.post(options, function(error1, response1, body1){
  console.log(body1)
  res.render("profile_edit", {body1});
  });
  }else{
  res.redirect('/')
  }
});

//TODO:バリデーションチェックを入れた方がいい
app.post('/profile_edit', function(req, res){
  if (req.isAuthenticated()==true){
    //ここでAPIに送る処理を書く
    var options = {
      uri: "http://localhost:82/web2",
      headers: {
        "Content-type": "application/json",
      },
      form: {
        "display_name":req.body.display_name,
        "user_id": req.body.user_id,
        "user_email":req.body.user_email
      }
    };
    console.log('---------')
    console.log(options)
    console.log('---------')
    request.post(options, function(error1, response1, body1){
    res.redirect('/mypage')
    })
  }else{
    //エラーページ
  }
});


//分析部分
app.post('/suggestion', upload.any(), (req, res, next) => {
  const fs = require('fs');
  let text = fs.readFileSync('uploads/'+req.files[0].filename, 'utf-8');
  var a='uploads/'+req.files[0].filename
  var text1 = fs.readFileSync(a, 'utf8');
  //テキストをpythonに送る。
  var options = {
    uri: "http://localhost:82/web3",
    headers: {
      "Content-type": "text/csv",
    },
    form: {
      text1
    }
  };
  request.post(options, function(error, response, body){
    console.log(body)
    //ここで一時保存したファイルを消す
    if (body=='not analytics'){
      a=body
      res.render("index", {});
    }else{
    fs.unlinkSync(a);
    console.log(body)
    body = JSON.parse(body);
    //取得したjson(str)をlordする必要がある
    console.log(body[0])
    console.log(body[1])
  //TODO:一時ファイルを消す処理が入る
  var s1_user=body[0]
  var s2_user=body[1]
  res.render("suggestion1", {s1_user,s2_user});
  }
  });
  });

//ログイン
app.get('/login', (req,res) => {
  if (req.isAuthenticated()==true){
    res.redirect('/mypage')
  }else{
    res.render("login", {});
  }
});

//pass login からpostされたときにする処理部分
app.post('/login', passport.authenticate('local', {
        failureRedirect: '/login',
        session: true
    }),
    function(req, res){
    res.redirect('/mypage')
    });
