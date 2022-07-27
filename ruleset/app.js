var jsdom = require("jsdom");
var request = require("request");
const fs = require('fs');

var xmlFileLink;

url = "https://github.com/rabiayilmazz/wazuh/tree/master/ruleset/decoderss" 
//https://github.com/rabiayilmazz/wazuh/tree/master/ruleset/decoderss
//https://github.com/wazuh/wazuh/blob/master/ruleset/decoders
siteUrl = "https://raw.githubusercontent.com"

// content of each file under decoder is retrieved
request(url, function (error, response, body) {
    var results = new jsdom.JSDOM(body);
    var links = results.window.document.querySelectorAll('span.css-truncate a.js-navigation-open');

    for(var i = 0; i < links.length; i++){
        xmlFileLink = siteUrl + links[i].getAttribute("href").replace("/blob","")
        //console.log(xmlFileLink);
        
        // the contents of all files are saved in note.xml 
        request(xmlFileLink,function(err,res,body){  
            fs.appendFile('rabia-yeni.xml', body , function (err, data) {
                if (err) throw err;
                console.log('Success');
            });
        })
    }
});    


