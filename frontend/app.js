// jshint esversion:6
if (process.env.NODE_ENV != 'production'){
    require('dotenv').config()
}

const express = require('express');
const bodyParser = require('body-parser');
const app = express();
const bcrypt = require('bcrypt');
const {request, response} = require("express");
const axios = require('axios');
const passport = require('passport')
const flash = require('express-flash')
const session = require('express-session');
const methodOverride = require('method-override');
const API = process.env.API;
const multer = require('multer'); // 用於處理檔案上傳的中間件
const FormData = require('form-data');
const fs = require('fs');

const storage = multer.memoryStorage(); // 將檔案暫存在內存中
const upload = multer({ storage: storage });

var priceTableJSON = require('./public/priceTable.json');
const pointRatio = priceTableJSON["點數"];
const dollorRatio = priceTableJSON["金額"];

const { log } = require('console');
const { start } = require('repl');
initializePassport(
    passport,
    async function(studentID){
        let user = null
        let config = {
          method: 'get',
          maxBodyLength: Infinity,
          headers: { }
        };
        
        await axios.request(config)
        .then((response) => {
            user = response.data[0]
        })
        .catch((error) => {
            user = null;
            console.log(error);
        });
        return user;
    }
);

app.set("view engine", "ejs");
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static('public', { 
    setHeaders: (res, path) => {
      if (path.endsWith('.js')) {
        res.setHeader('Content-Type', 'application/javascript');
      }
    }
}));
app.use(flash())
app.use(session({
    secret: process.env.SESSION_SECRET,
    resave: false,
    saveUninitialized: false,
    passReqToCallback: true,
    cookie: {
        maxAge: 24 * 60 * 60 * 1000 // 過期時間設定為 1 天
    }
}))
app.use(passport.initialize())
app.use(passport.session())
app.use(methodOverride('_method'))

app.get("/test", async function(req, res){
    
      let user = {
        "name": "User",
        "userID": 2,
        "balance": "1000",
        "studentID": "B123123123",
      }
      priceTable = JSON.parse(fs.readFileSync('./public/priceTable.json', 'utf8'));
      let printer = ['Printer1', 'Printer2', 'Printer3'];
    res.render('test', {printer : printer, studentID: 123, user:user });
});

app.get("/", checkAuthenticated, function (req, res) {
    res.redirect("/login");
});

/* Login */
app.get('/login' , function(req,res){
    req.session.regenerate(function(err) {
        if (err) {
            console.error('Error regenerating session:', err);
            return res.status(500).send('Server error');
        }
        req.session.user = { username: 'exampleUser' };
        res.render("login/Login", {});
    });
})

app.post('/login', checkNotAuthenticated, passport.authenticate('local', {
    badRequestMessage: '請輸入帳號密碼',
    successRedirect: '/navigate',
    failureRedirect: '/login',
    failureFlash: true
}))

app.delete('/logout', function(req, res, next){
    console.log('logout');
    req.session.destroy(err => {
        if (err) {
            console.error('Error destroying session:', err);
            return res.status(500).send('Server error');
        }
        res.redirect('/login');
    });
})

function checkAuthenticated(req, res, next){
    if (!checkLocalNetwork(req, res, next)){
        return res.redirect('/error/404');
    }
    if (req.isAuthenticated()){
        return next(); 
    }
    res.redirect('/login');
}

function checkLocalNetwork(req, res, next){
    const clientIP = req.headers['x-forwarded-for'] || req.ip;
    const ipv4Address = clientIP.includes('::ffff:') ? clientIP.split('::ffff:')[1] : clientIP;
    if (ipv4Address.startsWith("140.118.41")){
        return true;
    }
    else{
        return false
    }
}

function checkNotAuthenticated(req, res, next){
    if (!checkLocalNetwork(req, res, next)){
        return res.redirect('/error/404');
    }
    if (req.isAuthenticated()){
        return res.redirect('/admin');
    }
    next(); 
}

function checkUserRole(req, res, next) {
    if (req.isAuthenticated()) {
        if (req.user.permissionID == 1){
            res.redirect('/admin');
        }
        else if (req.user.permissionID == 2){
            res.redirect('/client');
        }
        else{
            res.redirect('/login');
        }
    } else {
      res.redirect('/login');
    }
  }  

function isAdmin(req, res, next){
    if (req.user.permissionID == 1){
        return next();
    }
    res.redirect('/client');
}

function isClient(req, res, next){
    if (req.user.permissionID == 2){
        return next();
    }
    res.redirect('/admin');
}

app.get('/navigate', checkUserRole, function(req, res){
});

/* Admin */
app.get("/admin", checkAuthenticated, isAdmin, function (req, res) {
    res.redirect("admin/account");
});

app.get("/admin/account", checkAuthenticated, isAdmin, async function (req, res){
    let accountData; // 全域變數
    let config = {
        method: 'get',
        maxBodyLength: Infinity,
        headers: { }
    };
    try {
        await axios.request(config)
        .then((response) => {
            accountData = response.data;
            res.render("admin/AccountView", { accounts: accountData , user: req.user});
        })
        .catch((error) => {
            console.log(error);
            res.render("errorView", { message: "很抱歉，伺服器出現錯誤。請洽維修人員(錯誤說明：request account error)"})
        });
    } catch (error) {
        console.error('Error:', error);
        res.render("errorView", { message: "很抱歉，伺服器出現錯誤。請洽維修人員(錯誤說明：account data error)"})
    }
});

app.get("/admin/usage", checkAuthenticated, isAdmin, async function (req, res){
    var usage;
    let config = {
        method: 'get',
        maxBodyLength: Infinity,
        headers: { }
    };
      
    await axios.request(config)
    .then((response) => {
        usage = response.data;
    })
    .catch((error) => {
        console.log(error);
    });

    sortedUsage = await sortingUsage(usage);
    res.render("admin/UsageView", {user: req.user, usage: sortedUsage});
});

app.get("/admin/statistics", checkAuthenticated, isAdmin, function (req, res){
    res.render("admin/StatisticsView", {user: req.user});
});

app.get("/admin/userEdit", checkAuthenticated, isAdmin, async function(req, res){
    let userID = req.query.id;
    let userData;

    let config = {
        method: 'get',
        maxBodyLength: Infinity,
        url: API + '/user/userID/' + userID,
        headers: { }
    };

    await axios.request(config)
        .then((response) => {
            userData = response.data[0];
        })
        .catch((error) => {
            console.log(error);
    });
    res.render('admin/AccountSettingView', {data: userData, user: req.user})

});

app.get("/admin/priceTableSetting", checkAuthenticated, isAdmin, async function(req, res){
    var priceTable = JSON.parse(fs.readFileSync('./public/priceTable.json', 'utf8'));
    res.render('admin/PriceTableSettingView', {user: req.user, priceTable: priceTable});
});

app.get("/admin/addUser", checkAuthenticated, isAdmin, function(req, res){
    res.render('admin/AddUserView', {user: req.user});
});

app.get("/admin/setBalance", checkAuthenticated, isAdmin, async function(req, res){
    res.render('admin/SetBalanceView', {user: req.user});
});

app.get("/admin/successful", checkAuthenticated, isAdmin, function(req, res){
    res.render('admin/SuccessfulView', {user: req.user});
})

app.get("/admin/failed", checkAuthenticated, isAdmin, function(req, res){
    res.render('admin/FailedView', {user: req.user});
})

app.post("/admin/setUser", checkAuthenticated, isAdmin, async function(req, res){
    let returnData = req.body;
    try{
        const rounds = bcrypt.getRounds(returnData.password)
        console.log("rounds: " + rounds);
    }
    catch{
        console.log("Hashing the password...");
        returnData.password = bcrypt.hashSync(returnData.password, 10);
    }
    await axios.put(API + '/user', returnData, {
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(response => {

        }).catch(error => {
        console.error(error);
    });
    res.redirect("/admin/account");
});

app.post("/admin/deleteUser", checkAuthenticated, isAdmin, async function(req, res){
    let id = req.body.userId;
    let data = '';

    let config = {
        method: 'delete',
        maxBodyLength: Infinity,
        url: url,
        headers: { },
        data : data
    };

    await axios.request(config)
    .then((response) => {
        console.log(JSON.stringify(response.data));
    })
    .catch((error) => {
        console.log(error);
    });
    res.redirect("/admin/account");
})

app.post("/admin/addUser", checkAuthenticated, isAdmin, function(req, res){
    let saltRounds = 10;
    req.body.password = bcrypt.hashSync(req.body.password, saltRounds);
    var data = JSON.stringify(req.body);
    console.log(data);

    let config = {
        method: 'post',
        maxBodyLength: Infinity,
        headers: { 
          'Content-Type': 'application/json'
        },
        data : data
      };
      
      axios.request(config)
      .then((response) => {
        console.log(JSON.stringify(response.data));
        res.redirect('/admin/successful')
      })
      .catch((error) => {
        console.log(error);
        res.redirect('/admin/failed')
      });
      
});

app.post('/api/addMoney', async function(req, res){
    let userID = req.body.userID;
    let balance = req.body.balance;
    let cash = balance*(dollorRatio/pointRatio);
    let type = req.body.type;
    let comment = req.body.comment;
    let data = JSON.stringify({
        "userID": userID,
        "cash": cash,
        "balance": balance, 
        "type": type,
        "comment": comment
    });
    let config = {
        method: 'put',
        maxBodyLength: Infinity,
        headers: { 
            'Content-Type': 'application/json'
        },
        data : data
    };
      
    await axios.request(config)
    .then((response) => {
    res.status(200).json({ status: 'success', message: '加值成功' });
    })
    .catch((error) => {
    res.status(500).json({ status: 'error', message: '加值失敗' });
    });
});

app.post('/api/getUserByStudentID', async function(req, res){
    let studentID = req.body.studentID;
    let config = {
        method: 'get',
        maxBodyLength: Infinity,
        headers: { }
    };
      
    await axios.request(config)
    .then((response) => {
        if (response.data[0] == null){
            res.status(200).json({ status: 'success', message: 'Not Found' });
        }
        else{
            res.status(200).json({ status: 'success', message: response.data[0] });
        }
    })
    .catch((error) => {
        res.status(500).json({ status: 'error', message: error });
    });
});

app.post('/api/setPriceTable', async function(req, res){
    let data = req.body;
    fs.writeFileSync('./public/priceTable.json', JSON.stringify(data.priceTable));
    res.status(200).json({ status: 'success', message: '設定成功' });
});

app.get('/api/usage', async function(req, res){
    let startDate = req.query.startDate;
    let endDate = req.query.endDate;
    var usage;
    let config = {
        method: 'get',
        maxBodyLength: Infinity,
        headers: { }
    };
      
    await axios.request(config)
    .then((response) => {
        usage = response.data;
    })
    .catch((error) => {
        console.log(error);
    });
    
    sortedUsage = await sortingUsage(usage);
    sortedUsage = await formatDate(sortedUsage);
    sortedUsage = await getTimeIntervalUsage(startDate, endDate, sortedUsage);
    res.status(200).json({ status: 'success', message: sortedUsage });
});

app.get('/api/statistics', async function(req, res){
    let year = req.query.year;
    let month = req.query.month;
    var usage;
    let config = {
        method: 'get',
        maxBodyLength: Infinity,
        headers: { }
    };
      
    await axios.request(config)
    .then((response) => {
        usage = response.data;
    })
    .catch((error) => {
        console.log(error);
    });
    
    sortedUsage = await sortingUsage(usage);
    sortedUsage = await formatDate(sortedUsage);
    monthStatics = await getMonthStatics(year, month, sortedUsage);
    res.status(200).json({ status: 'success', message: monthStatics });
});

/* Client */
app.get('/client', checkAuthenticated, isClient, function (req, res) {
    res.redirect("client/print");
});

app.get('/client/print', checkAuthenticated, isClient, async function (req, res) { 
    // recatch user data
    let userData = req.user;
    let userStudentID = req.user.studentID;
    async function getUserByStudentID(){
        let config = {
            method: 'get',
            maxBodyLength: Infinity,
            headers: { }
        };
        await axios.request(config)
        .then((response) => {
            userData = response.data[0];
        })
        .catch((error) => {
            console.log("ERROR: Occurred in the getUserByStudentID() function");
        });
    }
    await getUserByStudentID();
    // get printer list
    let printerData = ['No Printer'];
    async function getAllPrinterName(){
        let config = {
            method: 'get',
            maxBodyLength: Infinity,
            headers: { },
            timeout: 1000
        };
        await axios.request(config)
        .then((response) => {
            printerData = response.data;
        })
        .catch((error) => {
            console.log("ERROR: Occurred in the getAllPrinterName() function");
            // console.log(error);
        });
    }
    await getAllPrinterName();

    // get price table with fs
    var priceTable = (fs.readFileSync('./public/priceTable.json', 'utf8'));
    // console.log(priceTable);
    // console.log(userData);
    res.render("client/PrintSettingView", { printer: printerData, user: userData, priceTable: priceTable});
});

app.get('/client/usage', checkAuthenticated, isClient, function (req, res) {
    res.render("client/UsageView", {user: req.user});
});

app.post('/api/print/', upload.single('file'), async function(req, res){
    const file = req.file;
    const studentID = req.user.studentID;
    const printer = req.body['printer-name'];
    const pages = req.body.pages; 
    const color = req.body.color;
    const pageSize = req.body['page-size'];
    const copies = req.body.copies;
    const duplex = req.body.duplex;
    
    let data = new FormData();
    data.append('file', file.buffer, { filename: file.originalname });
    
    let clientConfig = {
        method: 'post',
        maxBodyLength: Infinity,
        headers: { 
            ...data.getHeaders()
        },
        data : data
    };

    await axios.request(clientConfig)
    .then((response) => {
        var userID = response.data.userID;
        var time = response.data.time;
        res.json({ "status": "success", "userID": userID, "time": time });
    })
    .catch((error) => {
        console.log("ERROR: request backend /printer/print error!!!");
        console.log(error);
        res.json({ "status": "error" })
    });
});

app.post('/api/confirm/', async function(req, res){
    const confirm = req.body.confirm;
    const userID = req.body.userID;
    const time = req.body.time;
    let returnString = "";
    if (confirm === "true"){
        returnString = "SUCCESS";
    }
    else{
        returnString = "FAILED";
    }
      let config = {
        method: 'put',
        maxBodyLength: Infinity,
        headers: { 
          'Content-Type': 'application/json'
        },
        data : data
      };
      
      await axios.request(config)
      .then((response) => {
        // console.log("call backend/printer/status: success");
        res.status(200).json({ status: 'success', message: 'success' });
      })
      .catch((error) => {
        console.log("call backend/printer/status: failed");
        console.log(error);
        res.status(500).json({ status: 'error', message: 'failed' });
      });
});
/* About */
app.get("/about", function (req, res) {
    res.render("about");
});

/* Error */
app.get("/error/404", function (req, res) {
    res.render("errorView", { message: "error 404"});
});

app.listen(process.env.PORT, function () {
    console.log("Server is running on port " + process.env.PORT);
});

async function sortingUsage(usage){
    var retUsage = [];
    for (let i = 0;i < usage.length; i++){
        var curUser;
        let config = {
            method: 'get',
            maxBodyLength: Infinity,
            headers: { }
        };
        
        await axios.request(config)
        .then((response) => {
            curUser = response.data[0];
        })
        .catch((error) => {
            console.log(error);
        });
        var curSheet;
        var totalPage = usage[i].pages * usage[i].copies;
        if (usage[i].duplex == 1){
            curSheet = Math.ceil(usage[i].pages / 2);
        }
        else{
            curSheet = usage[i].pages;
        }
        var totalSheet = curSheet * usage[i].copies;
        retUsage.push(curUsage);
    }
    return retUsage;
}

async function getTimeIntervalUsage(startDate, endDate, usage){
    var retUsage = [];
    for (let i = 0;i < usage.length; i++){
        if (usage[i].time >= startDate && usage[i].time <= endDate){
            retUsage.push(usage[i]);
        }
    }
    return retUsage;
}

// format data to yyyy-mm-dd
async function formatDate(usage){
    var retUsage = [];
    // original format: 2024-01-29T15:19:45
    for (let i = 0;i < usage.length; i++){
        var curTime = usage[i].time;
        var date = curTime.split('T')[0];
        var newTime = date + " ";
        usage[i].time = newTime;
        retUsage.push(usage[i]);
    }
    return retUsage;
}

async function getMonthStatics(year, month, usage){
    var retUsage = [];
    statistics = {
        "a4BlackTotalSheets": 0,
        "a4BlackTotalPages": 0,
        "a4BlackAmount": 0,
        "a4ColorTotalSheets": 0,
        "a4ColorTotalPages": 0,
        "a4ColorAmount": 0,
        "a3BlackTotalSheets": 0,
        "a3BlackTotalPages": 0,
        "a3BlackAmount": 0,
        "a3ColorTotalSheets": 0,
        "a3ColorTotalPages": 0,
        "a3ColorAmount": 0,
        "totalSheets": 0,
        "totalPages": 0,
        "totalAmount": 0
    }
    for (let i = 0;i < usage.length; i++){
        if (year == usage[i].time.split('-')[0] && month == usage[i].time.split('-')[1]){
            if (usage[i].pageSize == 0){ // A4
                if (usage[i].color == 0){ // black
                    statistics.a4BlackTotalSheets += usage[i].totalSheet;
                    statistics.a4BlackTotalPages += usage[i].totalPage;
                    statistics.a4BlackAmount += usage[i].cost;
                }
                else{
                    statistics.a4ColorTotalSheets += usage[i].totalSheet;
                    statistics.a4ColorTotalPages += usage[i].totalPage;
                    statistics.a4ColorAmount += usage[i].cost;
                }
            }
            else{ // A3
                if (usage[i].color == 0){ // black
                    statistics.a3BlackTotalSheets += usage[i].totalSheet;
                    statistics.a3BlackTotalPages += usage[i].totalPage;
                    statistics.a3BlackAmount += usage[i].cost;
                }
                else{
                    statistics.a3ColorTotalSheets += usage[i].totalSheet;
                    statistics.a3ColorTotalPages += usage[i].totalPage;
                    statistics.a3ColorAmount += usage[i].cost;
                }
            }
            statistics.totalSheets += usage[i].totalSheet;
            statistics.totalPages += usage[i].totalPage;
            statistics.totalAmount += usage[i].cost;
            retUsage.push(usage[i]);
        }
    }
    return statistics;
}