"""
Shared state for Jira Bug Regression Multi-Agent System
"""
from typing import TypedDict, List, Optional


class JiraTestState(TypedDict):

    # Jira input
    bugs: List[dict]

    # Regression coverage
    covered_bugs: List[dict]
    uncovered_bugs: List[dict]
    generation_failed_bugs: List[dict]

    # Generated regression tests
    test_cases: Optional[List[dict]]

    # TestRail results
    testrail_case_ids: Optional[List[int]]

    # Slack result
    slack_message_ts: Optional[str]

    # RAG
    retrieved_context: Optional[str]
    conversation_history: Optional[list]

    # Supervisor / routing
    next_agent: str

    # Final output + tracking
    summary_report: str
    steps_completed: List[str]
    errors: List[str]