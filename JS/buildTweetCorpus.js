/*
    1370516400 = 06 Jun 2013 11:00am GMT
    1372590000 = 30 Jun 2013 11:00am GMT

    "http://topsy.com/s?type=tweet&sort=-date&mintime=1370516400&maxtime=1372590000&q=%23ogiganteacordou&offset=0";
*/

var MINTIME = 1370516400; // = 06 Jun 2013 11:00am GMT
var MAXTIME = 1372590000; // = 30 Jun 2013 11:00am GMT
var URL = "http://topsy.com/s?type=tweet&sort=-date&mintime="+MINTIME+"&maxtime="+MAXTIME;
var URL_LENGTH = URL.length;

var system = require('system');
var cHashTag = "";
var cOffset = "0";

// Print usage message, if no twitter ID is passed
if (system.args.length < 3) {
    console.log("Usage: buildTweetCorpus.js [hashtag] [offset]");
    phantom.exit();
} else {
    cHashTag = system.args[1];
    cOffset = system.args[2];
}

function printTweets(url){
    return function(){
        var page = require('webpage').create();
        page.onConsoleMessage = function(msg) { console.log(msg); };

        page.open(url, function (status) {
            if (status !== 'success') {
                console.log('Unable to load the address!');
                return;
            }
            window.setTimeout(function(){
                var results = page.evaluate(function() {
                    var list = document.querySelectorAll('.media-body > div');
                    var aTagPattern = /<\/?a[^>]*>/ig;
                    var addressPattern = /[^\s]+\.(com|net|org|fm|be|co|me|gl|br|ly|it)[^\s]+/ig;
                    var userPattern = /@[^\s]+/ig;

                    for (var i=0; i<list.length; i++) {
                        var htmlText = list[i].innerHTML;
                        if(htmlText.lastIndexOf("RT",0) === 0) {continue;}
                        var s = htmlText.replace(aTagPattern, " ")
                                        .replace(addressPattern, " ")
                                        .replace(userPattern, " ")
                                        .replace(/\s+/g, " ").trim().toLowerCase();
                        console.log(s);
                    }
                });
                //console.log("\n---!!!---"+url.substring(URL_LENGTH)+"---!!!---\n");
                page.close();
                phantom.exit();
            }, 100);
        });        
    }
}

var furl = URL+"&q=%23"+cHashTag+"&offset="+cOffset;
printTweets(furl)();

