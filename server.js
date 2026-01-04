const express = require('express');
const axios = require('axios');
const path = require('path');

const app = express();

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'views', 'index.html'));
});

app.get('/results-page', (req, res) => {
    res.sendFile(path.join(__dirname, 'views', 'results.html'));
});

app.get('/favorites', (req, res) => {
    res.sendFile(path.join(__dirname, 'views', 'favorites.html'));
});

app.get('/api/search', async (req, res) => {
    try {
        const query = req.query.q;
        const response = await axios.get(`http://127.0.0.1:8000/search?query=${encodeURIComponent(query)}`);
        res.json(response.data);
    } catch (error) {
        res.status(500).json({ error: "خطأ في الاتصال بمحرك البحث" });
    }
});

app.listen(3000, () => console.log('🚀 السيرفر يعمل على http://localhost:3000'));