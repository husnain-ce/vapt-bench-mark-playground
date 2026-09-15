
function requireAuth(req, res, next) {
  if (!req.session.user) {
    req.session.flash = { type: 'error', message: 'Please log in.' };
    return res.redirect('/login');
  }
  next();
}

function requireUser(req, res, next) {
  if(!req.session.user) {
     req.session.flash = { type: 'error', message: 'Please log in.' };
     return res.redirect('/login'); 
  }
  if(req.session.user.role != "user") {
      req.session.flash = req.session.flash = { type: 'error', message: 'Unauthorized.' };
      return res.redirect('/checker');
  }
  next();
}

module.exports = { requireAuth, requireUser };
