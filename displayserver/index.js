console.log("PROGRAM INITIATED");

const  mysql = require('mysql');
const express = require('express');
const fs = require('fs')

let resourcelist = {};
let personlist = {};
var lastlocation = 0;

var connection = mysql.createConnection(
    {
        host:"siheternalvoid.cnqwzfu0zufz.ap-south-1.rds.amazonaws.com",
        user:"EternalVoid",
        password:"paneerbuttermasala",
        port : 3306,
        database : "temp"
        
    }
);
                                                                                                     

const app = express();
////////// DATABASE CONNECTION INITIALIZATION DONE////////////////////////////////

////////FUNCTION WHICH TAKES STRING AS ARGUMENT AND EXECUTES THE QUERY ///////////////


    app.get("/" , (req,res)=>{
        fs.readFile("landingpage.html",(err,filedata)=>{
            if(err)
            {
                console.log("Cannot read Landing page");
            }
            else
            {
                res.writeHead(200, {'Content-Type': 'text/html' });
                res.write(filedata);
                res.end();
            }
        })


    });//Landing Page



    app.get("/report" , (req,res)=>{
        fs.readFile("report.html",(err,filedata)=>{
            if(err)
            {
                console.log("Cannot read report page");
            }
            else
            {
                res.writeHead(200, {'Content-Type': 'text/html' });
                res.write(filedata);
                res.end();
            }
        })


    });//Landing Page




    app.get("/livereports",(req,res)=> {
        console.log("Homepage HIT!");
        
        fs.readFile("webpage.html",(err,filedata)=>{
            if(err)
            {
                console.log("File reading error");
            }
            else
            {
                res.writeHead(200,{ 'Content-Type': 'text/html' });
                res.write(filedata);
                res.end();
            }
        });

       
    });

    app.get("/disaster",(req,res)=>{
        console.log("Disaster table request hit");  
        var indexx = req.query.truck; 
        console.log("truck is : " + indexx);     
        connection.query(`SELECT distinct Disaster,Location FROM disaster `,(err,result,field)=>{
            if(err)
            {
                console.log(err);
            }
            else
            {
                console.log(result);
                res.send(result);
                res.end();
            }
        });

    });
 
    app.get("/resource",(req,res)=>{
        console.log( "Number of resouces : " + req.query.numberdata);
        var requestlocation = req.query.numberdata;
        

        connection.query(`SELECT * FROM people WHERE people.index > ${requestlocation}   ` , (err,result,field)=>{
            if(err)
            throw err;
            else
            {
                
                console.log(result);
                res.send(result);
                res.end();
            }
        } )
        console.log("AJAX HIT");
    });

    app.get("/agencylogin",(req,res)=>{


        fs.readFile("agency.html",(err,filedata)=>{
            if(err)
            {
                console.log("File reading error");
            }
            else
            {
                res.writeHead(200,{ 'Content-Type': 'text/html' });
                res.write(filedata);
                res.end();
            }
        });




    });

    
function initializeserver()
{
    app.listen(3002,()=>{
    console.log("Server started on port 3002");
    });
}

connection.connect(
    function(err)
    {
       
      if(err)
        throw err;
      else
      {
        initializeserver();
       
      } 

    }
);

console.log("OUT OF CONNECTION BLOCK");
