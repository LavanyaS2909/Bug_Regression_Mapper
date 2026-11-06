import json

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.core import get_logger, get_langchain_llm
from src.core import search_vector_store

logger = get_logger("regression_test_generator")
llm = get_langchain_llm()

prompt_template = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are a QA regression test generator.

Generate exactly ONE regression test case for the Jira bug provided.

Rules:

1. The title MUST follow this format:
   REG — [BUG_KEY] — [short scenario description]

2. Use the bug's exact Steps to Reproduce as the test steps.

3. Use the bug's Expected behavior as the expected result.

4. Do not invent, remove, or modify the reproduction steps.

5. Do not invent expected behavior.

6. Use the bug priority.

7. Return ONLY valid JSON.

IMPORTANT:
- Do not use Markdown code fences.
- Do not add any text before or after the JSON.
- The response must contain all four fields.

JSON format:

{{
  "title": "...",
  "steps": ["...", "..."],
  "expected": "...",
  "priority": "..."
}}
"""
    ),
    (
        "user",
        "{bug_context}"
    )
])

parser = StrOutputParser()

chain = prompt_template | llm | parser
def regression_test_generator(state):
    """Generate regression tests for uncovered Jira bugs using RAG + LLM."""

    logger.info("🤖 Regression Test Generator running...")

    uncovered_bugs = state.get("uncovered_bugs", [])
    test_cases = []
    generation_failed_bugs = []
    for bug in uncovered_bugs:
        bug_key = bug.get("key", "")
        summary = bug.get("summary", "")
        description = bug.get("description_text", "")
        priority = bug.get("priority", "Medium")

        logger.info(f"Generating regression test for {bug_key}...")
        results = search_vector_store(
            query=f"regression test writing standards for: {summary}",
            top_k=3
        )

        context_parts = []

        for doc, score in results:
            source = doc.metadata.get("source", "Unknown").split("/")[-1]

            context_parts.append(
                f"[Source: {source}]\n{doc.page_content}"
            )

        rag_context = "\n---\n".join(context_parts)
        bug_context = f"""
        Bug Key:
        {bug_key}

        Bug Summary:
        {summary}

        Bug Priority:
        {priority}

        Bug Description:
        {description}

        ---

        Regression Test Writing Standards from RAG:
        {rag_context}
        """
        try:
            response = chain.invoke({
                "bug_context": bug_context
            })
            logger.info(f"LLM RESPONSE FOR {bug_key}:\n{response}")
            response = response.strip()

            try:
                test_case = json.loads(response)
            except json.JSONDecodeError:
                start = response.find("{")
                end = response.rfind("}") + 1
                test_case = json.loads(response[start:end])
            test_case["bug_key"] = bug_key
            test_cases.append(test_case)

            logger.info(
                f"✅ Regression test generated for {bug_key}"
            )

        except Exception as e:
            logger.error(
                f"❌ Failed to generate regression test for {bug_key}: {e}"
            )
            generation_failed_bugs.append({
                "key": bug_key,
                "summary": summary,
                "error": str(e)
            })
            if "response" in locals():
                logger.error(
                    f"LLM RESPONSE FOR {bug_key}:\n{response}"
                )
    return {
                "test_cases": test_cases,
                "generation_failed_bugs": generation_failed_bugs,
                "retrieved_context": rag_context,
                "steps_completed": state["steps_completed"] + [
                    "regression_test_generator"
                ]
            }