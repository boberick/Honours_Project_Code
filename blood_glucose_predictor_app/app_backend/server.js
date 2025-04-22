const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const axios = require('axios');
const db = require('./database');

const app = express();
app.use(cors());
app.use(bodyParser.json());

app.get('/glucose-data', (req, res) => {
    db.find({}, (err, docs) => {
        if (err) {
            console.error('Database error:', err);
            return res.status(500).json({ error: 'Failed to fetch glucose data' });
        }
        res.json(docs);
    });
});

app.post('/predict', async (req, res) => {
  const { glucose, datetime } = req.body;

  try {
      // Make a request to the Python prediction model
      const response = await axios.post('http://localhost:5000/predict', { glucose, datetime });
      const predictions = response.data;

      // Store user input and predictions in the database
      const entry = { glucose, datetime, predictions: JSON.stringify(predictions) };
      db.insert(entry, (err, newDoc) => {
          if (err) {
              console.error('Database error:', err);
              return res.status(500).json({ error: 'Failed to save prediction' });
          }
          console.log('Inserted document:', newDoc);
          res.json(predictions);
      });

  } catch (error) {
      console.error('Prediction failed:', error.message);
      if (error.response) {
          console.error('Response data:', error.response.data);
          console.error('Response status:', error.response.status);
      }
      res.status(500).json({ error: 'Prediction failed', details: error.message });
  }
});

app.listen(8000, () => console.log('Node server running on http://localhost:8000'));