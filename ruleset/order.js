const XmlReader = require('xml-reader');

const { Console } = require('console');
const fs = require('fs');
const xmlQuery = require('xml-query');

var chars = ['w','s','S','d','t','.','(',')']

fs.writeFile('new.txt', '', function (err, data) {
  if (err) throw err;
});

fs.readFile('test.xml', function(err, data) {
    if(err) throw err;
    const paragraph = "'" + data + "'";
    const regex = /<decoder[\s\S]*?<\/decoder>/g;
    const found = paragraph.match(regex);

    var regexs = [];
    var order = [];
    
    for (var i=0; i<found.length; i++){
      
      const ast = XmlReader.parseSync(found[i]);
      const xq = xmlQuery(ast);
      var fields = xq.children().map(node => node.name);

      // xml deki field değerlerini almak için
      for (var j = 0; j < fields.length; j++ ){

        if(fields[j] == 'regex'){
          regexs[i] = xq.find(fields[j]).text();
        }

        if(fields[j] == 'order'){
            order[i] = xq.find(fields[j]).text();
        }
      }
      // nokta yı değiştir regexleri birleştir

      var decoder = found[i];
      var array = order[i].split(',');
      var regxs = [];
      var regx = regexs[i];
      var d = 1;
      regxs[0] = "ilk";
      // oderları decoderda gerekli yere yazdırma için order dizisinin uzunluğu kadar dön
      for (var r=0; r<array.length; r++){
        decoder = decoder.replace(decoder , decoder+"\r\n"+found[i]);
        decoder = decoder.replace(order[i],array[r]);

        // regexlerdeki parantezleri tek tel silmek için
        for(var k=0; k<r; k++){
            regx = regx.replace("(" , "");
            regx = regx.replace(")" , "");
            //regxs[0] = regexs[i];
            regxs[d] = regx;
            d++
        }
        //console.log(regxs[r] + r);
        decoder = decoder.replace(regexs[i],regxs[r]); 
        //decoder = decoder.replaceAll(regexs[i], "(" +regexs[i]+")")
        //console.log(decoder);
      }
      //console.log(decoder+"\n\n\n");
      decoder = decoder.replace("ilk",regexs[i]);
      decoder = decoder.replaceAll("\\.","öğö");
      decoder = decoder.replaceAll(".","\\.");
      decoder = decoder.replaceAll("öğö",".");
      decoder = decoder.replaceAll("</regex>\r\n<regex>", "");
      decoder = decoder.replaceAll("^","");
      //decoder = decoder.replaceAll("\\|","|");
      /*decoder = decoder.replaceAll("[","\\[");
      decoder = decoder.replaceAll("]","\\]");*/
      //decoder = decoder.replaceAll("\\.","\\S");
      fs.appendFile('test.xml', "\r\n" + decoder, function (err, data) {
        if (err) throw err;
      });    
    }  
});
