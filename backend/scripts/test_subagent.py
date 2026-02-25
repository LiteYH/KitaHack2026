"""Quick test script to debug subagent invocation."""
import os
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

from app.core.config import settings

if settings.google_api_key:
    os.environ["GOOGLE_API_KEY"] = settings.google_api_key
if settings.tavily_api_key:
    os.environ["TAVILY_API_KEY"] = settings.tavily_api_key

from app.agents.competitor_monitoring.agent import create_competitor_monitoring_agent


async def test():
    # Test: Full agent with production system prompt
    print("=== TEST: Full create_competitor_monitoring_agent ===")
    agent = create_competitor_monitoring_agent()
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "Check which competitors I am currently monitoring"}]},
        config={"configurable": {"thread_id": "test_full_001"}},
    )
    msgs = result.get("messages", [])
    print(f"Got {len(msgs)} messages")
    for i, m in enumerate(msgs):
        t = type(m).__name__
        c = getattr(m, "content", "")
        tc = getattr(m, "tool_calls", [])
        clen = len(c) if isinstance(c, str) else len(str(c)) if c else 0
        tc_names = []
        for tc_item in tc:
            name = tc_item.get("name", "?") if isinstance(tc_item, dict) else getattr(tc_item, "name", "?")
            tc_names.append(name)
        print(f"  [{i}] {t}: content_len={clen}, tool_calls={tc_names if tc_names else 0}")
    for m in reversed(msgs):
        if type(m).__name__ == "AIMessage" and getattr(m, "content", ""):
            print(f"FINAL ({len(m.content)} chars): {m.content[:400]}")
            return
    print("NO AI MESSAGE WITH CONTENT")


if __name__ == "__main__":
    asyncio.run(test())
