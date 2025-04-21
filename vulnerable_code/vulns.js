const express = require('express');
const app = express();

app.get('/user/:id', function(req, res) {
  const userId = req.params.id;
  // Potential SQL Injection vulnerability
  const query = "SELECT * FROM users WHERE id = '" + userId + "'";
  db.query(query, function(err, result) {
    if (err) throw err;
    res.send(result);
  });
});

app.listen(3000, () => {
  console.log('Server is running on port 3000');
});
#yes_done_done
