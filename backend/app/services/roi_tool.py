"""
LangChain Tool wrapper for ROI Analysis Service
Provides automatic tool selection for the orchestrator
"""

from typing import Dict, Any, Optional, Type
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from langchain_core.callbacks.manager import AsyncCallbackManagerForToolRun
from langchain_core.messages import HumanMessage, SystemMessage
import json


class ROIAnalysisInput(BaseModel):
    """Input schema for ROI Analysis Tool"""
    user_message: str = Field(description="The user's question about ROI, revenue, performance, or video metrics")
    user_email: str = Field(
        default="",
        description="The user's email address to fetch their ROI data from Firebase. If not provided, will attempt to retrieve from runtime config."
    )


class ROIAnalysisTool(BaseTool):
    """
    LangChain Tool for ROI Analysis with LangGraph Human-in-the-Loop (HITL)
    
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    AUTOMATIC USER APPROVAL FLOW (Human-in-the-Loop)
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    This tool implements a Human-in-the-Loop pattern:
    1. 🤖 AI detects ROI-related queries automatically
    2. ⏸️ LangGraph pauses execution and requests user approval
    3. 💬 User sees approval dialog with detailed information
    4. ✅/❌ User approves or denies data access
    5. 🚀 If approved: Tool executes, retrieves user's ROI data from Firebase
    6. 📈 AI analyzes data and generates insights with charts
    
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    DATA ACCESS & SECURITY
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    - Fetches user ROI data from Firebase ROI collection
    - Filters by user's Gmail address (user_email field)
    - Analyzes video performance metrics
    - Generates AI-powered insights
    - Returns chart configurations for data visualization
    
    Security: LangGraph HITL middleware intercepts tool calls BEFORE execution,
    ensuring user consent before accessing sensitive Firebase data.
    """
    
    name: str = "roi_analysis"
    description: str = """🎯 USE THIS TOOL when the user asks about:

**Financial Metrics:**
- ROI (Return on Investment)
- Revenue, profit, earnings, income
- Costs, expenses, budget analysis
- Profit margins or net gains

**Video Performance:**
- Video metrics (views, likes, comments, shares)
- Engagement rates or audience interaction
- Retention rates or watch time
- Video performance comparisons

**Analytics & Insights:**
- Performance analytics or data insights
- Marketing campaign effectiveness
- Content performance analysis
- Trend analysis over time

**Time-Based Queries:**
- "Last X days" or "past X days"
- "This week" or "last week"
- "This month" or "last month"
- Date range analysis

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Example Questions:**
- "What is my ROI for the last 7 days?"
- "Show me my revenue breakdown"
- "Which video performed best this month?"
- "How much profit did I make last month?"
- "What are my top performing videos?"
- "Analyze my video engagement trends"
- "Compare my costs vs revenue"

**Input Requirements:**
- user_message: The user's question (string)
- user_email: User's Gmail address (MUST be provided - used to query Firebase)

**Output:**
JSON with AI analysis and chart configurations for visualization.

**Security Note:**
This tool is protected by LangGraph's Human-in-the-Loop middleware.
User approval is AUTOMATICALLY requested before execution.
Data is filtered by user_email to ensure privacy."""
    
    args_schema: Type[BaseModel] = ROIAnalysisInput
    return_direct: bool = True  # Return result directly without further processing
    
    # Add model as class variable (will be set after initialization)
    model: Any = None
    
    def set_model(self, model):
        """Set the AI model for generating insights"""
        self.model = model
    
    async def _arun(
        self,
        user_message: str,
        user_email: str = "",
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """
        Execute ROI analysis asynchronously
        
        Note: With LangGraph HITL middleware, this tool is only called AFTER user approval.
        The agent interrupts BEFORE calling this tool, requests user approval, and only
        proceeds to execute this method if the user approves.
        
        Args:
            user_message: User's question about ROI
            user_email: User's email for data fetching (can be empty, will try to get from config)
            run_manager: Callback manager for async execution
            
        Returns:
            JSON string containing AI analysis and chart configurations
        """
        try:
            from app.services.roi_analysis_service import roi_analysis_service
            
            # Try to get user_email from runtime config if not provided or empty
            if not user_email and run_manager:
                try:
                    # LangGraph passes config through run_manager
                    if hasattr(run_manager, 'get_config'):
                        config = run_manager.get_config()
                    elif hasattr(run_manager, 'metadata'):
                        config = run_manager.metadata
                    elif hasattr(run_manager, 'tags') and run_manager.tags:
                        # Sometimes config is in tags
                        for tag in run_manager.tags:
                            if isinstance(tag, dict) and 'user_email' in tag:
                                user_email = tag['user_email']
                                break
                    else:
                        config = {}
                    
                    if not user_email and isinstance(config, dict):
                        user_email = config.get('configurable', {}).get('user_email', '')
                except Exception:
                    pass
            
            # Validate user_email is present
            if not user_email or user_email.strip() == "":
                return json.dumps({
                    "success": False,
                    "error": "User email is required to access ROI data. Please ensure you're logged in.",
                    "analysis": "⚠️ **Authentication Required**\n\nI need your Gmail address to access your ROI data from Firebase. Please make sure you're logged in with your account.\n\n**Why is this needed?**\n- Your ROI data is stored in Firebase\n- Data is filtered by Gmail address for privacy\n- Only you can access your own data\n\n**Next Steps:**\n1. Log in to your account\n2. Try your question again",
                    "tool_used": "roi_analysis"
                }, indent=2)
            
            # Call the ROI analysis service to:
            # 1. Fetch user's ROI data from Firebase (filtered by user_email)
            # 2. Analyze the data based on the user's question
            # 3. Generate insights and chart configurations
            # Note: Skip custom confirmation since LangGraph HITL already handled approval
            analysis_data, charts, _ = await roi_analysis_service.process_roi_query(
                user_message=user_message,
                user_email=user_email,
                skip_confirmation=True  # LangGraph already handled approval
            )
            
            if not analysis_data.get("found_data"):
                return json.dumps({
                    "success": True,
                    "analysis": "I couldn't find any ROI data for your account. Please make sure you have uploaded video performance data to get insights.",
                    "charts": [],
                    "tool_used": "roi_analysis"
                }, indent=2)
            
            # Pass data to AI for intelligent analysis
            system_prompt = """You are a data analyst expert specializing in YouTube content ROI analysis.
Your task is to analyze the provided ROI data and generate insightful, actionable recommendations.

Guidelines:
- Provide a clear, conversational summary of the key findings
- Highlight strengths and areas for improvement
- Use emojis appropriately (📊, 💰, 🎯, ✅, ⚠️, 📈)
- Focus on actionable insights
- Keep the tone professional but friendly
- Structure your response with markdown formatting
- Reference specific numbers to support your analysis"""

            user_prompt = f"""User Question: {user_message}

{analysis_data.get('data_summary', '')}

Please provide an insightful analysis of this ROI data, directly addressing the user's question. Include:
1. A brief overview of overall performance
2. Key insights and patterns
3. Actionable recommendations
4. Mention that visualizations are provided below"""

            ai_messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            # Invoke AI model
            if self.model:
                ai_response = await self.model.ainvoke(ai_messages)
                ai_analysis = ai_response.content
            else:
                # Fallback if model not set
                ai_analysis = analysis_data.get('data_summary', '')
            
            # Return structured result as JSON
            result = {
                "success": True,
                "analysis": ai_analysis,
                "charts": charts,
                "tool_used": "roi_analysis"
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            error_msg = f"Error in ROI analysis: {str(e)}"
            import traceback
            traceback.print_exc()
            
            result = {
                "success": False,
                "error": error_msg,
                "tool_used": "roi_analysis"
            }
            
            return json.dumps(result, indent=2)
    
    def _run(
        self,
        user_message: str,
        user_email: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """
        Synchronous version (not implemented - use async version)
        """
        raise NotImplementedError("ROI Analysis Tool only supports async execution. Use _arun instead.")


# Create singleton instance of the tool
roi_analysis_tool = ROIAnalysisTool()
