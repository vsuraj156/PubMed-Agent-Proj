import json
from datetime import datetime
import anthropic
from dotenv import load_dotenv

load_dotenv()

from .pubmed_tools import (
    pubmed_search_tool,
    clinical_guidelines_tool,
    recent_research_tool,
    TOOL_MAPPING
)

CLIENT = anthropic.Anthropic()

def clinical_research_agent(
    clinical_question: str,
    model: str = "claude-haiku-4-5-20251001",
    max_turns: int = 10
) -> str:

    print("=" * 60)
    print("CLINICAL RESEARCH AGENT")
    print("=" * 60)
    print(f"Question: {clinical_question}\n")

    system_prompt = f"""You are an expert clinical research assistant with access to PubMed, the world's largest biomedical literature database.

    Your capabilities:
    - search_pubmed: General medical literature search
    - search_clinical_guidelines: Find evidence-based clinical practice guidelines, systematic reviews, and meta-analyses
    - search_recent_research: Find cutting-edge research from recent years

    Your responsibilities:
    1. Search medical literature comprehensively using appropriate tools
    2. Synthesize findings into evidence-based recommendations
    3. Always cite sources with PMID numbers and URLs
    4. Distinguish between different levels of evidence (guidelines vs. individual studies)
    5. Note any conflicting findings or limitations
    6. Use appropriate medical terminology
    7. Organize findings clearly with sections

    Current date: {datetime.now().strftime('%Y-%m-%d')}

    Format your final response as a structured research report with:
    - Executive Summary
    - Key Findings (with citations)
    - Evidence-Based Recommendations
    - Limitations & Gaps
    - References
    """

    tools = [pubmed_search_tool, clinical_guidelines_tool, recent_research_tool]
    messages = [{"role": "user", "content": clinical_question}]

    for turn in range(max_turns):
        print(f"Turn {turn + 1}")

        response = CLIENT.messages.create(
            model=model,
            max_tokens=4096,
            system=system_prompt,
            messages=messages,
            tools=tools,
        )

        # Append assistant response to messages
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            print("\n" + "=" * 60)
            print("RESEARCH COMPLETE")
            print("=" * 60)
            # Extract text from response content blocks
            return next(
                (block.text for block in response.content if hasattr(block, "text")),
                ""
            )

        if response.stop_reason != "tool_use":
            break

        # Process tool calls and collect all results for a single user turn
        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue

            tool_name = block.name
            args = block.input

            print(f"  {tool_name}")
            print(f"     Query: {args}")

            try:
                tool_func = TOOL_MAPPING[tool_name]
                result = tool_func(**args)

                if "error" in result:
                    print(f"     Error: {result['error']}")
                else:
                    print(f"     Found {result.get('count', 0)} articles")

            except Exception as e:
                result = {"error": str(e)}
                print(f"     Exception: {e}")

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": json.dumps(result),
            })

        messages.append({"role": "user", "content": tool_results})
        print()

    return "Max research turns reached. Consider asking a more specific question."


def test():
    question = "What are the current treatment recommendations for type 2 diabetes in adults?"
    result = clinical_research_agent(question)
    print("\n" + result)
    return result

if __name__ == "__main__":
    test()
