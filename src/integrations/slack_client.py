"""
Slack Client - Sends messages to Slack via Web API
"""
import os
import httpx
from dotenv import load_dotenv

load_dotenv()


class SlackClient:

    def __init__(self):
        self.base_url = os.getenv(
            "SLACK_BASE_URL",
            "http://localhost:4003"
        )
        self.token = os.getenv("SLACK_TOKEN")
        self.channel = os.getenv(
            "SLACK_CHANNEL",
            "qa-reports"
        )
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def post_message(self, text: str) -> dict:
        """Send a plain text message to the configured Slack channel."""

        url = f"{self.base_url}/api/chat.postMessage"

        payload = {
            "channel": self.channel,
            "text": text
        }

        response = httpx.post(
            url,
            json=payload,
            headers=self.headers
        )

        response.raise_for_status()

        data = response.json()

        if not data.get("ok"):
            raise Exception(
                f"Slack API error: {data.get('error')}"
            )

        return data

    def build_regression_summary(
        self,
        total_bugs: int,
        covered_bugs: list,
        new_regression_bugs: list,
        testrail_ids: list
    ) -> str:
        """Format regression coverage summary."""

        covered_keys = [
            bug.get("key")
            for bug in covered_bugs
        ]

        new_keys = [
            bug.get("key")
            for bug in new_regression_bugs
        ]

        coverage_count = (
            len(covered_bugs) +
            len(new_regression_bugs)
        )

        skipped_str = (
            ", ".join(covered_keys)
            if covered_keys
            else "None"
        )

        new_str = (
            ", ".join(new_keys)
            if new_keys
            else "None"
        )

        ids_str = (
            ", ".join(str(i) for i in testrail_ids)
            if testrail_ids
            else "None"
        )

        return (
            f"*Jira Bug Regression Coverage Report*\n\n"
            f"Total bugs analysed      : {total_bugs}\n"
            f"Already covered (skipped): {len(covered_bugs)}\n"
            f"Skipped bugs             : {skipped_str}\n\n"
            f"New regression tests     : "
            f"{len(new_regression_bugs)}\n"
            f"Newly covered bugs       : {new_str}\n"
            f"TestRail Case IDs        : [{ids_str}]\n\n"
            f"*Coverage: {coverage_count} of {total_bugs} "
            f"bugs now have regression coverage*"
        )