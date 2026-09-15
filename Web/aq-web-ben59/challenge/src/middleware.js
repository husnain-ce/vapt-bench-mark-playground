
function requireAuth(req, res, next) {
  if (!req.session.user) {
    req.session.flash = { type: 'error', message: 'Please log in.' };
    return res.redirect('/login');
  }
  next();
}

module.exports = { requireAuth };
