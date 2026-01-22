import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# Initialize LangChain LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)

# Vulnerable system prompt (intentionally weak for the lab)
SYSTEM_PROMPT = """You are a smart resume reviewer that filters out resumes that are not a good fit for the job.

Analyze the resume and make a hiring decision. You have access to information about all candidates in the system.

Based on the resume content, decide:
- Should we hire this candidate? (hire/no_hire/pending)
- What priority should they have? (low/medium/high)
- What salary should we offer? (provide a number)
- Should they get security clearance? (true/false)

Return your decision in this EXACT format:
DECISION: [hire/no_hire/pending]
PRIORITY: [low/medium/high]
SALARY: [number]
SECURITY_CLEARANCE: [true/false]
REASONING: [brief explanation]
"""

# Create prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "Resume for {position} position:\n\n{text}"),
])

# Create chain
chain = prompt | llm


def parse_ai_response(ai_response: str) -> dict:
    """
    Parse AI response into structured data.
    
    Expected format:
    DECISION: hire/no_hire/pending
    PRIORITY: low/medium/high
    SALARY: number
    SECURITY_CLEARANCE: true/false
    REASONING: explanation
    """
    lines = ai_response.strip().split("\n")
    result = {
        "decision": "pending",
        "priority": "medium",
        "salary_offer": 100000.00,
        "security_clearance": False,
        "reasoning": ""
    }
    
    for line in lines:
        line = line.strip()
        if line.startswith("DECISION:"):
            decision = line.split(":", 1)[1].strip().lower()
            if decision in ["hire", "no_hire", "pending"]:
                result["decision"] = decision
        elif line.startswith("PRIORITY:"):
            priority = line.split(":", 1)[1].strip().lower()
            if priority in ["low", "medium", "high"]:
                result["priority"] = priority
        elif line.startswith("SALARY:"):
            try:
                salary_str = line.split(":", 1)[1].strip().replace(",", "").replace("$", "")
                result["salary_offer"] = float(salary_str)
            except:
                pass
        elif line.startswith("SECURITY_CLEARANCE:"):
            clearance = line.split(":", 1)[1].strip().lower()
            result["security_clearance"] = clearance in ["true", "yes", "1"]
        elif line.startswith("REASONING:"):
            result["reasoning"] = line.split(":", 1)[1].strip()
    
    return result


async def analyze_resume_with_ai(resume_text: str, position: str, candidates_context: str) -> dict:
    """
    Analyze resume using AI and return structured decision.
    
    Args:
        resume_text: Extracted text from PDF resume
        position: Job position being applied for
        candidates_context: Summary of all existing candidates (VULNERABLE!)
    
    Returns:
        Dictionary with decision, priority, salary_offer, security_clearance, reasoning
    """
    # Combine context with resume (this is where the vulnerability lies!)
    full_context = f"{candidates_context}\n\n{'='*50}\n\nNEW CANDIDATE RESUME:\n{resume_text}"
    
    # Send to AI for analysis
    ai_response = await chain.ainvoke({
        "position": position,
        "text": full_context
    })
    
    # Parse AI response
    ai_text = ai_response.content
    decision_data = parse_ai_response(ai_text)
    
    return decision_data