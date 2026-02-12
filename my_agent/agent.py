from google.adk.agents.llm_agent import Agent

# Mock tool implementation
def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city."""
    return {"status": "success", "city": city, "time": "10:30 AM"}
def verify_security_fix(code: str) -> dict:
    """Verifies if the code still contains common vulnerabilities."""
    issues = []
    if "db.execute(f\"" in code or "db.execute(\"" in code:
        issues.append("SQL Injection Risk: Use parameterized queries.")
    if "api_key =" in code:
        issues.append("Hardcoded Secret: Use environment variables.")
    
    return {
        "status": "SECURE" if not issues else "VULNERABLE",
        "details": issues
    }


root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description="Checks the Code for security vulnerabilities and suggests fixes.",
    instruction=(
        "You are a Hostile Security Auditor. Your job is to find even the smallest flaw. "
        "Check for: \n"
        "- Hardcoded secrets (API keys, passwords, salts)\n"
        "- SQL injection (using f-strings or string concatenation in queries)\n"
        "- Lack of input validation\n"
        "If you find a flaw, USE the 'verify_security_fix' tool to confirm it, "
        "then REWRITE the code using best practices (e.g., environment variables, parameterized queries)."
    ),
    tools=[get_current_time,verify_security_fix],
)