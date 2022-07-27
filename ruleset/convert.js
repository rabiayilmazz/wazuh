var fs = require('fs');
var xml2json = require('xml2js');
var parser = new xml2json.Parser();

fs.appendFile('note.xml', '</body>', function (err, data) {
  if (err) throw err;
  console.log('Success');
});

fs.readFile('note.xml', function(err,data){
    parser.parseString(data, function(err, result){  
        result = JSON.stringify(result, null, 0);
        console.log(result);
        fs.writeFile('result.json', result, function (err, data) {
            console.log(result)
            if (err) throw err;
            console.log('Success');
          });
    });
});
