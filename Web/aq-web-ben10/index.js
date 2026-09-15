const express = require('express');
const ejs = require('ejs');
const app = express();

app.get('/', (req, res) => {
    const query = req.query;
    const queryValues = Object.values(query).join(' ').toLowerCase();
    const rawQuery = JSON.stringify(query).toLowerCase();
    const blacklist = [
    'require', 'fs', 'child_process', 'exec', 'spawn', 'flag', 'cat',
    'global', 'process', 'mainmodule', 'this','constructor', 'proto', 'return', 
    'function', 'class', 'new', 'import',
    ' ', '+', '`', '[', ']', '\\', 'char', 'from', 
    'join', 'split', 'reverse', 'replace', 'concat', 'slice',
    'eval', 'atob', 'btoa', 'buffer', 'decode', 'reflect', 'object', 'array', 'symbol', 'padend', 'padstart', 'unescape', 'escape', 'match', 'search', 'substring', 'substr'
];
    
    if (blacklist.some(word => rawQuery.includes(word))) {
        return res.status(403).send("What are you doing? There are nothing in here. Go away!");
    }

    const template = `
        <h2>Lylera secret, shhh!</h2>
        <p>Yui: Pst here ${query.msg || 'Standby'}</p>
        <p>Note: nothing in here...</p>
    `;

    try {
        const html = ejs.render(template, query, query); 
        res.send(html);
    } catch (e) {
        res.send("Hee-, Omoshiroi tane. Sa... wakatta, watashiwa makedesuyone. Ganbaree!! Hora flag: " + e.toString() );
    }
});

app.listen(3333, () => console.log('Lylera database Podium on 3333'));  
