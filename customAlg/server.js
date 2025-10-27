var http = require("http");
var url = require("url");
var selector = require('./nmapSelector.js') ;

const port=(process.argv[2] ? Number(process.argv[2]) : 8081);

function onRequest(request, response) {
  let queryData = "";

  response.setHeader("Access-Control-Allow-Origin", "*");
  response.setHeader("Access-Control-Allow-Headers", "ctatsession, Content-Type, Accept, Tutorshop-Path");
  response.setHeader("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS");
  response.setHeader("Access-Control-Max-Age", "1728000");

  var pathname = decodeURIComponent(url.parse(request.url).pathname);
  console.log("Request from", request.socket.remoteAddress, "for", pathname, "content-type", request.headers["content-type"]);
    if( !/::1|127[.]0[.]0[.]1/.test(request.socket.remoteAddress) &&
        !/[^0-9]?172[.][0-9]+[.][0-9]+[.][0-9]+/.test(request.socket.remoteAddress) ) {
    let err = "Unauthorized remoteAddress: "+request.socket.remoteAddress;
    console.log(err);
    request.destroy(new Error(err));
    return;
  }
  request.setEncoding("utf-8");        // data is string, not FormData
  request.on("data", function(data) {
    queryData += data;
  });

  request.on("end", function() {
    try {
      response.setHeader("Content-type", "application/json");
      response.end(selector.selectProblem(queryData, "skillAndProblemLevelRandom", true))
    } catch(e) {
      console.log("Error from router", e);
      request.destroy(e);
    }
  });
}

console.log("Server to listen on port",port,"argv",process.argv);
http.createServer(onRequest).listen(port);
