"""
Slack Notifier Agent - Sends regression coverage summary to Slack
"""
from src.core import get_logger
from src.integrations import SlackClient

logger = get_logger("slack_notifier_agent")

client = SlackClient()


def slack_notifier_agent(state):
    """Send regression coverage summary to Slack."""

    logger.info("💬 Slack Notifier running...")

    bugs = state.get("bugs", [])
    covered_bugs = state.get("covered_bugs", [])
    test_cases = state.get("test_cases") or []
    testrail_ids = state.get("testrail_case_ids") or []

    # Bugs for which new regression tests were generated
    new_regression_bugs = []

    for test_case in test_cases:
        bug_key = test_case.get("bug_key")

        if bug_key:
            new_regression_bugs.append({
                "key": bug_key
            })

    try:
        message = client.build_regression_summary(
            total_bugs=len(bugs),
            covered_bugs=covered_bugs,
            new_regression_bugs=new_regression_bugs,
            testrail_ids=testrail_ids
        )

        logger.info(f"Slack message:\n{message}")

        result = client.post_message(message)
        ts = result.get("ts", "")

        logger.info(f"✅ Slack message sent (ts: {ts})")

        return {
            "slack_message_ts": ts,
            "steps_completed": state["steps_completed"] + [
                "slack_notifier"
            ]
        }

    except Exception as e:
        logger.error(f"❌ Slack Notifier failed: {e}")

        return {
            "slack_message_ts": "",
            "steps_completed": state["steps_completed"] + [
                "slack_notifier"
            ],
            "errors": state["errors"] + [
                f"Slack Notifier: {e}"
            ]
        }