var mongoose = require("mongoose"),
    passportLocalMongoose = require("passport-local-mongoose");

var SniffSchema = new mongoose.Schema({
    capture : {
        time_stats : [
            {   arrival : String, // arrival time
                epoch : String, // epoch time
            }
        ],
        address: // MAC address
        [
            {
                source : String,
                destination : String,
            }
        ],
        advertising_data : [
            {   
                device_name : String,
                company_id : String,
                UUID : String
            }
        ],
        _timestamp : Number, // time of capture
    }
});

SniffSchema.plugin(passportLocalMongoose);
module.exports = mongoose.model("Bluetooth", SniffSchema);