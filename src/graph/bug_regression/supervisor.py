"""
Supervisor - Routes and coordinates Jira Bug Regression pipeline
"""

from src.core import get_logger

logger = get_logger("supervisor")


def supervisor_router(state):
    """Passthrough node used only for routing."""
    return state


def route_next(state):
    """Supervisor decides which node should execute next."""

    steps = state.get("steps_completed", [])

    # ---------------------------------------------------------
    # 1. Fetch Jira bugs
    # ---------------------------------------------------------
    if "jira_bugsfetcher" not in steps:
        logger.info("→ Supervisor: jira_bugsfetcher")
        return "jira_bugsfetcher"

    # ---------------------------------------------------------
    # 2. Check existing regression coverage
    # ---------------------------------------------------------
    if "regression_checker" not in steps:
        logger.info("→ Supervisor: regression_checker")
        return "regression_checker"

    # ---------------------------------------------------------
    # 3. Generate regression tests ONLY if uncovered bugs exist
    # ---------------------------------------------------------
    uncovered_bugs = state.get("uncovered_bugs") or []

    if uncovered_bugs and "regression_test_generator" not in steps:
        logger.info(
            f"→ Supervisor: {len(uncovered_bugs)} uncovered bug(s). "
            "Generating regression tests."
        )
        return "regression_test_generator"

    # ---------------------------------------------------------
    # 4. Push generated tests ONLY if test cases exist
    # ---------------------------------------------------------
    test_cases = state.get("test_cases") or []

    if test_cases and "testrail_pusher" not in steps:
        logger.info(
            f"→ Supervisor: {len(test_cases)} test case(s). "
            "Pushing to TestRail."
        )
        return "testrail_pusher"

    # ---------------------------------------------------------
    # 5. Send Slack summary exactly once
    # ---------------------------------------------------------
    if "slack_notifier" not in steps:
        logger.info("→ Supervisor: slack_notifier")
        return "slack_notifier"

    # ---------------------------------------------------------
    # 6. Compile final report exactly once
    # ---------------------------------------------------------
    if "supervisor_compile" not in steps:
        logger.info("→ Supervisor: supervisor_compile")
        return "supervisor_compile"

    # ---------------------------------------------------------
    # 7. End workflow
    # ---------------------------------------------------------
    logger.info("→ Supervisor: FINISH")
    return "FINISH"


def supervisor_compile(state):
    """Compile final regression coverage report."""

    logger.info("📄 Supervisor compiling final report...")

    bugs = state.get("bugs", [])
    covered_bugs = state.get("covered_bugs", [])
    generation_failed_bugs = state.get("generation_failed_bugs", [])
    test_cases = state.get("test_cases") or []
    testrail_ids = state.get("testrail_case_ids") or []
    slack_ts = state.get("slack_message_ts", "N/A")

    total_bugs = len(bugs)
    already_covered = len(covered_bugs)
    newly_created = len(test_cases)
    final_coverage = already_covered + newly_created

    newly_covered_keys = [
        tc.get("bug_key", "N/A")
        for tc in test_cases
    ]

    report = f"""
======================================================================
           JIRA BUG REGRESSION COVERAGE REPORT
======================================================================

Total bugs analysed       : {total_bugs}
Already covered (skipped) : {already_covered}
New regression tests      : {newly_created}

Skipped bugs:
{", ".join(bug["key"] for bug in covered_bugs) or "None"}

Generation failed:
{", ".join(
    bug.get("key", "N/A")
    for bug in generation_failed_bugs
) or "None"}

Newly covered bugs:
{", ".join(newly_covered_keys) or "None"}

TestRail Case IDs:
{testrail_ids or "None"}

Coverage:
{final_coverage} of {total_bugs} bugs now have regression coverage.

Slack timestamp:
{slack_ts}
"""

    logger.info("✅ Final report compiled")

    return {
        "summary_report": report,
        # IMPORTANT: mark compile as completed
        "steps_completed": state["steps_completed"] + ["supervisor_compile"]
    }