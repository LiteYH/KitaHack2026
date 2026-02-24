from typing import Optional
from langchain.tools import tool
from app.services.rag_service import rag_service

@tool
def generate_content(user_input: str) -> str:
    """
    Generate high-performing social media content using RAG examples.
    
    :param user_input: Description
    :type user_input: str
    :return: content post
    :rtype: str
    """

    intent = rag_service.extract_intent(user_input)

    examples = rag_service.get_examples(
        sentiment=intent["sentiment"],
        keywords=intent["keywords"],
        platform = intent["platform"],
        top_k = 3
    )

    best_time = rag_service.get_best_posting_time(
        platform=intent["platform"]
    )

    formatted_examples = rag_service.format_examples_for_prompt(examples)

    response = f"""
        ### High-Performing Examples
        {formatted_examples}

        ### Scheduling Insight
        Best Time: **{best_time['best_time']}**
        Average Engagement: **{best_time['avg_engagement']:.2%}**

        Now generate optimized content for the following request:
        {user_input}
        """
    
    return response.strip()

