import os
import requests
from datetime import datetime
from typing import Dict, Any, Optional
from src.utils.logger import get_logger

logger = get_logger(__name__)


class JiraCloudClient:
    def __init__(self):
        self.base_url = os.getenv("JIRA_BASE_URL", "").rstrip('/')
        self.email = os.getenv("JIRA_EMAIL", "")
        self.api_token = os.getenv("JIRA_API_TOKEN", "")
        self.project_key = os.getenv("JIRA_PROJECT_KEY", "MLP")

        if not self.base_url or not self.email or not self.api_token:
            logger.warning("Jira credentials not configured. Integration disabled.")
            self.enabled = False
        else:
            self.enabled = True
            self.auth = (self.email, self.api_token)
            self.headers = {"Content-Type": "application/json", "Accept": "application/json"}
            logger.info(f"Jira client initialized for {self.base_url}")

    def test_connection(self) -> bool:
        if not self.enabled:
            return False
        try:
            resp = requests.get(f"{self.base_url}/rest/api/3/myself", auth=self.auth, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                user = resp.json()
                logger.info(f"✓ Connected to Jira as: {user.get('displayName')}")
                return True
            logger.error(f"Connection failed: {resp.status_code}")
            return False
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False

    def create_issue(self, summary: str, issue_type: str, description: str, labels: Optional[list] = None) -> Dict[str, Any]:
        if not self.enabled:
            return {"success": False, "error": "Jira not configured"}

        payload = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": summary,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [{
                        "type": "paragraph",
                        "content": [{"type": "text", "text": description}]
                    }]
                },
                "issuetype": {"name": issue_type}
            }
        }
        if labels:
            payload["fields"]["labels"] = labels

        try:
            resp = requests.post(f"{self.base_url}/rest/api/3/issue", json=payload, auth=self.auth, headers=self.headers, timeout=30)
            if resp.status_code == 201:
                result = resp.json()
                logger.info(f"✓ Issue created: {result['key']} - {summary}")
                return {"success": True, "key": result["key"], "url": f"{self.base_url}/browse/{result['key']}"}
            logger.error(f"Failed: {resp.text}")
            return {"success": False, "error": resp.text}
        except Exception as e:
            logger.error(f"Error: {e}")
            return {"success": False, "error": str(e)}

    def create_pipeline_run_issue(self, run_id: str, status: str, metrics: Dict[str, Any], duration_seconds: float) -> Dict[str, Any]:
        # Фильтруем только числовые метрики
        numeric_metrics = {}
        for k, v in metrics.items():
            if isinstance(v, (int, float)):
                numeric_metrics[k] = v
            else:
                logger.info(f"Skipping non-numeric metric: {k}={v}")
        
        metrics_str = "\n".join([f"- {k}: {v:.4f}" for k, v in numeric_metrics.items()])
        
        description = f"""**Pipeline Run:** {run_id}
**Status:** {status.upper()}
**Duration:** {duration_seconds:.2f}s
**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**Model Metrics:**
{metrics_str}"""

        return self.create_issue(
            summary=f"Pipeline Run: {run_id} - {status.upper()}",
            issue_type="ML Experiment",
            description=description,
            labels=["ml-pipeline", status]
        )