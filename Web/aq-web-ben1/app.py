import flask
import flaHIGHNOTE_API_KEY_PLACEHOLDER
import config
import jira_client
import models
import db_helpers
import logging
import io

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = flask.Flask(__name__)
app.config.from_object(config.Config)

# Initialize database
models.db.init_app(app)
migrate = flaHIGHNOTE_API_KEY_PLACEHOLDER.Migrate(app, models.db)


# Helper function to get active Jira client
def get_jira_client():
    """Get Jira client from active configuration in database"""
    active_config = models.JiraConfiguration.query.filter_by(is_active=True).first()

    if active_config is None:
        return None

    return jira_client.JiraClient(
        jira_url=active_config.jira_url,
        email=active_config.email,
        api_token=active_config.api_token,
    )


@app.route("/")
def index():
    """Home page"""
    connection_status = None
    jira = get_jira_client()

    if jira is not None:
        connection_status = jira.test_connection()

    return flask.render_template("index.html", connection_status=connection_status)


@app.route("/projects")
def projects():
    """Display all projects"""
    jira = get_jira_client()
    if jira is None:
        flask.flash("Jira not configured. Please configure Jira settings.", "error")
        return flask.redirect(flask.url_for("settings"))

    projects_list = jira.get_projects()

    if isinstance(projects_list, dict) and "error" in projects_list:
        flask.flash(f"Error fetching projects: {projects_list['error']}", "error")
        projects_list = []
    else:
        # Cache projects in database
        for project_data in projects_list:
            db_helpers.cache_project(project_data)
        logger.info(f"Cached {len(projects_list)} projects")

    return flask.render_template("projects.html", projects=projects_list)


@app.route("/project/<project_key>")
def project_detail(project_key):
    """Display project details"""
    jira = get_jira_client()
    if jira is None:
        flask.flash("Jira not configured. Please configure Jira settings.", "error")
        return flask.redirect(flask.url_for("settings"))

    project = jira.get_project(project_key)

    if isinstance(project, dict) and "error" in project:
        flask.flash(f"Error fetching project: {project['error']}", "error")
        return flask.redirect(flask.url_for("projects"))
    else:
        # Cache project in database
        db_helpers.cache_project(project)
        logger.info(f"Cached project: {project_key}")

    return flask.render_template("project_detail.html", project=project)


@app.route("/issues")
@app.route("/issues/<project_key>")
def issues(project_key=None):
    """Display issues, optionally filtered by project"""
    jira = get_jira_client()
    if jira is None:
        flask.flash("Jira not configured. Please configure Jira settings.", "error")
        return flask.redirect(flask.url_for("settings"))

    # Get query parameters
    max_results = flask.request.args.get("max_results", 50, type=int)

    # Fetch issues
    issues_data = jira.get_issues(project_key=project_key, max_results=max_results)

    # Cache issues in database
    if "issues" in issues_data and len(issues_data["issues"]) > 0:
        cached_count = db_helpers.cache_multiple_issues(issues_data["issues"])
        logger.info(f"Cached {cached_count} issues")

    # Get project info if filtering by project
    project = None
    if project_key is not None and project_key != "":
        project = jira.get_project(project_key)
        if project is not None and (
            not isinstance(project, dict) or "error" not in project
        ):
            db_helpers.cache_project(project)

    return flask.render_template(
        "issues.html",
        issues=issues_data.get("issues", []),
        total=issues_data.get("total", 0),
        project=project,
        project_key=project_key,
    )


@app.route("/issue/<issue_key>")
def issue_detail(issue_key):
    """Display detailed information about a specific issue"""
    jira = get_jira_client()
    if jira is None:
        flask.flash("Jira not configured. Please configure Jira settings.", "error")
        return flask.redirect(flask.url_for("settings"))

    issue = jira.get_issue(issue_key)

    if isinstance(issue, dict) and "error" in issue:
        flask.flash(f"Error fetching issue: {issue['error']}", "error")
        return flask.redirect(flask.url_for("issues"))
    else:
        # Cache issue in database
        db_helpers.cache_issue(issue)
        logger.info(f"Cached issue: {issue_key}")

    # Get comments
    comments = jira.get_issue_comments(issue_key)

    return flask.render_template("issue_detail.html", issue=issue, comments=comments)


@app.route("/search")
def search():
    """Search issues using JQL"""
    jira = get_jira_client()
    if jira is None:
        flask.flash("Jira not configured. Please configure Jira settings.", "error")
        return flask.redirect(flask.url_for("settings"))

    jql = flask.request.args.get("jql", "")
    max_results = flask.request.args.get("max_results", 50, type=int)

    issues_data = None

    if jql is not None and jql != "":
        issues_data = jira.search_issues(jql=jql, max_results=max_results)

        # Cache search results
        if (
            issues_data is not None
            and "issues" in issues_data
            and len(issues_data["issues"]) > 0
        ):
            cached_count = db_helpers.cache_multiple_issues(issues_data["issues"])
            logger.info(f"Cached {cached_count} issues from search")

    return flask.render_template(
        "search.html",
        jql=jql,
        issues=issues_data.get("issues", []) if issues_data is not None else [],
        total=issues_data.get("total", 0) if issues_data is not None else 0,
    )


@app.route("/attachment/<attachment_id>")
def download_attachment(attachment_id):
    """Download attachment from Jira"""
    jira = get_jira_client()
    if jira is None:
        flask.flash("Jira not configured. Please configure Jira settings.", "error")
        return flask.redirect(flask.url_for("settings"))

    # Get attachment metadata
    attachment = jira.get_attachment(attachment_id)

    if isinstance(attachment, dict) and "error" in attachment:
        flask.flash(f"Error fetching attachment: {attachment['error']}", "error")
        return flask.redirect(flask.url_for("index"))

    # Get the content URL and filename
    content_url = attachment.get("content")
    filename = attachment.get("filename", "download")

    if content_url is None or content_url == "":
        flask.flash("Attachment content URL not found", "error")
        return flask.redirect(flask.url_for("index"))

    # Download the attachment content
    content, content_type = jira.download_attachment_content(content_url)

    if content is None:
        flask.flash("Failed to download attachment", "error")
        return flask.redirect(flask.url_for("index"))

    # Return the file
    return flask.send_file(
        io.BytesIO(content),
        mimetype=content_type,
        as_attachment=True,
        download_name=filename,
    )


@app.route("/api/test-connection")
def api_test_connection():
    """API endpoint to test connection"""
    jira = get_jira_client()
    if jira is None:
        return flask.jsonify({"success": False, "message": "Jira not configured"}), 500

    result = jira.test_connection()
    status_code = 200 if result.get("success") else 500

    return flask.jsonify(result), status_code


@app.route("/api/projects")
def api_projects():
    """API endpoint to get all projects"""
    jira = get_jira_client()
    if jira is None:
        return flask.jsonify({"error": "Jira not configured"}), 500

    projects_list = jira.get_projects()
    return flask.jsonify(projects_list)


@app.route("/api/issues")
def api_issues():
    """API endpoint to get issues"""
    jira = get_jira_client()
    if jira is None:
        return flask.jsonify({"error": "Jira not configured"}), 500

    project_key = flask.request.args.get("project")
    max_results = flask.request.args.get("max_results", 50, type=int)
    jql = flask.request.args.get("jql")

    issues_data = jira.get_issues(
        project_key=project_key, max_results=max_results, jql=jql
    )

    return flask.jsonify(issues_data)


@app.route("/api/issue/<issue_key>")
def api_issue(issue_key):
    """API endpoint to get a specific issue"""
    jira = get_jira_client()
    if jira is None:
        return flask.jsonify({"error": "Jira not configured"}), 500

    issue = jira.get_issue(issue_key)
    return flask.jsonify(issue)


# Settings routes
@app.route("/settings")
def settings():
    """Jira settings page"""
    active_config = models.JiraConfiguration.query.filter_by(is_active=True).first()
    all_configs = models.JiraConfiguration.query.order_by(
        models.JiraConfiguration.created_at.desc()
    ).all()

    return flask.render_template(
        "settings.html", active_config=active_config, configurations=all_configs
    )


@app.route("/api/settings/jira", methods=["POST"])
def create_jira_config():
    """Create a new Jira configuration"""
    try:
        data = flask.request.get_json()

        # Validate required fields
        required_fields = ["name", "jira_url", "email", "api_token"]
        for field in required_fields:
            if field not in data or data[field] == "":
                return flask.jsonify({"error": f"Missing required field: {field}"}), 400

        # If is_active is True, deactivate all other configs
        if data.get("is_active", False):
            models.JiraConfiguration.query.update(
                {models.JiraConfiguration.is_active: False}
            )

        # Create new configuration
        new_config = models.JiraConfiguration(
            name=data["name"],
            jira_url=data["jira_url"],
            email=data["email"],
            api_token=data["api_token"],
            project_key=data.get("project_key", ""),
            is_active=data.get("is_active", False),
        )

        models.db.session.add(new_config)
        models.db.session.commit()

        return flask.jsonify(
            {
                "message": "Configuration created successfully",
                "config": new_config.to_dict(),
            }
        ), 201

    except Exception as e:
        models.db.session.rollback()
        logger.error(f"Error creating Jira configuration: {e}")
        return flask.jsonify({"error": str(e)}), 500


@app.route("/api/settings/jira/<int:config_id>", methods=["GET"])
def get_jira_config(config_id):
    """Get a specific Jira configuration"""
    config = models.JiraConfiguration.query.get_or_404(config_id)
    return flask.jsonify(config.to_dict(include_token=True))


@app.route("/api/settings/jira/<int:config_id>", methods=["PUT"])
def update_jira_config(config_id):
    """Update a Jira configuration"""
    try:
        config = models.JiraConfiguration.query.get_or_404(config_id)
        data = flask.request.get_json()

        # Update fields
        if "name" in data:
            config.name = data["name"]
        if "jira_url" in data:
            config.jira_url = data["jira_url"]
        if "email" in data:
            config.email = data["email"]
        if "api_token" in data:
            config.api_token = data["api_token"]
        if "project_key" in data:
            config.project_key = data["project_key"]

        # Handle is_active
        if "is_active" in data and data["is_active"]:
            # Deactivate all other configs
            models.JiraConfiguration.query.filter(
                models.JiraConfiguration.id != config_id
            ).update({models.JiraConfiguration.is_active: False})
            config.is_active = True
        elif "is_active" in data and not data["is_active"]:
            config.is_active = False

        models.db.session.commit()

        return flask.jsonify(
            {
                "message": "Configuration updated successfully",
                "config": config.to_dict(),
            }
        )

    except Exception as e:
        models.db.session.rollback()
        logger.error(f"Error updating Jira configuration: {e}")
        return flask.jsonify({"error": str(e)}), 500


@app.route("/api/settings/jira/<int:config_id>", methods=["DELETE"])
def delete_jira_config(config_id):
    """Delete a Jira configuration"""
    try:
        config = models.JiraConfiguration.query.get_or_404(config_id)
        models.db.session.delete(config)
        models.db.session.commit()

        return flask.jsonify({"message": "Configuration deleted successfully"})

    except Exception as e:
        models.db.session.rollback()
        logger.error(f"Error deleting Jira configuration: {e}")
        return flask.jsonify({"error": str(e)}), 500


@app.route("/api/settings/jira/<int:config_id>/activate", methods=["POST"])
def activate_jira_config(config_id):
    """Activate a specific Jira configuration"""
    try:
        config = models.JiraConfiguration.query.get_or_404(config_id)

        # Deactivate all configs
        models.JiraConfiguration.query.update(
            {models.JiraConfiguration.is_active: False}
        )

        # Activate this one
        config.is_active = True
        models.db.session.commit()

        return flask.jsonify(
            {
                "message": f'Configuration "{config.name}" activated successfully',
                "config": config.to_dict(),
            }
        )

    except Exception as e:
        models.db.session.rollback()
        logger.error(f"Error activating Jira configuration: {e}")
        return flask.jsonify({"error": str(e)}), 500


@app.route("/api/settings/jira/test", methods=["POST"])
def test_jira_config():
    """Test a Jira configuration without saving it"""
    try:
        data = flask.request.get_json()

        # Validate required fields
        if "jira_url" not in data or "email" not in data or "api_token" not in data:
            return flask.jsonify({"error": "Missing required fields"}), 400

        # Create temporary Jira client
        test_jira = jira_client.JiraClient(
            jira_url=data["jira_url"], email=data["email"], api_token=data["api_token"]
        )

        # Test connection
        result = test_jira.test_connection()
        return flask.jsonify(result)

    except Exception as e:
        logger.error(f"Error testing Jira configuration: {e}")
        return flask.jsonify(
            {"success": False, "message": "Connection test failed", "error": str(e)}
        ), 500


# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return flask.render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal error: {error}")
    return flask.render_template("500.html"), 500


# Template filters
@app.template_filter("format_date")
def format_date(date_string):
    """Format ISO date string to readable format"""
    if date_string is None or date_string == "":
        return "N/A"

    try:
        from datetime import datetime

        dt = datetime.fromisoformat(date_string.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return date_string


if __name__ == "__main__":
    with app.app_context():
        jira = get_jira_client()
        if jira is None:
            logger.warning(
                "No active Jira configuration found. Please configure Jira at http://127.0.0.1:5000/settings"
            )
        else:
            logger.info("Project Hub running at http://127.0.0.1:5000")

    app.run(debug=config.Config.DEBUG, host="0.0.0.0", port=5000)
