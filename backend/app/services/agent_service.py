"""
LangGraph Agent Service with Human-in-the-Loop (HITL) Middleware
Uses official LangChain/LangGraph HITL pattern for tool execution approval
"""

import os
from typing import List, Optional, Dict, Any, Tuple
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from app.core.config import settings
from app.schemas.chat import ChatMessage
from app.services.roi_tool import roi_analysis_tool
from functools import partial


def create_roi_tool_with_config(config: Dict[str, Any]):
    """
    Create a partial ROI tool that has access to the runtime config.
    This allows the tool to automatically access user_email from config.
    """
    user_email = config.get('configurable', {}).get('user_email', '')
    
    # Create a wrapper functi that injects user_email
    class ConfigBoundROITool(roi_analysis_tool.__class__):
        async def _arun(self, user_message: str, user_email: str = "", run_manager = None):
            # Use the user_email from config if not provided in args
            actual_email = user_email or config.get('configurable', {}).get('user_email', '')
            return await super()._arun(user_message, actual_email, run_manager)
    
    bound_tool = ConfigBoundROITool()
    bound_tool.name = roi_analysis_tool.name
    bound_tool.description = roi_analysis_tool.description
    bound_tool.args_schema = roi_analysis_tool.args_schema
    bound_tool.return_direct = roi_analysis_tool.return_direct
    bound_tool.model = roi_analysis_tool.model
    
    return bound_tool


class AgentService:
    """
    LangGraph-based Agent Service with Human-in-the-Loop for ROI data access
    
    Features:
    - Automatic tool selection using ReAct pattern
    - Human approval required before accessing sensitive ROI data
    - Stateful execution with checkpointing (MemorySaver)
    - Support for approve/reject decisions
    """
    
    def __init__(self):
        """Initialize the LangGraph Agent with HITL middleware"""
        # Get API key from settings
        api_key = settings.google_api_key or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables.")
        
        # Initialize LangChain ChatGoogleGenerativeAI model
        self.model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            google_api_key=api_key,
            temperature=0.7,
            max_output_tokens=2048,
            convert_system_message_to_human=True
        )
        
        # Set model for ROI tool
        roi_analysis_tool.set_model(self.model)
        
        # System instruction
        self.system_message = self._get_system_instruction()
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # LANGGRAPH AGENT WITH HUMAN-IN-THE-LOOP
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        # Create checkpointer for state persistence (required for HITL)
        self.checkpointer = MemorySaver()
        
        # Create ReAct agent with tools
        # Interrupt BEFORE tool execution to request human approval
        self.agent = create_react_agent(
            model=self.model,
            tools=[roi_analysis_tool],
            checkpointer=self.checkpointer,
            # Interrupt before calling tools (HITL pattern)
            interrupt_before=["tools"]
        )
        
        print("✅ [AGENT] LangGraph agent initialized with HITL middleware")
        print("   ↳ Tools: [roi_analysis]")
        print("   ↳ Interrupt: BEFORE tool execution (HITL approval required)")
        print("   ↳ Checkpointer: MemorySaver (in-memory state)")
    
    def _get_system_instruction(self) -> str:
        """Get the system instruction for the AI assistant"""
        return """You are BossolutionAI, an AI-powered marketing assistant designed specifically for SMEs (Small and Medium Enterprises). 

Your capabilities include:
- Content Creation: Generate engaging marketing content, social media posts, ad copy, and campaign ideas
- Competitor Analysis: Analyze competitors' marketing strategies and provide insights
- Campaign Optimization: Suggest improvements for marketing campaigns to maximize ROI
- Content Scheduling: Help with content planning and scheduling strategies
- Performance Analytics: Interpret marketing metrics and provide actionable recommendations
- Market Research: Provide insights on target audiences, trends, and market opportunities

Your personality:
- Professional yet friendly and approachable
- Focus on practical, actionable advice
- Use clear language, avoiding excessive jargon
- Be encouraging and supportive of SME growth
- Provide specific examples and suggestions when possible

IMPORTANT - Formatting Guidelines:
- ALWAYS format your responses using Markdown for better readability
- Use **bold text** for emphasis and important points
- Use bullet points (- or *) or numbered lists (1., 2., 3.) to organize information
- Break long paragraphs into shorter, digestible chunks (2-3 sentences max)
- Use headers (##, ###) to organize different sections of your response
- Add blank lines between sections for better spacing
- Use line breaks to avoid wall-of-text responses

CRITICAL - ROI Data Access (Human-in-the-Loop Flow):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
When the user asks questions about ROI, revenue, video performance, analytics, or data insights:

**Step 1: Detect ROI-Related Queries**
Automatically recognize queries about:
- ROI (Return on Investment) metrics
- Revenue, profit, earnings, or costs
- Video performance (views, engagement, retention)
- Analytics or metrics data
- Time-based analysis ("last 7 days", "this month", etc.)

**Step 2: Automatically Use ROI Analysis Tool**
- The authenticated user's Gmail is ALREADY available in the system
- DO NOT ask the user for their email - it's provided in the system context
- Directly invoke the `roi_analysis` tool with:
  * user_message: The user's original question
  * user_email: Use the email provided in the system context (see below)

**Step 3: Approval Flow (Automatic)**
- The system will AUTOMATICALLY pause and request user approval
- You don't need to do anything - LangGraph handles this
- The user will see an approval dialog explaining:
  * What data will be accessed (their ROI data from Firebase)
  * That data is filtered by their Gmail address
  * Privacy and security guarantees
- If approved: The tool executes and retrieves their ROI data
- If denied: Respond supportively and offer alternative assistance

**Step 4: Provide Insights**
After approval, analyze the data and provide:
- Clear, actionable insights
- Data visualizations (charts)
- Specific recommendations for improvement
- Answers to their original question

**Example Flow:**
User: "What was my ROI for the last 7 days?"
→ You detect this is ROI-related
→ You call roi_analysis(user_message="What was my ROI for the last 7 days?", user_email=<from context>)
→ System pauses and requests user approval
→ User approves
→ Tool retrieves ROI data from Firebase (filtered by user's Gmail)
→ You analyze and present insights with charts

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Always aim to:
1. Understand the user's specific needs and context
2. Provide tailored recommendations for SME budgets and resources
3. Offer step-by-step guidance when appropriate
4. Be concise yet comprehensive in your responses
5. FORMAT responses with proper spacing, headings, and lists for easy reading"""
    
    async def chat(
        self,
        user_message: str,
        conversation_history: Optional[List[ChatMessage]] = None,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        thread_id: Optional[str] = None,
        approval_decision: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, Optional[List[Dict[str, Any]]], bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Process chat message using LangGraph agent with HITL
        
        Args:
            user_message: User's input message
            conversation_history: Previous messages for context
            user_id: Optional user ID
            user_email: User's email (required for ROI tool)
            thread_id: Thread ID for resuming interrupted conversations
            approval_decision: User's approval decision for pending tool execution
            
        Returns:
            Tuple of (response_text, charts, requires_approval, approval_request, thread_id)
        """
        try:
            import uuid
            import json
            
            # Generate or reuse thread_id for state management
            if not thread_id:
                thread_id = str(uuid.uuid4())
            
            # Configuration for the agent execution
            config = {
                "configurable": {
                    "thread_id": thread_id,
                    "user_email": user_email or ""
                }
            }
            
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # Handle approval decision (resume from interrupt)
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            
            if approval_decision:
                approved = approval_decision.get("approved", False)
                
                if not approved:
                    # User rejected tool execution
                    return (
                        "I understand. I won't access your ROI data. Feel free to ask me anything else about marketing strategies, content creation, or general business advice! 😊",
                        None,
                        False,
                        None,
                        thread_id
                    )
                
                # User approved - resume execution
                # Get current state and inject user_email into tool args if missing
                state = self.agent.get_state(config)
                
                # Inject user_email into tool args if missing
                if state.values.get("messages"):
                    last_msg = state.values["messages"][-1]
                    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                        tool_call = last_msg.tool_calls[0]
                        tool_args = tool_call.get("args", {})
                        
                        # CRITICAL FIX: Inject user_email if missing or empty
                        if not tool_args.get("user_email") and user_email:
                            tool_args["user_email"] = user_email
                            tool_call["args"] = tool_args
                
                # Continue execution with potentially updated tool args
                result = None
                async for event in self.agent.astream(None, config, stream_mode="values"):
                    result = event
                
                # Check if we hit another interrupt (shouldn't happen for ROI tool)
                state_after = self.agent.get_state(config)
                if state_after.next:
                    # Still interrupted (edge case)
                    return await self._handle_interrupt(state_after, thread_id)
                
                # Extract response from final state
                return self._extract_response(result, thread_id)
            
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # Start new conversation or continue existing thread
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            
            # Build messages with history
            messages = []
            
            # Add system message first
            # Include user email in system context if available
            system_content = self.system_message
            if user_email:
                system_content += f"\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                system_content += f"🔑 AUTHENTICATED USER CONTEXT:\n"
                system_content += f"User Gmail: {user_email}\n"
                system_content += f"\n"
                system_content += f"CRITICAL: When using the roi_analysis tool, you MUST pass this email address:\n"
                system_content += f"  user_email=\"{user_email}\"\n"
                system_content += f"\n"
                system_content += f"This email is used to:\n"
                system_content += f"1. Query Firebase ROI collection (filtered by user_email field)\n"
                system_content += f"2. Ensure the user only sees their own data\n"
                system_content += f"3. Maintain data privacy and security\n"
                system_content += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            messages.append(SystemMessage(content=system_content))
            
            if conversation_history:
                for msg in conversation_history:
                    if msg.role == "user":
                        messages.append(HumanMessage(content=msg.content))
                    elif msg.role == "assistant":
                        messages.append(AIMessage(content=msg.content))
            
            # Add current message
            messages.append(HumanMessage(content=user_message))
            
            # Prepare input for agent
            agent_input = {"messages": messages}
            
            # Stream agent execution
            result = None
            async for event in self.agent.astream(agent_input, config, stream_mode="values"):
                result = event
            
            # Check if agent was interrupted (tool execution needs approval)
            state = self.agent.get_state(config)
            
            if state.next:
                # Agent is interrupted - tool execution pending approval
                print(f"⏸️ [HITL] Agent interrupted - tool execution requires approval")
                return await self._handle_interrupt(state, thread_id)
            
            # No interrupt - extract final response
            return self._extract_response(result, thread_id)
            
        except Exception as e:
            print(f"❌ [AGENT ERROR] {str(e)}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Failed to process message: {str(e)}")
    
    async def _handle_interrupt(
        self, 
        state: Any, 
        thread_id: str
    ) -> Tuple[str, Optional[List[Dict[str, Any]]], bool, Optional[Dict[str, Any]], str]:
        """
        Handle agent interrupt (tool execution requires approval)
        
        Args:
            state: Agent state at interrupt
            thread_id: Current thread ID
            
        Returns:
            Tuple with approval request
        """
        import json
        
        # Get the pending tool calls
        last_message = state.values.get("messages", [])[-1]
        
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            tool_call = last_message.tool_calls[0]
            tool_name = tool_call.get("name", "unknown")
            tool_args = tool_call.get("args", {})
            
            print(f"🔒 [HITL] Tool execution requires approval:")
            print(f"   ↳ Tool: {tool_name}")
            print(f"   ↳ Args: {json.dumps(tool_args, indent=2)}")
            
            # Create approval request message
            user_message = tool_args.get("user_message", "your ROI data")
            user_email = tool_args.get("user_email", "your account")
            period_days = None
            
            # Try to extract time period from message
            from app.services.roi_analysis_service import roi_analysis_service
            if hasattr(roi_analysis_service, 'extract_time_period'):
                period_days = roi_analysis_service.extract_time_period(user_message)
            
            period_text = f" from the last {period_days} days" if period_days else ""
            
            approval_message = f"""🔒 **ROI Data Access Request**

I need your permission to access your ROI data from Firebase{period_text} to answer your question:

> *"{user_message}"*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**📊 What I'll Access:**
- Video performance metrics (views, engagement, retention rates)
- Revenue breakdown (ad revenue, sponsorships, affiliate earnings)
- Cost analysis (production, promotion costs)
- ROI calculations and performance trends

**🔐 Your Account:**
- Gmail: `{user_email}`
- Data Source: Firebase ROI Collection
- Filter: `user_email == '{user_email}'`

**🛡️ Privacy & Security Guarantees:**
- ✅ **Isolated Data Access** - Only YOUR data will be retrieved (filtered by Gmail)
- ✅ **No Cross-User Access** - Other users' data remains completely inaccessible
- ✅ **Session-Only Usage** - Data is used ONLY for this analysis session
- ✅ **No Storage** - Retrieved data is not stored or cached
- ✅ **No Sharing** - Data is never shared with third parties
- ✅ **You Control Access** - You can deny this request at any time

**📋 Data Flow:**
1. Your approval triggers Firebase query
2. Query filters: `WHERE user_email = '{user_email}'`
3. ROI data is retrieved and analyzed
4. Insights and charts are generated
5. Data is discarded after response

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Do you approve this data access?**

*(Click "Yes" to proceed or "No" to cancel)*"""
            
            approval_request = {
                "tool_name": tool_name,
                "tool_args": tool_args,
                "message": approval_message,
                "thread_id": thread_id,
                "requires_approval": True
            }
            
            return (
                approval_message,
                None,
                True,  # requires_approval
                approval_request,
                thread_id
            )
        
        # No tool calls found (shouldn't happen)
        print(f"⚠️ [HITL] Interrupted but no tool calls found")
        return (
            "An unexpected error occurred. Please try again.",
            None,
            False,
            None,
            thread_id
        )
    
    def _extract_response(
        self, 
        result: Any, 
        thread_id: str
    ) -> Tuple[str, Optional[List[Dict[str, Any]]], bool, Optional[Dict[str, Any]], str]:
        """
        Extract response from agent result
        
        Args:
            result: Agent execution result
            thread_id: Current thread ID
            
        Returns:
            Tuple of response data
        """
        import json
        
        if not result:
            return (
                "I apologize, but I couldn't generate a response. Please try again.",
                None,
                False,
                None,
                thread_id
            )
        
        # Get the last message from the agent
        messages = result.get("messages", [])
        if not messages:
            return (
                "I apologize, but I couldn't generate a response. Please try again.",
                None,
                False,
                None,
                thread_id
            )
        
        last_message = messages[-1]
        
        # Check if it's a tool response with charts
        charts = None
        response_text = ""
        
        # If last message is a tool message, get the AI's response after processing
        if hasattr(last_message, "content"):
            response_text = last_message.content
            
            # Try to extract charts from tool response
            try:
                # Check if response contains JSON with charts
                if isinstance(response_text, str) and "{" in response_text:
                    # Try to parse JSON from tool result
                    json_start = response_text.find("{")
                    json_end = response_text.rfind("}") + 1
                    if json_start >= 0 and json_end > json_start:
                        json_str = response_text[json_start:json_end]
                        data = json.loads(json_str)
                        if "charts" in data:
                            charts = data["charts"]
                        if "analysis" in data:
                            response_text = data["analysis"]
            except Exception as e:
                print(f"⚠️ [AGENT] Could not extract charts: {e}")
        
        print(f"✅ [AGENT] Response generated successfully")
        if charts:
            print(f"   ↳ Charts: {len(charts)}")
        
        return (
            response_text,
            charts,
            False,  # No approval required for final response
            None,
            thread_id
        )


# Singleton instance
agent_service = AgentService()
