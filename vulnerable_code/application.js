const express = require('express');
const app = express();
const bodyParser = require('body-parser');
app.use(bodyParser.urlencoded({ extended: true }));

// Insecure eval usage
app.post('/eval', (req, res) => {
  const input = req.body.code;
  eval(input);  // ❌ High severity
  res.send("Evaluated input");
});

// Hardcoded password
const dbPassword = "supersecretpassword";  // ❌ Should be flagged
