"""
Database helper functions for caching Jira data
"""

import models
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


def cache_project(project_data):
    """
    Cache or update a project in the database

    Args:
        project_data (dict): Project data from Jira API

    Returns:
        Project: The cached project object
    """
    try:
        project_key = project_data.get("key")
        if project_key is None or project_key == "":
            logger.warning("Project data missing 'key' field")
            return None

        # Check if project already exists
        project = models.Project.query.filter_by(project_key=project_key).first()

        if project is not None:
            # Update existing project
            project.name = project_data.get("name", project.name)
            project.description = project_data.get("description", project.description)
            project.lead = project_data.get("lead", {}).get("displayName", project.lead)
            project.project_type = project_data.get(
                "projectTypeKey", project.project_type
            )
            project.cached_at = datetime.utcnow()
            project.raw_data = json.dumps(project_data)
            logger.info(f"Updated project cache: {project_key}")
        else:
            # Create new project
            project = models.Project(
                project_key=project_key,
                name=project_data.get("name", ""),
                description=project_data.get("description", ""),
                lead=project_data.get("lead", {}).get("displayName", ""),
                project_type=project_data.get("projectTypeKey", ""),
                raw_data=json.dumps(project_data),
            )
            models.db.session.add(project)
            logger.info(f"Created project cache: {project_key}")

        models.db.session.commit()
        return project

    except Exception as e:
        logger.error(f"Error caching project: {e}")
        models.db.session.rollback()
        return None


def cache_issue(issue_data):
    """
    Cache or update an issue in the database

    Args:
        issue_data (dict): Issue data from Jira API

    Returns:
        CachedIssue: The cached issue object
    """
    try:
        issue_key = issue_data.get("key")
        if issue_key is None or issue_key == "":
            logger.warning("Issue data missing 'key' field")
            return None

        fields = issue_data.get("fields", {})

        # Check if issue already exists
        issue = models.CachedIssue.query.filter_by(issue_key=issue_key).first()

        # Parse dates
        created_date = None
        updated_date = None
        try:
            created_value = fields.get("created")
            updated_value = fields.get("updated")
            if created_value is not None and created_value != "":
                created_date = datetime.fromisoformat(
                    created_value.replace("Z", "+00:00")
                )
            if updated_value is not None and updated_value != "":
                updated_date = datetime.fromisoformat(
                    updated_value.replace("Z", "+00:00")
                )
        except Exception as e:
            logger.warning(f"Error parsing dates for {issue_key}: {e}")

        # Derive project key, fall back to key prefix if Jira omits project field
        project_key = fields.get("project", {}).get("key")
        if (project_key is None or project_key == "") and "-" in issue_key:
            project_key = issue_key.split("-", 1)[0]

        if issue is not None:
            # Update existing issue
            issue.project_key = project_key or issue.project_key
            issue.summary = fields.get("summary", issue.summary)
            issue.description = fields.get("description", issue.description)
            issue.status = fields.get("status", {}).get("name", issue.status)
            issue.priority = fields.get("priority", {}).get("name", issue.priority)
            issue.issue_type = fields.get("issuetype", {}).get("name", issue.issue_type)
            assignee_data = fields.get("assignee")
            if assignee_data is not None:
                issue.assignee = assignee_data.get("displayName")
            else:
                issue.assignee = None
            reporter_data = fields.get("reporter")
            if reporter_data is not None:
                issue.reporter = reporter_data.get("displayName")
            else:
                issue.reporter = None
            issue.created_date = created_date or issue.created_date
            issue.updated_date = updated_date or issue.updated_date
            issue.cached_at = datetime.utcnow()
            issue.raw_data = json.dumps(issue_data)
            logger.info(f"Updated issue cache: {issue_key}")
        else:
            # Create new issue
            assignee_data = fields.get("assignee")
            if assignee_data is not None:
                assignee_value = assignee_data.get("displayName")
            else:
                assignee_value = None
            reporter_data = fields.get("reporter")
            if reporter_data is not None:
                reporter_value = reporter_data.get("displayName")
            else:
                reporter_value = None
            issue = models.CachedIssue(
                issue_key=issue_key,
                project_key=project_key or "",
                summary=fields.get("summary", ""),
                description=fields.get("description", ""),
                status=fields.get("status", {}).get("name", ""),
                priority=fields.get("priority", {}).get("name", ""),
                issue_type=fields.get("issuetype", {}).get("name", ""),
                assignee=assignee_value,
                reporter=reporter_value,
                created_date=created_date,
                updated_date=updated_date,
                raw_data=json.dumps(issue_data),
            )
            models.db.session.add(issue)
            logger.info(f"Created issue cache: {issue_key}")

        models.db.session.commit()
        return issue

    except Exception as e:
        logger.error(f"Error caching issue: {e}")
        models.db.session.rollback()
        return None


def cache_multiple_issues(issues_list):
    """
    Cache multiple issues at once

    Args:
        issues_list (list): List of issue data from Jira API

    Returns:
        int: Number of issues successfully cached
    """
    cached_count = 0
    for issue_data in issues_list:
        cached_issue = cache_issue(issue_data)
        if cached_issue is not None:
            cached_count += 1

    return cached_count


def get_cached_project(project_key):
    """
    Get a cached project from the database

    Args:
        project_key (str): Project key

    Returns:
        Project: The cached project or None
    """
    return models.Project.query.filter_by(project_key=project_key).first()


def get_cached_issue(issue_key):
    """
    Get a cached issue from the database

    Args:
        issue_key (str): Issue key

    Returns:
        CachedIssue: The cached issue or None
    """
    return models.CachedIssue.query.filter_by(issue_key=issue_key).first()


def get_cached_issues(project_key=None, limit=50):
    """
    Get cached issues from the database

    Args:
        project_key (str): Filter by project key (optional)
        limit (int): Maximum number of issues to return

    Returns:
        list: List of cached issues
    """
    query = models.CachedIssue.query

    if project_key is not None and project_key != "":
        query = query.filter_by(project_key=project_key)

    return query.order_by(models.CachedIssue.updated_date.desc()).limit(limit).all()


def clear_old_cache(days=7):
    """
    Clear cache entries older than specified days

    Args:
        days (int): Number of days to keep cache

    Returns:
        int: Number of entries deleted
    """
    try:
        from datetime import timedelta

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Delete old projects
        project_count = models.Project.query.filter(
            models.Project.cached_at < cutoff_date
        ).delete()

        # Delete old issues
        issue_count = models.CachedIssue.query.filter(
            models.CachedIssue.cached_at < cutoff_date
        ).delete()

        models.db.session.commit()
        logger.info(
            f"Cleared {project_count} projects and {issue_count} issues from cache"
        )

        return project_count + issue_count

    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        models.db.session.rollback()
        return 0
