from app import initialize_application
from flask import redirect, url_for, request, g

application = initialize_application()

@application.after_request
def apply_security_headers(response):
    security_token = getattr(g, 'nonce', '')
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Content-Security-Policy'] = (
        f"default-src 'self'; "
        f"script-src 'self' 'nonce-{security_token}'; "
        f"style-src 'self' 'nonce-{security_token}'; "
        f"img-src *; "
        f"font-src 'self'; "
        f"connect-src 'self'; "
    )
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    return response

@application.route('/')
def root():
    return redirect(url_for('identity.authenticate'))

if __name__ == '__main__':
    application.run(host='0.0.0.0', port=5000)