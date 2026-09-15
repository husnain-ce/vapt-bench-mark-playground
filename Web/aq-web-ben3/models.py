from flaHIGHNOTE_API_KEY_PLACEHOLDER import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class SAMLConfig(db.Model):
    """SAML Configuration Model - Supports Multiple IdPs"""
    __tablename__ = 'saml_config'

    id = db.Column(db.Integer, primary_key=True)

    # Organization/Tenant identifier - each IdP is tied to an organization
    organization = db.Column(db.String(200), unique=True, nullable=False, default='default')
    organization_display_name = db.Column(db.String(200))

    # State flags
    enabled = db.Column(db.Boolean, default=False, nullable=False)
    configured = db.Column(db.Boolean, default=False, nullable=False)

    # Identity Provider (IdP) Configuration
    idp_entity_id = db.Column(db.String(500))
    idp_sso_url = db.Column(db.String(500))
    idp_slo_url = db.Column(db.String(500))
    idp_x509_cert = db.Column(db.Text)

    # Service Provider (SP) Configuration
    sp_entity_id = db.Column(db.String(500))
    sp_acs_url = db.Column(db.String(500))
    sp_sls_url = db.Column(db.String(500))
    sp_x509_cert = db.Column(db.Text)
    sp_private_key = db.Column(db.Text)

    # Organization Information
    org_name = db.Column(db.String(200))
    org_display_name = db.Column(db.String(200))
    org_url = db.Column(db.String(500))

    # Technical Contact
    tech_contact_name = db.Column(db.String(200))
    tech_contact_email = db.Column(db.String(200))

    # Support Contact
    support_contact_name = db.Column(db.String(200))
    support_contact_email = db.Column(db.String(200))

    # Security Settings (stored as JSON-like strings or booleans)
    authn_requests_signed = db.Column(db.Boolean, default=False)
    logout_request_signed = db.Column(db.Boolean, default=False)
    logout_response_signed = db.Column(db.Boolean, default=False)
    want_messages_signed = db.Column(db.Boolean, default=False)
    want_assertions_signed = db.Column(db.Boolean, default=False)
    want_assertions_encrypted = db.Column(db.Boolean, default=False)
    want_name_id_encrypted = db.Column(db.Boolean, default=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_settings_dict(self):
        """Convert database model to settings.json format for python3-saml"""
        return {
            "strict": False,
            "debug": False,
            "sp": {
                "entityId": self.sp_entity_id or "",
                "assertionConsumerService": {
                    "url": self.sp_acs_url or "",
                    "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
                },
                "singleLogoutService": {
                    "url": self.sp_sls_url or "",
                    "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
                },
                "NameIDFormat": "urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified",
                "x509cert": self.sp_x509_cert or "",
                "privateKey": self.sp_private_key or ""
            },
            "idp": {
                "entityId": self.idp_entity_id or "",
                "singleSignOnService": {
                    "url": self.idp_sso_url or "",
                    "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
                },
                "singleLogoutService": {
                    "url": self.idp_slo_url or "",
                    "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
                },
                "x509cert": self.idp_x509_cert or ""
            },
            "security": {
                "nameIdEncrypted": self.want_name_id_encrypted,
                "authnRequestsSigned": self.authn_requests_signed,
                "logoutRequestSigned": self.logout_request_signed,
                "logoutResponseSigned": self.logout_response_signed,
                "signMetadata": False,
                "wantMessagesSigned": self.want_messages_signed,
                "wantAssertionsSigned": self.want_assertions_signed,
                "wantAssertionsEncrypted": self.want_assertions_encrypted,
                "wantNameId": True,
                "wantNameIdEncrypted": self.want_name_id_encrypted,
                "wantAttributeStatement": True,
                "requestedAuthnContext": True,
                "signatureAlgorithm": "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256",
                "digestAlgorithm": "http://www.w3.org/2001/04/xmlenc#sha256"
            },
            "contactPerson": {
                "technical": {
                    "givenName": self.tech_contact_name or "",
                    "emailAddress": self.tech_contact_email or ""
                },
                "support": {
                    "givenName": self.support_contact_name or "",
                    "emailAddress": self.support_contact_email or ""
                }
            },
            "organization": {
                "en-US": {
                    "name": self.org_name or "",
                    "displayname": self.org_display_name or "",
                    "url": self.org_url or ""
                }
            }
        }

    @staticmethod
    def get_or_create():
        """Get existing config or create a new one (backwards compatibility)"""
        config = SAMLConfig.query.first()
        if not config:
            config = SAMLConfig(organization='default')
            db.session.add(config)
            db.session.commit()
        return config

    @staticmethod
    def get_by_organization(organization):
        """Get SAML config for a specific organization"""
        return SAMLConfig.query.filter_by(organization=organization).first()

    @staticmethod
    def get_all_enabled():
        """Get all enabled SAML configurations"""
        return SAMLConfig.query.filter_by(enabled=True).all()

    def __repr__(self):
        return f'<SAMLConfig org={self.organization} enabled={self.enabled} configured={self.configured}>'


class Todo(db.Model):
    """Todo Model"""
    __tablename__ = 'todos'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), nullable=False)
    organization = db.Column(db.String(200), default='default')  # Links todo to organization
    title = db.Column(db.String(500), nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        """Convert to dictionary for JSON responses"""
        return {
            'id': self.id,
            'username': self.username,
            'organization': self.organization,
            'title': self.title,
            'completed': self.completed,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'<Todo {self.id}: {self.title} (completed={self.completed})>'