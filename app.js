const express = require("express"),
    app = express(),
    mongoose = require("mongoose"),
    Wifi = require("./models/wifi"),
    Bluetooth = require("./models/bluetooth"),
    bodyParser = require("body-parser"),
    dotenv = require("dotenv");

dotenv.config();
app.use(bodyParser.urlencoded({
    extended: true,
    limit: '50mb',
    parameterLimit: 100000,
    extended: true 
}));

app.use(express.json({limit: '50mb'}));
app.use(bodyParser.json({limit: '50mb'}));


var redirectToHTTPS = require('express-http-to-https').redirectToHTTPS; //makes all request secure
app.use(redirectToHTTPS([/localhost:(\d{4})/], [/\/insecure/], 301));


var MemoryStore = require("memorystore")(require('express-session'));

app.use(require("express-session")({
   secret : process.env.expressSECRET,
   store: new MemoryStore({
    checkPeriod: 86400000 // prune expires entries every 24h
  }),
   resave : false,
   saveUninitialized : false
}));

/**
 * CORS Bypass
 */
app.use(function (req, res, next) {

    // Website you wish to allow to connect
    res.setHeader('Access-Control-Allow-Origin', '*');

    // Request methods you wish to allow
    res.setHeader('Access-Control-Allow-Methods', 'GET');

    // Request headers you wish to allow
    res.setHeader('Access-Control-Allow-Headers', 'X-Requested-With,content-type');

    // Set to true if you need the website to include cookies in the requests sent
    // to the API (e.g. in case you use sessions)
    res.setHeader('Access-Control-Allow-Credentials', true);

    // Pass to next layer of middleware
    next();
});


/**
 * Mongoose Setup
 */
// mongoose.set('useCreateIndex', true);
// mongoose.set('useFindAndModify', false);

// mongoose.Promise = global.Promise;
const URI = `mongodb+srv://${process.env.mongo_username}:${process.env.mongo_password}@cluster0.ql2nq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority`;

const connectionParams={
    useNewUrlParser: true,
    // useCreateIndex: true,
    useUnifiedTopology: true 
}

mongoose.connect(URI,connectionParams)
    .then( () => {
        console.log('Connected to database')
    })
    .catch( (err) => {
        console.error(`Error connecting to the database. \n${err}`);
    });


// mongoose.connect("mongodb://"+process.env.mongoDB+"/CACTUS",{ useNewUrlParser: true , useUnifiedTopology: true}); // LOCAL connection


// /**
//  * Constant 10 minute Heroku based request for minimized load times.
//  * Removes server idling.
//  */
// setInterval(() => {
//     request(process.env.url);
//     console.debug("API loaded again");
// }, 9.99*1000*60);

// Removes all data from the database -- use with caution
var destruct = async ()=>{
    // make sure wifi collection exists
    Wifi.collection.count((err, count)=> {
        if (!err && count > 0) {
            Wifi.collection.drop((err, collectionDrop)=>{
                if(err)
                {
                    console.error("Failed to drop collection");
                    throw new Error(err.message);
                }
                console.log("Wifi Collection dropped successfully");
            });
        }
        else
        {
            console.log("Wifi Collection exists");
        }
    });
    
    Bluetooth.collection.count((err, count)=> {
        if (!err && count > 0) {
            Bluetooth.collection.drop((err, collectionDrop)=>{
                if(err)
                {
                    console.error("Failed to drop collection");
                    throw new Error(err.message);
                }
                console.log("Bluetooth Collection dropped successfully");
            });
        }
        else
        {
            console.log("Bluetooth Collection exists");
        }
    });

}

/**
 * helper function for creating a new Sniff Object
 * data specified by param.
 * @param {Object} data : Check API under models/sniff
 */
var createObservation = (data, type)=>{
    if(type === "wifi")
    {
        Wifi.create({"capture" : data}, (err, addedObj)=>{
            if(err)
            {
                if(err.code === 11000)
                {
                    Wifi.collection.dropIndex("username_1", (err, indexDrop)=>{
                        if(err)
                        {
                            console.error("Failed to drop index duplicate key");
                            throw new Error(err.message);
                        }
                        console.log("index duplicate key drop successful");
                        createObservation(data);
                    });
                }
                else
                {
                    throw new Error(err.message);
                }
                
            }
            console.log("Successfully created new WiFi object");
        });
    }
    else
    {
        Bluetooth.create({"capture" : data}, (err, addedObj)=>{
            if(err)
            {
                if(err.code === 11000)
                {
                    Bluetooth.collection.dropIndex("username_1", (err, indexDrop)=>{
                        if(err)
                        {
                            console.error("Failed to drop index duplicate key");
                            throw new Error(err.message);
                        }
                        console.log("index duplicate key drop successful");
                        createObservation(data);
                    });
                }
                else
                {
                    throw new Error(err.message);
                }
                
            }
            console.log("Successfully created new Bluetooth object");
        });
    }
    
};

//******************************************************************** ROUTES *************************************************************************** */

//  create a POST route that will read the json data and create a new Sniff object
app.post("/api/sniff", (req, res)=>{
    console.log("POST request received");
    var data = req.body.data;
    const type = req.body.type;
    createObservation(data, type);
    res.send("Successfully uploaded new object");
});

app.get("/", (req, res)=>{
    res.send("Hello world!");
});

const limit = 10; // number of objects to return

// create a route called /showdata that will return all the data in the database
app.get("/showdata", (req, res)=>{
    if(req.query && req.query.technology === "wifi" )
    {
        Wifi.find().sort({'capture._timestamp' : -1}).limit(limit).exec((err, data)=>{
            if(err)
            {
                throw new Error(err.message);
            }
            return res.json(data);
        });
    }
    else if(req.query && req.query.technology === "bluetooth")
    {
        Bluetooth.find().sort({'capture._timestamp' : -1}).limit(limit).exec((err, data)=>{
            if(err)
            {
                throw new Error(err.message);
            }
            return res.json(data);
        });
    }
    else
    {
        return res.send("Please specify technology. Options: [wifi, bluetooth]");
    }
    
});

// create a route called /query that takes in input a MAC address string and returns the data that matches the query
// app.get("/query", (req, res)=>{
//     if(req.query && req.query.technology === "wifi" )
//     {
//         Wifi.find(req.query).sort({'capture._timestamp' : -1}).limit(limit).exec((err, data)=>{
//             if(err)
//             {
//                 throw new Error(err.message);
//             }
//             return res.json(data);
//         });
//     }
//     else if(req.query && req.query.technology === "bluetooth")
//     {
//         Bluetooth.find(req.query).sort({'capture._timestamp' : -1}).limit(limit).exec((err, data)=>{
//             if(err)
//             {
//                 throw new Error(err.message);
//             }
//             return res.json(data);
//         });
//     }
//     else
//     {
//         return res.send("Please specify technology. Options: [wifi, bluetooth]");
//     }
    
// });

// create a route called /danger/removedata that will return all the data in the database
app.get("/danger/removedata", (req, res)=>{
    destruct().then(()=>{
        res.send("Successfully removed all data from database");
    });

});

app.post("*", (req, res)=>{
    res.send("Invalid API route");
});

//******************************************************************** LAUNCH SERVER *************************************************************************** */
app.listen(process.env.PORT || 5000, process.env.IP,()=>{
    console.log(`Server Connected at port ${process.env.PORT || 5000}`);
 });
