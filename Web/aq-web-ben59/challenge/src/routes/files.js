
const express = require('express');
const fs = require('fs');
const path = require('path');
const { requireAuth } = require('../middleware');

const router = express.Router();

function listDirectory(directory, scrapname = "") {
  let entries = [];
  try {
    if (fs.existsSync(directory)) {
      entries = fs.readdirSync(directory).map(name => ({
        name,
        path: scrapname == "" ? path.join(directory, name).split("/").pop() : scrapname+"/"+path.join(directory, name).split("/").pop()
      }));
    }
  } catch {}
  return entries;
}

function safeJoin(base, ...segments) {
  const target = path.normalize(path.join(base, ...segments));
  if (!target.startsWith(path.normalize(base + path.sep))) {
    throw new Error('Path traversal blocked');
  }
  return target;
}

router.get('/', requireAuth, (req, res) => {
  let entries = listDirectory(req.session.user.scrap_dir);
  res.render('files', { entries });
});

router.get('/:scrapname/:subpath(*)?', requireAuth, (req, res) => {
  const rootUserDir = req.session.user.scrap_dir;
  const scrapName   = req.params.scrapname;
  const subpath     = req.params.subpath || '';

  const allScraps = listDirectory(rootUserDir);
  if (!allScraps.some(entry => entry.name === scrapName)) {
    req.session.flash = { type: 'error', message: 'This scrap does not exists.' };
    return res.redirect('/files');
  }

  let targetPath;
  try {
    targetPath = safeJoin(rootUserDir, scrapName, subpath);
  } catch {
    return res.sendStatus(400);
  }

  fs.stat(targetPath, (err, stats) => {
    if (err) {
      if (subpath) {
        req.session.flash = { type: 'error', message: 'This file does not exists.' };
        return res.redirect(`/files/${scrapName}`);
      } else {
        req.session.flash = { type: 'error', message: 'This scrap does not exists.' };
        return res.redirect('/files');
      }
    }

    if (stats.isDirectory()) {
      const entries = listDirectory(targetPath, path.posix.join(scrapName, subpath));
      return res.render('files', { entries });
    }

    res.setHeader('Content-Type', 'text/plain; charset=utf-8');
    res.setHeader('X-Content-Type-Options', 'nosniff');

    const stream = fs.createReadStream(targetPath);
    stream.on('error', () => res.sendStatus(500));
    stream.pipe(res);
  });
});

module.exports = router;
