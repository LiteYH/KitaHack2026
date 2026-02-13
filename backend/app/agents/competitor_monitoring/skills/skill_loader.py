"""
Skill Loader for Agent Skills (progressive disclosure).

Skills are folder-based with SKILL.md files containing frontmatter metadata
and full instructions. The loader reads frontmatter first (cheap) and loads
full content on demand (expensive) to save tokens.

This implements the official LangChain skills pattern with:
- load_skill tool for agent to load full content
- SkillMiddleware to inject skill descriptions dynamically
"""

from pathlib import Path
from typing import Callable, Dict, List, Optional

import frontmatter
from langchain.agents.middleware import AgentMiddleware, ModelRequest, ModelResponse
from langchain.messages import SystemMessage
from langchain.tools import tool


class SkillLoader:
    """Load and manage agent skills with progressive disclosure."""

    def __init__(self, skills_dir: Path):
        self.skills_dir = skills_dir
        self._index: Optional[List[Dict]] = None

    @property
    def skills_index(self) -> List[Dict]:
        """Lazy-load skill index from frontmatter."""
        if self._index is None:
            self._index = self._build_index()
        return self._index

    def _build_index(self) -> List[Dict]:
        """Scan skill directories and load frontmatter only."""
        skills: List[Dict] = []
        if not self.skills_dir.exists():
            return skills

        for skill_dir in self.skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue
            skill_file = skill_dir / "SKILL.md"
            if not skill_file.exists():
                continue

            post = frontmatter.load(str(skill_file))

            skills.append(
                {
                    "name": post.metadata.get("name", skill_dir.name),
                    "description": post.metadata.get("description", ""),
                    "metadata": post.metadata.get("metadata", {}),
                    "compatibility": post.metadata.get("compatibility", ""),
                    "license": post.metadata.get("license", ""),
                    "path": skill_dir,
                }
            )
        return skills

    def get_skills_summary(self, skill_names: Optional[List[str]] = None) -> str:
        """
        Get a brief summary of available skills for the system prompt.

        If *skill_names* is supplied, only include those skills;
        otherwise include all discovered skills.
        """
        lines: List[str] = []
        for skill in self.skills_index:
            if skill_names and skill["name"] not in skill_names:
                continue
            lines.append(f"- **{skill['name']}**: {skill['description']}")
        return "\n".join(lines) if lines else "No skills loaded."

    def get_relevant_skills(self, query: str) -> List[str]:
        """
        Progressive disclosure: return full skill content for skills
        whose description matches the query.
        
        Note: In practice, the LLM decides which skills to load via the
        load_skill tool based on skill descriptions shown in the system prompt.
        This method is for fallback/compatibility.
        """
        relevant: List[str] = []
        query_lower = query.lower()

        for skill in self.skills_index:
            # Match against description and skill name
            description_lower = skill["description"].lower()
            name_lower = skill["name"].lower()
            
            if query_lower in description_lower or query_lower in name_lower:
                content = self.load_full_skill(skill["name"])
                if content:
                    relevant.append(content)
        return relevant

    def load_full_skill(self, skill_name: str) -> Optional[str]:
        """Load the full SKILL.md content for a named skill."""
        for skill in self.skills_index:
            if skill["name"] == skill_name:
                skill_file = skill["path"] / "SKILL.md"
                if skill_file.exists():
                    post = frontmatter.load(str(skill_file))
                    return str(post.content)
        return None

    def load_supplementary(self, skill_name: str, filename: str) -> Optional[str]:
        """Load a supplementary file from within a skill directory."""
        for skill in self.skills_index:
            if skill["name"] == skill_name:
                file_path = skill["path"] / filename
                if file_path.exists():
                    return file_path.read_text(encoding="utf-8")
        return None


# ── Global skill loader instance ────────────────────────────────────
# Initialized by create_load_skill_tool factory
_GLOBAL_SKILL_LOADER: Optional[SkillLoader] = None


def create_load_skill_tool(skill_loader: SkillLoader):
    """
    Factory to create the load_skill tool with access to a SkillLoader instance.
    
    Returns the @tool-decorated function that agents can call.
    """
    global _GLOBAL_SKILL_LOADER
    _GLOBAL_SKILL_LOADER = skill_loader

    @tool
    def load_skill(skill_name: str) -> str:
        """Load the full content of a skill into the agent's context.

        Use this when you need detailed information about how to handle a specific
        type of request. This will provide you with comprehensive instructions,
        policies, and guidelines for the skill area.

        Args:
            skill_name: The name of the skill to load (e.g., "competitor_search", 
                       "competitor_analysis", "notification_management")
        
        Returns:
            The full skill content with instructions and workflows.
        """
        if _GLOBAL_SKILL_LOADER is None:
            return "Error: Skill loader not initialized"
        
        content = _GLOBAL_SKILL_LOADER.load_full_skill(skill_name)
        if content:
            return f"**Loaded skill: {skill_name}**\n\n{content}"
        
        # Skill not found - return helpful error
        available = ", ".join(s["name"] for s in _GLOBAL_SKILL_LOADER.skills_index)
        return f"Skill '{skill_name}' not found. Available skills: {available}"
    
    return load_skill


class SkillMiddleware(AgentMiddleware):
    """
    Middleware that injects skill descriptions into the system prompt.
    
    Follows the official LangChain skills pattern:
    - Registers load_skill tool via class variable
    - Dynamically injects skill descriptions via wrap_model_call
    - Agent decides which skills to load based on descriptions
    """

    def __init__(self, skill_loader: SkillLoader, skill_names: Optional[List[str]] = None):
        """
        Initialize middleware with skill loader.
        
        Args:
            skill_loader: SkillLoader instance to load skills from
            skill_names: Optional list of skill names to include. If None, includes all.
        """
        super().__init__()
        self.skill_loader = skill_loader
        self.skill_names = skill_names
        
        # Create the load_skill tool
        self.load_skill_tool = create_load_skill_tool(skill_loader)
        
        # Build skills prompt from skill loader index
        skills_list = []
        for skill in skill_loader.skills_index:
            if skill_names and skill["name"] not in skill_names:
                continue
            skills_list.append(f"- **{skill['name']}**: {skill['description']}")
        
        self.skills_prompt = "\n".join(skills_list) if skills_list else "No skills available."

    @property
    def tools(self):
        """Register the load_skill tool with the agent."""
        return [self.load_skill_tool]

    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        """Inject skill descriptions into system prompt (synchronous version)."""
        # Build the skills addendum
        skills_addendum = (
            f"\n\n## Available Skills\n\n{self.skills_prompt}\n\n"
            "Use the **load_skill** tool when you need detailed information "
            "about handling a specific type of request or when a skill seems "
            "relevant to the user's query."
        )

        # Append to system message content blocks
        new_content = list(request.system_message.content_blocks) + [
            {"type": "text", "text": skills_addendum}
        ]
        new_system_message = SystemMessage(content=new_content)
        modified_request = request.override(system_message=new_system_message)

        return handler(modified_request)

    async def awrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        """Inject skill descriptions into system prompt (asynchronous version)."""
        # Build the skills addendum
        skills_addendum = (
            f"\n\n## Available Skills\n\n{self.skills_prompt}\n\n"
            "Use the **load_skill** tool when you need detailed information "
            "about handling a specific type of request or when a skill seems "
            "relevant to the user's query."
        )

        # Append to system message content blocks
        new_content = list(request.system_message.content_blocks) + [
            {"type": "text", "text": skills_addendum}
        ]
        new_system_message = SystemMessage(content=new_content)
        modified_request = request.override(system_message=new_system_message)

        return await handler(modified_request)
