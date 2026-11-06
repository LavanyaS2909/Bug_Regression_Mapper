from src.core import get_logger
from src.integrations import JiraClient

logger = get_logger("jira_bugsfetcher_agent")

client = JiraClient()


def jira_bugsfetcher_agent(state):
    logger.info("🔍 Jira Bugs Fetcher running...")

    try:
        bugs = client.search_bugs()

        logger.info(f"✅ Fetched {len(bugs)} Jira bugs")

        return {
            "bugs": bugs,
            "steps_completed": state["steps_completed"] + ["jira_bugsfetcher"]
        }

    except Exception as e:
        logger.error(f" Jira Bug Fetcher failed: {e}")
        return {
            "bugs": [],
            "steps_completed": state["steps_completed"] + ["jira_bug_fetcher"],
            "errors": state["errors"] + [f"Jira Bug Fetcher: {e}"]
        }