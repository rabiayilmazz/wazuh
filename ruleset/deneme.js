const XmlReader = require('xml-reader');

const { Console } = require('console');
const fs = require('fs');
const xmlQuery = require('xml-query');

var chars = ['w','s','S','d','t','.','(',')']

fs.writeFile('note.txt', '', function (err, data) {
  if (err) throw err;
});

fs.readFile('./xmls/0320-sudo_decoders.xml', function(err, data) {
    if(err) throw err;
    const paragraph = "'" + data + "'";
    const regex = /<decoder[\s\S]*?<\/decoder>/g;
    const found = paragraph.match(regex);

    var prematchs = [];
    var regexs = [];
    var decoder_names = []; 
    var dublicate = 0;
    var titles = [];
    var fieldnames = [];
    
    for (var i=0; i<found.length; i++){
      const ast = XmlReader.parseSync(found[i]);
      const xq = xmlQuery(ast);
      var fields = xq.children().map(node => node.name);

      decoder_names[i] = xq.attr('name');

      if (titles.includes(xq.attr('name'))){
        dublicate++;
        titles[i] = xq.attr('name')+dublicate;
      }else{
        titles[i] = xq.attr('name');
      }

      for (var j = 0; j < fields.length; j++ ){

        if(fields[j] == 'regex'){
          regexs[i] = xq.find(fields[j]).text();
        }

        //console.log(xq.children().eq(j).attr(0));
        if(fields[j] == 'prematch'){
          prematchs[i] = xq.find(fields[j]).text();
        }

        if(fields[j] == 'order'){
          fieldnames[i] = xq.find(fields[j]).text();
        }
        
      }

      if(regexs[i]==undefined){
        regexs[i]= " ";
      }

      if(prematchs[i]==undefined){
        prematchs[i]= " ";
      }

      if(fieldnames[i]==undefined){
        fieldnames[i]= decoder_names[i];
      }

      for(var char = 0; char<chars.length; char++){
        prematchs[i] = Replace(prematchs[i], chars[char]);
        regexs[i] = Replace(regexs[i], chars[char]);
      }

      convert(titles[i], fieldnames[i], regexs[i], prematchs[i]);
    }    
});

// create graylog extractor type with wazuh values
function convert(title, name, regex, prematch){
    var result =`
    "body":"{
      "title":"`+title+`",
      "cut_or_copy":"copy",
      "source_field":"message",
      "target_field":"`+name+`",
      "extractor_type":"regex",
      "extractor_config":{"regex_value":"`+ regex +`"},
      "converters":{},
      "condition_type":"regex",
      "condition_value":"`+prematch+`"
    }"\n`;

    fs.appendFile('sudo.txt', result, function (err, data) {
      if (err) throw err;
    });
    return result;
  }

  // change "\" character to "\\"
  function Replace(value, char){
    value = value.replaceAll("\\"+char ,  "\\\\"+char );
    return value;
  }
