"""
Driver for Jira Bug Regression Multi-Agent Pipeline
"""

from datetime import datetime
from pathlib import Path

from src.graph.bug_regression.graph import build_graph
from src.core import get_logger


logger = get_logger("jira_bug_regression_driver")


ROOT = Path(__file__).resolve().parents[3]

OUT_DIR = ROOT / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def main():

    logger.info("🚀 Starting Jira Bug Regression pipeline")

    app = build_graph()

    init_state = {

        # Jira
        "bugs": [],

        # Regression coverage
        "covered_bugs": [],
        "uncovered_bugs": [],
        "generation_failed_bugs": [],

        "next_agent": "",

        # Generated tests
        "test_cases": [],

        # TestRail
        "testrail_case_ids": [],

        # Slack
        "slack_message_ts": None,

        # RAG
        "retrieved_context": None,
        "conversation_history": None,

        # Final report
        "summary_report": "",

        # Pipeline tracking
        "steps_completed": [],

        # Errors
        "errors": []
    }

    logger.info("=" * 70)

    final_state = app.invoke(init_state)

    if final_state.get("summary_report"):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        report_path = OUT_DIR / f"report_{timestamp}.txt"
        report_path.write_text(final_state["summary_report"])
        logger.info(f"📄 Report written to {report_path}")

    print("\nGENERATED REGRESSION TESTS:")
    print(final_state.get("test_cases") or "None")

    print("\nCOVERED:")
    print(final_state.get("covered_bugs") or "None")

    print("\nUNCOVERED:")
    print(final_state.get("uncovered_bugs") or "None")

    print("\nTESTRAIL CASE IDs:")
    print(final_state.get("testrail_case_ids") or "None")

    print("\nSTEPS COMPLETED:")
    print(final_state.get("steps_completed"))

    if final_state.get("errors"):
        print("\nERRORS:")
        print(final_state["errors"])

    if final_state.get("summary_report"):
        print("\nFINAL REPORT:")
        print(final_state["summary_report"])


if __name__ == "__main__":
    main()