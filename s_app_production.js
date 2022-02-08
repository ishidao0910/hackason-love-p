'use strict';
//モジュール読み込み
var express = require('express');
var passport = require('passport');
var LocalStrategy = require('passport-local').Strategy;
var session = require('express-session');
var cookieParser = require("cookie-parser");
var request = require('request');
var expressSanitizer = require('express-sanitizer');
const multer = require('multer')
const upload = multer({ dest: 'uploads/' })
var app = express();
var bodyParser = require('body-parser');

app.use(bodyParser.urlencoded({ extended: true }));
require('dotenv').config();
require('date-utils');
app.use(express.static('public'))

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

//関数一覧
function fn2(test) {
  /*
    ここの関数では, userがアンケートを実施しているかどうかを
    確認するための関数
  */
    var options = {
      uri: "http://133.125.60.167:82/web2/user_ans_flag",
      // uri: "http://192.168.10.3:5002/user_ans_flag",
      headers: {
        "Content-type": "application/json",
      },
      json: {
        'user_id':test
      }
    };
    request.post(options, function(error, response, body){
      global.test1 = body.ans_flag
    })
    return global.test1
}

//ログイン周り
passport.use(new LocalStrategy({
  usernameField: "username",
  passwordField: "password",
},
  function(username, password, done){
    var options1 = {
      uri: "http://133.125.60.167:82/web2",
      headers: {
        "Content-type": "application/json",
      },
      json: {
        "user_name": username,
        "pass": password
      }
    };
    request.post(options1, function(error, response, body){
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
    if (req.isAuthenticated()==true){
      var an_flag=fn2(req.user)
      console.log(an_flag)
      if(an_flag==0){
        res.redirect('/questionnaire')
      }else{
      fl=1
      res.render("index", {fl,a});
    }
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
      var options4 = {
        uri: "http://133.125.60.167:82/web2/score_transition",
        headers: {
          "Content-type": "application/json",
        },
        json: {
          "user_id": req.user,
          "girls_id": req.params.girls_id
        }
      };
      var options3 = {
        uri: "http://133.125.60.167:82/web2/get_girls_suggest",
        headers: {
          "Content-type": "application/json",
        },
        json: {
          "girls_id": req.params.girls_id
        }
      };
    var options1 = {
      uri: "http://133.125.60.167:82/web2/girls_suggest_score",
      headers: {
        "Content-type": "application/json",
      },
      json: {
        "user_id": req.user,
        "girls_id": req.params.girls_id
      }
    };
    var options = {
      uri: "http://133.125.60.167:82/web2/girls_name",
      headers: {
        "Content-type": "application/json",
      },
      json: {
        "girls_id": req.params.girls_id
      }
    };
    request.post(options4, function(error4, response4, body4){
      console.log(body4)
    request.post(options1, function(error1, response1, body){
      request.post(options, function(error, response, body1){
        request.post(options3, function(error3, response3, body3){
      // console.log(body)
      var girls_id = req.params.girls_id
      //bodyで取れる情報は女の子の基本情報
      res.render("girls", {body,body1,girls_id,body3,body4});
    })
    })
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
  if (req.isAuthenticated()==true){
    console.log('user:'+req.user)
    var options3 = {
      uri: "http://133.125.60.167:82/web2/user_ans_flag",
      // uri: "http://192.168.10.3:5002/user_ans_flag",
      headers: {
        "Content-type": "application/json",
      },
      json: {
        'user_id':req.user
      }
    };
    request.post(options3, function(error, response, body3){
      console.log('OK')
      var test2 =1
      test2 = body3.ans_flag
      console.log('user::'+req.user)
      console.log('test:'+test2)
    if(test2==0){
      console.log('test1:'+test2)
      res.redirect('/questionnaire')
    }else{
  var options1 = {
    uri: "http://133.125.60.167:82/web2/user_information",
    headers: {
      "Content-type": "application/json",
    },
    json: {
      "user_id": req.user
    }
  };
  var options2 = {
    uri: "http://133.125.60.167:82/web2/girls_list",
    headers: {
      "Content-type": "application/json",
    },
    json: {
      "user_id": req.user
    }
  };
  request.post(options1, function(error, response, body){
    var options3 = {
      uri: "http://133.125.60.167:82/web4/style",
      // uri: "http://0.0.0.0:5004//style",
      headers: {
        "Content-type": "application/json",
      },
      json: {
        "style": body.style
      }
    };
    request.post(options3, function(error3, response3, body3){
      console.log(body3)
    request.post(options2, function(error1, response1, body1){
    if (body==undefined){
        body=''
    }
    res.render("mypage", {body,body1,body3});
      })
    })
  })
}
})
}else{
  res.redirect('/login')
}
});

//分析ページ
app.get('/analysis/:girls_id', function(req, res){
    var options2 = {
      uri: "http://133.125.60.167:82/web2/girls_name",
      headers: {
        "Content-type": "application/json",
      },
      json: {
        "girls_id": req.params.girls_id
      }
    };
    
    request.post(options2, function(error1, response1, body1){
    if (req.isAuthenticated()==true){
    var user_name=body1[0].user_gn
    var aaaa=''
    var girls_id =req.params.girls_id
    res.render("analysis", {user_name,girls_id,aaaa});
    }else{
    res.redirect('/')
    }
  })
});

//データの追加
app.get('/add_girl', function(req, res){
  if (req.isAuthenticated()==true){
    var options10 = {
      uri: "http://133.125.60.167:82/web2/user_ans_flag",
      // uri: "http://192.168.10.3:5002/user_ans_flag",
      headers: {
        "Content-type": "application/json",
      },
      json: {
        'user_id':req.user
      }
    };
    request.post(options10, function(error, response, body3){
      console.log('OK')
      var test2 =1
      test2 = body3.ans_flag
      console.log('user::'+req.user)
      console.log('test:'+test2)
    if(test2==0){
      console.log('test1:'+test2)
      res.redirect('/questionnaire')
    }else{
  var test = ''
  res.render("add_girl", {test});
  }
  });
}else{
  res.redirect('/')
  }
});

app.post('/add_girl', upload.single('file1') , function(req, res){
  if (req.isAuthenticated()==true){
    console.log()
    if (req.body.name!=''){
    var girl_name = req.body.name
    //ここでAPIに送る処理を書く
    console.log(req.file)
    if (req.file!=undefined){
      let fs = require('fs');
      fs.readFile(req.file.path, function( err, content ) {
        if( err ) {
          console.error(err);
        }else{
          if(req.file.mimetype=='image/png'){
            /* Base64変換 */
            var base64_data = content.toString('base64');
            var data_trpe = 'image/png'

            }else if(req.file.mimetype=='image/jpeg'){
            /* Base64変換 */
            var base64_data = content.toString('base64');
            var data_trpe = 'image/jpeg'
            }else{
              var base64_data=undefined
            }
      var options = {
        // uri: "http://localhost:5001/profile_edit_2" ,
        uri: "http://133.125.60.167:82/web1/profile_edit_2",
        headers: {
          "Content-type": data_trpe,
        },
        form: {
          "image_data":base64_data,
          "user_id":req.user,
          "girls_name": girl_name
        }
      };
    //ここでpostする(画像が入っている場合)
    request.post(options, function(error1, response1, body1){
      fs.unlinkSync(req.file.path)
      res.redirect('/mypage')
            })
          }
        })
      }else{
        var test = '女の子の画像を入れないと追加できません'
        res.render("add_girl", {test});
      }
    }
  }
});

//プロフィール編集
app.get('/profile_edit', function(req, res){
    //ここでAPIに送る処理を書く
    var options = {
      uri: "http://133.125.60.167:82/web2/user_information",
      headers: {
        "Content-type": "application/json",
      },
      json: {
        "user_id": req.user
      }
    };
  if (req.isAuthenticated()==true){
    var options10 = {
      uri: "http://133.125.60.167:82/web2/user_ans_flag",
      // uri: "http://192.168.10.3:5002/user_ans_flag",
      headers: {
        "Content-type": "application/json",
      },
      json: {
        'user_id':req.user
      }
    };
    request.post(options10, function(error, response, body3){
      console.log('OK')
      var test2 =1
      test2 = body3.ans_flag
      console.log('user::'+req.user)
      console.log('test:'+test2)
    if(test2==0){
      console.log('test1:'+test2)
      res.redirect('/questionnaire')
      
    }else{
  request.post(options, function(error1, response1, body1){
  console.log(body1)
  res.render("profile_edit", {body1});
  });
  }
});
  }else{
  res.redirect('/')
  }
  
});

//TODO:バリデーションチェックを入れた方がいい
app.post('/profile_edit', upload.single('file1'), (req, res) => {
  if (req.isAuthenticated()==true){
    if(fn2(req.user)==0){
      res.redirect('/questionnaire')
    }else{
    //データがnullでは受け付けない
    if((req.body.user_id=='')|(req.body.user_email=='')){
      res.redirect('/profile_edit')
    }else{
    //ここでAPIに送る処理を書く
    console.log(req.file)
    if (req.file!=undefined){
      let fs = require('fs');
      fs.readFile(req.file.path, function( err, content ) {
      if( err ) {
        console.error(err);
      }
      else {
      if(req.file.mimetype=='image/png'){
      /* Base64変換 */
      var base64_data = content.toString('base64');
      var data_trpe = 'image/png'
      // fs.unlinkSync(req.file.path)
      }else{
      /* Base64変換 */
      var base64_data = content.toString('base64');
      var data_trpe = 'image/jpeg'
      }
      }
      var options1 = {
        // uri: "http://localhost:5001/profile_edit_1" ,
        uri: "http://133.125.60.167:82/web1/profile_edit_1",
        headers: {
          "Content-type": data_trpe,
        },
        form: {
          "image_data":base64_data,
          "display_name":req.body.display_name,
          "user_id": req.user,
          "user_email":req.body.user_email,
          "user_name":req.body.user_name
        }
      };
    request.post(options1, function(error1, response1, body1){
      console.log(error1)
      res.redirect('/mypage')
    });
    });
    }else{
    var options = {
      // uri: "http://192.168.10.3:5001/profile_edit" ,
      uri: "http://133.125.60.167:82/web1/profile_edit",
      headers: {
        "Content-type": "application/json",
      },
      form: {
        "display_name":req.body.display_name,
        "user_id": req.user,
        "user_email":req.body.user_email,
        "user_name":req.body.user_name
      }
    };
    request.post(options, function(error1, response1, body1){
    res.redirect('/mypage')
    })
  }
  }
  }
  }else{
    //エラーページ
  }
});

//分析部分
app.post('/suggestion/:id', upload.any(), (req, res, next) => {
  /*
  :id⇨girls_id
  データを保存する為の前処理
  */
  var options1 = {
    // uri: "http://192.168.10.3:5001/girls_id_count ,
    uri: "http://133.125.60.167:82/web2/girls_id_count",
    headers: {
      "Content-type": "application/json",
    },
    json: {
      "girls_id":req.params.id
    }
  };
  request.post(options1, function(error1, response1, body1){
  console.log(body1)
  if (body1==1){
  const fs = require('fs');
  let text = fs.readFileSync('uploads/'+req.files[0].filename, 'utf-8');
  var a='uploads/'+req.files[0].filename
  var text1 = fs.readFileSync(a, 'utf8');
  //テキストをpythonに送る。
  var options = {
    uri: "http://133.125.60.167:82/web3",
    // uri: "http://0.0.0.0:5003/",
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
      var aaaa='このファイルは対応してません'
      var girls_id =req.params.id
      var options2 = {
        uri: "http://133.125.60.167:82/web2/girls_name",
        headers: {
          "Content-type": "application/json",
        },
        json: {
          "girls_id": req.params.id
        }
      };
      request.post(options2, function(error1, response1, body1){
        var user_name = body1[0].user_gn
      res.render("analysis", {aaaa,girls_id,user_name});
      })
    }else{
    fs.unlinkSync(a);
    console.log(body)
    body = JSON.parse(body);
    //取得したjson(str)をlordする必要がある
    console.log(body[0])
    console.log(body[1])
    console.log(body[2])
    console.log(body[3])
  //TODO:一時ファイルを消す処理が入る
  var s1_user=body[0]
  var s2_user=body[1]
  var s1_user_score=body[2]
  var s2_user_score=body[3]
  var s2_user_value=body[4]
  var total_s1_score = ((s1_user_score["is_mov"] + s1_user_score["is_pic"] + s1_user_score["is_stamp"] + s1_user_score["is_call"] + s1_user_score["call_time"] + s1_user_score["emoji_count"] + s1_user_score["is_thanks"] + s1_user_score["is_apology"] + s1_user_score["is_question"] + s1_user_score["is_complement"] + s1_user_score["is_affection"] + s1_user_score["words_count"] + s1_user_score["chat_count"] + s1_user_score["ave_response_mins"])*0.1)
  //ここで計算してください！
  /*
  ここでデータの書き込みを行う
  保存するデータ
  var s1_user
  var s2_user
  var s1_user_score
  var s2_user_score
  var s2_user_value
  */
  var options3 = {
    uri: "http://133.125.60.167:82/web1/suggest_push",
    // uri: "http://192.168.10.3:5001/suggest_push",
    headers: {
      "Content-type": "application/json",
    },
    json: {
      "user_id":req.user,
      "girls_id":req.params.id,
      "s1_user":s1_user,
      "s2_user":s2_user,
      "s1_user_score":s1_user_score,
      "s2_user_score":s2_user_score,
      "s2_user_value":s2_user_value,
      "score":total_s1_score
    }
  };
  request.post(options3, function(error3, response3, body3){
  })
  /*
  ここで女の子の画像を追加する
  */
  var options4 = {
    uri: "http://133.125.60.167:82/web2/get_girls_id_img",
    // uri: "http://192.168.10.3:5001/get_girls_id_img",
    headers: {
      "Content-type": "application/json",
    },
    json: {
      "girls_id":req.params.id
    }
  };
  request.post(options4, function(error4, response4, body4){
    console.log(body4.girls_img)
    var img= body4.girls_img
    console.log(s1_user)
    /*
    愛着スタイルの取得
     */
    var options6 = {
      uri: "http://133.125.60.167:82/web2/user_information",
      // uri: "http://localhost:5004/",
      headers: {
        "Content-type": "application/json",
      },
      json: {
        "user_id": req.user
      }
    };
    request.post(options6, function(error6, response6, body6){
    console.log('愛着スタイル:'+body6.style)
    /*
    愛着スタイルをもとに適切な計算
    */
    var options5 = {
      uri: "http://133.125.60.167:82/web3/style_suggest",
      // uri: "http://0.0.0.0:5003/style_suggest",
      headers: {
        "Content-type": "application/json",
      },
      json: {
        "style":body6.style,
        "user_id":req.user,
        "girls_id":req.params.id,
        "s1_user":s1_user,
        "s2_user":s2_user,
        "s1_user_score":s1_user_score,
        "s2_user_score":s2_user_score,
        "s2_user_value":s2_user_value,
        "score":total_s1_score
      }
    };
    request.post(options5, function(error5, response5, body5){
      console.log('愛着スタイル:'+body5["contents"])
      var suggest_contents = body5["contents"]
    /*
    ここで愛着スタイルの結果が出る.
    */
  res.render("suggestion1", {s1_user,s2_user, s1_user_score, s2_user_score, s2_user_value, img, total_s1_score, suggest_contents});
  })
  })
  })
  }
  });
  }
  else{
    //TODO:ここのurlは後で変更する.
    res.redirect('/mypage')
  }
  })
  });

//ログイン
app.get('/login', (req,res) => {
  if (req.isAuthenticated()==true){
    if(fn2(req.user)==0){
      res.redirect('/questionnaire')
    }else{
    res.redirect('/mypage')
  }
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
    if(fn2(req.user)==0){
      res.redirect('/questionnaire')
    }else{
      res.redirect('/mypage')
    }
    });

//sinup
//ログイン
app.get('/sinup', (req,res) => {
  var body=''
  if (req.isAuthenticated()==true){
    if(fn2(req.user)==0){
      res.redirect('/questionnaire')
    }else{
    res.redirect('/mypage')
  }
}else{
    res.render("sinup", {body});
  }
});

app.post('/sinup', function(req, res){
  if (req.isAuthenticated()!=true){
    //データがnullでは受け付けない
    if((req.body.email=='')|(req.body.username=='')|(req.body.password=='')){
      res.redirect('/sinup')
    }else{
    var body =0
    console.log(req.body.username)
    //重複がないか確認する
    var options = {
      uri: "http://133.125.60.167:82/web2/get_user_name",
      // uri: "http://localhost:5002/get_user_name",
      headers: {
        "Content-type": "application/json",
      },
      json: {
        "user_name": req.body.username,
        "user_email": req.body.email
      }
    };
    request.post(options, function(error, response, body){
    if (body==1){
      body='※このIDは使用されています'
      res.render("sinup", {body});
    }else if(body==2){
      body='※このemailは使用されています'
      res.render("sinup", {body});
    }else{
      //ここの処理で初めてDBに書き込みを行う
      var options1 = {
        uri: "http://133.125.60.167:82/web1/user_registration",
        // uri: "http://localhost:5001/user_registration",
        headers: {
          "Content-type": "application/json",
        },
        json: {
          "user_id": req.body.username,
          "user_email": req.body.email,
          "user_pass": req.body.password
        }
      };
      body=req.body.email
      request.post(options1, function(error1, response1, body1){
        res.render("email",{body});
          })
        }
      })
    }
  }
});

app.get('/sinup/:id', (req,res) => {
  var token_userl=req.params.id
  var options = {
    uri: "http://133.125.60.167:82/web2/token",
    // uri: "http://localhost:5002/token",
    headers: {
      "Content-type": "application/json",
    },
    json: {
      "token": token_userl
    }
  };
  request.post(options, function(error1, response1, body1){
      if(body1==1){
        res.redirect('/')
      }else{
        //ここadd_instartでflagを1に変える
        console.log(body1)
        var options = {
          uri: "http://133.125.60.167:82/web1/user_flag",
          // uri: "http://localhost:5001/user_flag",
          headers: {
            "Content-type": "application/json",
          },
          json: {
            "user_name": body1
          }
        };
        request.post(options, function(error2, response2, body2){
        res.redirect('/login')
        })
      }
      })
});

app.get('/questionnaire', (req,res) => {
  res.render("questionnaire", {});
});

app.post('/questionnaire', function(req, res){
  var options = {
    uri: "http://133.125.60.167:82/web4",
    // uri: "http://localhost:5004/",
    headers: {
      "Content-type": "application/json",
    },
    json: {
      "ans_info": req.body
    }
  };
  request.post(options, function(error, response, body){
  console.log(body)
  //ここで愛着スタイルが返ってくるから返ってきたらさらにDBに書き込みを行う
  var options1 = {
    uri: "http://133.125.60.167:82/web1/style",
    // uri: "http://localhost:5001/style",
    headers: {
      "Content-type": "application/json",
    },
    json: {
      "style": body,
      'username':req.user

    }
  };
  request.post(options1, function(error1, response1, body1){
  console.log(body1)
  res.redirect("/mypage")
  })
})
})

/*
過去データを取得して表示する機能
url /Past_suggestions
:id⇨user_id
:id1⇨girls_id
:id2⇨slag

EX)
/Past_suggestions/:id/:id1/:id2
*/
app.get('/test/:id/:id1/:id2', (req,res) => {
  if (req.isAuthenticated()==true){
    if(req.params.id==req.user){
      /*
      ここで該当のデータがあるかどうかをみる
      */
      var options = {
        uri: "http://133.125.60.167:82/web2/get_girls_suggest_contents",
        // uri: "http://192.168.10.3:5002/get_girls_suggest_contents",
        headers: {
          "Content-type": "application/json",
        },
        json: {
          'user_id': req.user,
          'girls_id':req.params.id1,
          'slag':req.params.id2

        }
      };
      request.post(options, function(error1, response1, body1){
      console.log('---')
      const s1_user = JSON.parse(body1[0].s1);
      console.log('---')
      const s2_user = JSON.parse(body1[0].s2);
      console.log('---')
      const s1_user_score = JSON.parse(body1[0].s1_score);
      console.log('---')
      const s2_user_score = JSON.parse(body1[0].s2_score);
      console.log('---')
      console.log(body1[0].s2_value)
      const s2_user_value = JSON.parse(body1[0].s2_value);
      var options4 = {
        uri: "http://133.125.60.167:82/web2/get_girls_id_img",
        // uri: "http://192.168.10.3:5001/get_girls_id_img",
        headers: {
          "Content-type": "application/json",
        },
        json: {
          "girls_id":req.params.id1
        }
      };
      request.post(options4, function(error4, response4, body4){
        console.log(body4.girls_img)
        var img= body4.girls_img
      res.render("suggestion2", {s1_user, s2_user, s1_user_score, s2_user_score, img,s2_user_value});
      // s1_user,s2_user, s1_user_score, s2_user_score, s2_user_value
      })
    })
    }else{
      res.redirect("/girls/"+req.params.id+'/'+req.params.id1)
    }
  }else{
    res.redirect("/login")
  }
});



