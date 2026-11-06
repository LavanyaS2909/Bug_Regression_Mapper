import os
from src.core import get_logger
from src.integrations import TestRailClient

logger = get_logger("regression_checker_agent")

client = TestRailClient()

def regression_checker(state):
    logger.info(" Regression Checker running...")
    bugs = state.get("bugs", [])
    section_id = int(os.getenv("TESTRAIL_SECTION_ID", 1))
    testrail_data = client.get_cases(section_id)
    existing_cases = testrail_data.get("cases", [])
    covered_bugs = []
    uncovered_bugs = []
    for bug in bugs:
        bug_key = bug["key"]
        covered = any(
            bug_key in testrail_case.get("title", "")
            for testrail_case in existing_cases
        )
        if covered:
            covered_bugs.append(bug)
        else:
            uncovered_bugs.append(bug)

    return {
        "covered_bugs": covered_bugs,
        "uncovered_bugs": uncovered_bugs,
        "steps_completed": state["steps_completed"] + ["regression_checker"]
    }

