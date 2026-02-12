from google.adk.agents.llm_agent import Agent

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
security_guardian = Agent(
    model='gemini-2-flash', # Your working model!
    name='security_guardian',
    description="Analyzes code for vulnerabilities and provides production-ready secure rewrites.",
    instruction=(
        "You are an automated Security Guardian in a CI/CD pipeline. "
        "When provided with a code snippet: "
        "1. Identify flaws like SQLi, XSS, or Hardcoded Credentials. "
        "2. Use the 'verify_security_fix' tool to check your logic. "
        "3. Output ONLY the corrected code block. Do not explain unless specifically asked."
    ),
    tools=[verify_security_fix],
)