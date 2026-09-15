import requests
import requests.auth
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JiraClient:
    """
    A client for interacting with Jira REST API
    """

    def __init__(self, jira_url, email, api_token):
        """
        Initialize the Jira client

        Args:
            jira_url (str): Jira instance URL (e.g., 'company.atlassian.net')
            email (str): User email for authentication
            api_token (str): API token for authentication
        """
        self.base_url = f"https://{jira_url}"
        self.auth = requests.auth.HTTPBasicAuth(email, api_token)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def _make_request(
        self, method, endpoint, params=None, json_data=None, api_version="3"
    ):
        """
        Make an HTTP request to Jira API

        Args:
            method (str): HTTP method (GET, POST, etc.)
            endpoint (str): API endpoint
            params (dict): Query parameters
            json_data (dict): JSON body for POST/PUT requests
            api_version (str): API version - "3" for REST API v3, "agile" for Agile API

        Returns:
            dict: JSON response or None if error
        """
        if api_version == "agile":
            url = f"{self.base_url}/rest/agile/1.0/{endpoint}"
        else:
            url = f"{self.base_url}/rest/api/{api_version}/{endpoint}"

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                auth=self.auth,
                params=params,
                json=json_data,
                timeout=30,
            )

            response.raise_for_status()

            # Handle empty responses
            if (
                response.status_code == 204
                or response.content is None
                or len(response.content) == 0
            ):
                return {"success": True}

            return response.json()

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP Error: {e}")
            error_text = e.response.text if e.response is not None else "No response"
            logger.error(f"Response: {error_text}")
            status_code = e.response.status_code if e.response is not None else None
            return {"error": str(e), "status_code": status_code, "details": error_text}
        except requests.exceptions.RequestException as e:
            logger.error(f"Request Error: {e}")
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected Error: {e}")
            return {"error": str(e)}

    def test_connection(self):
        """
        Test the connection to Jira

        Returns:
            dict: Connection status and user info
        """
        result = self._make_request("GET", "myself")

        if result is not None and "error" not in result:
            return {
                "success": True,
                "message": "Connected to Jira successfully!",
                "user": result.get("displayName", "Unknown"),
                "email": result.get("emailAddress", "Unknown"),
            }
        else:
            error_message = "Unknown error"
            if result is not None:
                error_message = result.get("error", "Unknown error")
            return {
                "success": False,
                "message": "Failed to connect to Jira",
                "error": error_message,
            }

    def get_projects(self):
        """
        Get all projects accessible to the user

        Returns:
            list: List of projects
        """
        result = self._make_request("GET", "project")

        if result is not None and "error" not in result:
            return result
        else:
            logger.error(f"Error fetching projects: {result}")
            return []

    def get_project(self, project_key):
        """
        Get details of a specific project

        Args:
            project_key (str): Project key (e.g., 'PROJ')

        Returns:
            dict: Project details
        """
        return self._make_request("GET", f"project/{project_key}")

    def get_boards(self, project_key=None):
        """
        Get all boards, optionally filtered by project

        Args:
            project_key (str): Filter by project key (optional)

        Returns:
            list: List of boards
        """
        params = {}
        if project_key is not None and project_key != "":
            params["projectKeyOrId"] = project_key

        result = self._make_request("GET", "board", params=params, api_version="agile")

        if result is not None and "error" not in result:
            return result.get("values", [])
        else:
            logger.error(f"Error fetching boards: {result}")
            return []

    def get_board_issues(self, board_id, max_results=50):
        """
        Get issues from a specific board using Agile API

        Args:
            board_id (int): Board ID
            max_results (int): Maximum number of results to return

        Returns:
            dict: Issues and metadata
        """
        params = {"maxResults": max_results}
        result = self._make_request(
            "GET", f"board/{board_id}/issue", params=params, api_version="agile"
        )

        if result is not None and "error" not in result:
            return {
                "total": result.get("total", 0),
                "issues": result.get("issues", []),
                "max_results": result.get("maxResults", max_results),
            }
        else:
            logger.error(f"Error fetching board issues: {result}")
            error_value = None
            if result is not None:
                error_value = result.get("error")
            return {"total": 0, "issues": [], "error": error_value}

    def get_issues(self, project_key=None, max_results=50, jql=None):
        """
        Get issues from Jira

        Args:
            project_key (str): Filter by project key (optional)
            max_results (int): Maximum number of results to return
            jql (str): Custom JQL query (optional)

        Returns:
            dict: Issues and metadata
        """
        # If using Agile API (no custom JQL specified)
        if jql is None or jql == "":
            if project_key is not None and project_key != "":
                boards = self.get_boards(project_key=project_key)
            else:
                boards = self.get_boards()

            if boards is not None and len(boards) > 0:
                # If no project specified, get issues from all boards
                if project_key is None or project_key == "":
                    all_issues = []
                    total = 0
                    for board in boards:
                        board_id = board.get("id")
                        logger.info(f"Fetching issues from board {board_id}")
                        board_issues = self.get_board_issues(
                            board_id, max_results=max_results
                        )
                        all_issues.extend(board_issues.get("issues", []))
                        total += board_issues.get("total", 0)

                    return {
                        "total": total,
                        "issues": all_issues[:max_results],  # Limit to max_results
                        "max_results": max_results,
                    }
                else:
                    # Use the first board found for this project
                    board_id = boards[0].get("id")
                    logger.info(f"Using Agile API for board {board_id}")
                    return self.get_board_issues(board_id, max_results=max_results)

        # Fallback to JQL search (for custom JQL queries)
        if jql is not None and jql != "":
            # Use custom JQL
            search_jql = jql
        elif project_key is not None and project_key != "":
            # Filter by project
            search_jql = f"project = {project_key} ORDER BY created DESC"
        else:
            # Get all issues assigned to current user (avoids unbounded query error)
            search_jql = "assignee = currentUser() OR reporter = currentUser() ORDER BY created DESC"

        # Using the new /search/jql endpoint with POST and JSON body
        json_data = {
            "jql": search_jql,
            "maxResults": max_results,
            # Include project + other fields we persist locally
            "fields": [
                "summary",
                "status",
                "assignee",
                "priority",
                "created",
                "updated",
                "issuetype",
                "project",
                "description",
                "reporter",
            ],
        }

        result = self._make_request("POST", "search/jql", json_data=json_data)

        if result is not None and "error" not in result:
            # The new API returns 'values' instead of 'issues'
            issues = result.get("values", [])
            return {
                "total": result.get("total", 0),
                "issues": issues,
                "max_results": result.get("maxResults", max_results),
            }
        else:
            logger.error(f"Error fetching issues: {result}")
            error_value = None
            if result is not None:
                error_value = result.get("error")
            return {"total": 0, "issues": [], "error": error_value}

    def get_issue(self, issue_key):
        """
        Get detailed information about a specific issue

        Args:
            issue_key (str): Issue key (e.g., 'PROJ-123')

        Returns:
            dict: Issue details
        """
        return self._make_request("GET", f"issue/{issue_key}")

    def get_issue_comments(self, issue_key):
        """
        Get comments for a specific issue

        Args:
            issue_key (str): Issue key (e.g., 'PROJ-123')

        Returns:
            dict: Comments data
        """
        result = self._make_request("GET", f"issue/{issue_key}/comment")

        if result is not None and "error" not in result:
            return result.get("comments", [])
        else:
            return []

    def search_issues(self, jql, max_results=50):
        """
        Search issues using JQL (Jira Query Language)

        Args:
            jql (str): JQL query string
            max_results (int): Maximum number of results

        Returns:
            dict: Search results
        """
        return self.get_issues(jql=jql, max_results=max_results)

    def get_statuses(self):
        """
        Get all available issue statuses

        Returns:
            list: List of statuses
        """
        result = self._make_request("GET", "status")

        if result is not None and "error" not in result:
            return result
        else:
            return []

    def get_priorities(self):
        """
        Get all available issue priorities

        Returns:
            list: List of priorities
        """
        result = self._make_request("GET", "priority")

        if result is not None and "error" not in result:
            return result
        else:
            return []

    def get_issue_types(self):
        """
        Get all available issue types

        Returns:
            list: List of issue types
        """
        result = self._make_request("GET", "issuetype")

        if result is not None and "error" not in result:
            return result
        else:
            return []

    def get_users_assignable_to_project(self, project_key):
        """
        Get users that can be assigned to issues in a project

        Args:
            project_key (str): Project key

        Returns:
            list: List of users
        """
        params = {"project": project_key}

        result = self._make_request("GET", "user/assignable/search", params=params)

        if result is not None and "error" not in result:
            return result
        else:
            return []

    def get_attachment(self, attachment_id):
        """
        Get attachment metadata

        Args:
            attachment_id (str): Attachment ID

        Returns:
            dict: Attachment metadata
        """
        return self._make_request("GET", f"attachment/{attachment_id}")

    def download_attachment_content(self, content_url):
        """
        Download attachment content from URL

        Args:
            content_url (str): URL to download the attachment from

        Returns:
            tuple: (content_bytes, content_type) or (None, None) on error
        """
        try:
            response = requests.get(content_url, auth=self.auth, timeout=30)
            response.raise_for_status()

            content_type = response.headers.get(
                "Content-Type", "application/octet-stream"
            )
            return response.content, content_type
        except Exception as e:
            logger.error(f"Error downloading attachment: {e}")
            return None, None
