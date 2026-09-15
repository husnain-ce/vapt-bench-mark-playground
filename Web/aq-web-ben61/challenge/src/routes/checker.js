
const express = require('express');
const { requireAuth } = require('../middleware');
const { visitUserWebsite } = require('../services/bot');

const router = express.Router();

router.get('/', requireAuth, async (_, res) => {
  res.render('checker');
});

router.post('/visit', requireAuth, async (req, res) => {
  const { url } = req.body;
  try {
    if(!url.startsWith("http://") && !url.startsWith("https://")) {
      req.session.flash = { type: 'error', message: 'Invalid URL.' };
    } else {
      await visitUserWebsite(url, req.session.user.data_dir);
      req.session.flash = { type: 'success', message: 'Your website can definitely be scrap, be careful...' };
    }
  } catch (e) {
    console.log(e);
    req.session.flash = { type: 'error', message: `An error occured.` };
  }
  res.redirect('/checker');
});

module.exports = router;
