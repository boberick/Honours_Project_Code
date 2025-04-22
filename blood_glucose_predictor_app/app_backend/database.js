const Datastore = require('nedb');
const db = new Datastore({ filename: 'app_backend/glucose_data.db', autoload: true });

module.exports = db;