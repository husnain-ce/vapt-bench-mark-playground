"""
Database models for Project Hub
"""

import flaHIGHNOTE_API_KEY_PLACEHOLDER
import datetime

db = flaHIGHNOTE_API_KEY_PLACEHOLDER.SQLAlchemy()


class User(db.Model):
    """User model for storing user information"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    jira_account_id = db.Column(db.String(120), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    # Relationships
    cached_issues = db.relationship("CachedIssue", backref="cached_by_user", lazy=True)
    activity_logs = db.relationship("ActivityLog", backref="user", lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "jira_account_id": self.jira_account_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class CachedIssue(db.Model):
    """Cache Jira issues locally for faster access"""

    __tablename__ = "cached_issues"

    id = db.Column(db.Integer, primary_key=True)
    issue_key = db.Column(db.String(50), unique=True, nullable=False, index=True)
    project_key = db.Column(db.String(50), nullable=False, index=True)
    summary = db.Column(db.String(500))
    description = db.Column(db.Text)
    status = db.Column(db.String(50))
    priority = db.Column(db.String(50))
    issue_type = db.Column(db.String(50))
    assignee = db.Column(db.String(120))
    reporter = db.Column(db.String(120))
    created_date = db.Column(db.DateTime)
    updated_date = db.Column(db.DateTime)

    # Cache metadata
    cached_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    cached_by = db.Column(db.Integer, db.ForeignKey("users.id"))

    # Store full JSON data
    raw_data = db.Column(db.Text)  # JSON string

    def __repr__(self):
        return f"<CachedIssue {self.issue_key}>"

    def to_dict(self):
        return {
            "id": self.id,
            "issue_key": self.issue_key,
            "project_key": self.project_key,
            "summary": self.summary,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "issue_type": self.issue_type,
            "assignee": self.assignee,
            "reporter": self.reporter,
            "created_date": self.created_date.isoformat()
            if self.created_date
            else None,
            "updated_date": self.updated_date.isoformat()
            if self.updated_date
            else None,
            "cached_at": self.cached_at.isoformat() if self.cached_at else None,
        }


class Project(db.Model):
    """Store project information"""

    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    project_key = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    lead = db.Column(db.String(120))
    project_type = db.Column(db.String(50))

    # Cache metadata
    cached_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Store full JSON data
    raw_data = db.Column(db.Text)  # JSON string

    def __repr__(self):
        return f"<Project {self.project_key}>"

    def to_dict(self):
        return {
            "id": self.id,
            "project_key": self.project_key,
            "name": self.name,
            "description": self.description,
            "lead": self.lead,
            "project_type": self.project_type,
            "cached_at": self.cached_at.isoformat() if self.cached_at else None,
        }


class ActivityLog(db.Model):
    """Log user activities and API calls"""

    __tablename__ = "activity_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    action = db.Column(
        db.String(100), nullable=False
    )  # e.g., 'view_issue', 'search', 'download_attachment'
    resource_type = db.Column(db.String(50))  # e.g., 'issue', 'project', 'attachment'
    resource_id = db.Column(db.String(100))  # e.g., 'KAN-1', 'PROJECT-KEY'
    details = db.Column(db.Text)  # JSON string for additional details
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    created_at = db.Column(
        db.DateTime, default=datetime.datetime.utcnow, nullable=False, index=True
    )

    def __repr__(self):
        return f"<ActivityLog {self.action} - {self.resource_type}:{self.resource_id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "details": self.details,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class SavedSearch(db.Model):
    """Store user's saved JQL searches"""

    __tablename__ = "saved_searches"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    name = db.Column(db.String(200), nullable=False)
    jql_query = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    is_favorite = db.Column(db.Boolean, default=False)
    created_at = db.Column(
        db.DateTime, default=datetime.datetime.utcnow, nullable=False
    )
    updated_at = db.Column(
        db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    # Relationships
    user = db.relationship("User", backref="saved_searches", lazy=True)

    def __repr__(self):
        return f"<SavedSearch {self.name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "jql_query": self.jql_query,
            "description": self.description,
            "is_favorite": self.is_favorite,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class JiraConfiguration(db.Model):
    """Store Jira connection configuration"""

    __tablename__ = "jira_configurations"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)  # Friendly name for this config
    jira_url = db.Column(
        db.String(500), nullable=False
    )  # e.g., 'company.atlassian.net'
    email = db.Column(db.String(200), nullable=False)  # User email for authentication
    api_token = db.Column(
        db.Text, nullable=False
    )  # API token (should be encrypted in production)
    project_key = db.Column(db.String(50))  # Default project key
    is_active = db.Column(
        db.Boolean, default=False
    )  # Only one config can be active at a time
    created_at = db.Column(
        db.DateTime, default=datetime.datetime.utcnow, nullable=False
    )
    updated_at = db.Column(
        db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    def __repr__(self):
        return f"<JiraConfiguration {self.name}>"

    def to_dict(self, include_token=False):
        result = {
            "id": self.id,
            "name": self.name,
            "jira_url": self.jira_url,
            "email": self.email,
            "project_key": self.project_key,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_token:
            result["api_token"] = self.api_token
        return result
