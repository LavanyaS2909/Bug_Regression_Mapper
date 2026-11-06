"""
Jira Bug → Regression Test → TestRail → Slack Multi-Agent Graph
"""

from langgraph.graph import StateGraph, END

from .state import JiraTestState

from .supervisor import (
    supervisor_router,
    route_next,
    supervisor_compile
)

from .agents import (
    jira_bugsfetcher_agent,
    regression_checker,
    regression_test_generator,
    testrail_pusher_agent,
    slack_notifier_agent,
)

from src.core import get_logger


logger = get_logger("jira_bug_regression_graph")


def build_graph():
    """Build Jira Bug Regression graph."""

    logger.info("Building Jira Bug Regression graph...")

    workflow = StateGraph(JiraTestState)

    # ---------------------------------------------------------
    # Add nodes
    # ---------------------------------------------------------

    workflow.add_node(
        "supervisor",
        supervisor_router
    )

    workflow.add_node(
        "jira_bugsfetcher",
        jira_bugsfetcher_agent
    )

    workflow.add_node(
        "regression_checker",
        regression_checker
    )

    workflow.add_node(
        "regression_test_generator",
        regression_test_generator
    )

    workflow.add_node(
        "testrail_pusher",
        testrail_pusher_agent
    )

    workflow.add_node(
        "slack_notifier",
        slack_notifier_agent
    )

    workflow.add_node(
        "supervisor_compile",
        supervisor_compile
    )

    # ---------------------------------------------------------
    # Entry point
    # ---------------------------------------------------------

    workflow.set_entry_point("supervisor")

    # ---------------------------------------------------------
    # Supervisor decides what happens next
    # ---------------------------------------------------------

    workflow.add_conditional_edges(
        "supervisor",
        route_next,
        {
            "jira_bugsfetcher": "jira_bugsfetcher",
            "regression_checker": "regression_checker",
            "regression_test_generator": "regression_test_generator",
            "testrail_pusher": "testrail_pusher",
            "slack_notifier": "slack_notifier",
            "supervisor_compile": "supervisor_compile",
            "FINISH": END,
        }
    )

    # ---------------------------------------------------------
    # Every agent returns control to supervisor
    # ---------------------------------------------------------

    workflow.add_edge(
        "jira_bugsfetcher",
        "supervisor"
    )

    workflow.add_edge(
        "regression_checker",
        "supervisor"
    )

    workflow.add_edge(
        "regression_test_generator",
        "supervisor"
    )

    workflow.add_edge(
        "testrail_pusher",
        "supervisor"
    )

    workflow.add_edge(
        "slack_notifier",
        "supervisor"
    )

    # ---------------------------------------------------------
    # Final report → END
    # ---------------------------------------------------------

    workflow.add_edge(
        "supervisor_compile",
        END
    )

    logger.info("✅ Graph built successfully")

    return workflow.compile()