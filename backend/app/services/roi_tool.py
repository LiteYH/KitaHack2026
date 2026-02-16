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
    user_email: str = Field(description="The user's email address to fetch their ROI data from Firebase")


class ROIAnalysisTool(BaseTool):
    """
    LangChain Tool for ROI Analysis
    
    This tool:
    1. Fetches user ROI data from Firebase
    2. Analyzes the metrics
    3. Passes data to AI for intelligent insights
    4. Generates charts with fixed types
    """
    
    name: str = "roi_analysis"
    description: str = """Use this tool when the user asks about:
    - ROI (Return on Investment)
    - Revenue, profit, or earnings
    - Video performance or metrics
    - Views, engagement, or analytics
    - Cost analysis or budget
    - Time-based questions (e.g., "last 7 days", "this month")
    
    Input should be the user's question and their email address.
    The tool will fetch their ROI data, analyze it, and return insights with chart configurations.
    
    Example questions:
    - "What is my ROI for the last 7 days?"
    - "Show me my revenue breakdown"
    - "Which video performed best?"
    - "How much profit did I make last month?"
    """
    
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
        user_email: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """
        Execute ROI analysis asynchronously
        
        Args:
            user_message: User's question about ROI
            user_email: User's email for data fetching
            run_manager: Callback manager for async execution
            
        Returns:
            JSON string containing AI analysis and chart configurations
        """
        try:
            from app.services.roi_analysis_service import roi_analysis_service
            
            print(f"🎯 [ROI TOOL] Executing ROI analysis for: {user_email}")
            print(f"   ↳ Query: {user_message}")
            
            # Step 1: Fetch and analyze ROI data from Firebase
            analysis_data, charts = await roi_analysis_service.process_roi_query(
                user_message=user_message,
                user_email=user_email
            )
            
            if not analysis_data.get("found_data"):
                print(f"   ↳ No data found")
                return json.dumps({
                    "success": True,
                    "analysis": "I couldn't find any ROI data for your account. Please make sure you have uploaded video performance data to get insights.",
                    "charts": [],
                    "tool_used": "roi_analysis"
                }, indent=2)
            
            # Step 2: Pass data to AI for intelligent analysis
            print(f"   ↳ Passing data to AI for analysis...")
            
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

{analysis_data['data_summary']}

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
                ai_analysis = analysis_data['data_summary']
            
            print(f"   ↳ Generated: {len(charts)} charts")
            print(f"✅ [ROI TOOL] Analysis complete with AI insights")
            
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
            print(f"❌ [ROI TOOL ERROR] {error_msg}")
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
