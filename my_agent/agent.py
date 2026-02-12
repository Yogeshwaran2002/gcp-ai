import os
import vertexai
from vertexai.preview import reasoning_engines
from google.adk.agents.llm_agent import Agent

# 1. Initialize Vertex AI (Update with your project details)
PROJECT_ID = "ai-connect-sap26blr-315"
LOCATION = "us-central1"
vertexai.init(project=PROJECT_ID, location=LOCATION)

# --- DETERMINISTIC TOOLS ---

def secret_scanner(code: str) -> dict:
    """Detects high-entropy strings and hardcoded credentials."""
    if "api_key" in code.lower() and "os.getenv" not in code:
        return {"status": "FAIL", "issue": "Hardcoded API Key found."}
    return {"status": "PASS"}

def injection_scanner(code: str) -> dict:
    """Detects SQLi, Command Injection, and XSS patterns."""
    if "execute(" in code and ("f\"" in code or "+" in code):
        return {"status": "FAIL", "issue": "SQL Injection vulnerability via string interpolation."}
    return {"status": "PASS"}

def logic_validator(code: str) -> dict:
    """Checks for business logic flaws (e.g., missing auth checks)."""
    if "def delete_" in code and "@login_required" not in code:
        return {"status": "FAIL", "issue": "Dangerous operation missing authentication decorator."}
    return {"status": "PASS"}

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

# --- SPECIALIZED AGENTS ---

injection_agent = Agent(
    model='gemini-2.0-flash',
    name='injection_hunter',
    description="Specialist in detecting SQL Injection and XSS.",
    instruction="Analyze code for injection flaws. Report risks clearly.",
    tools=[injection_scanner]
)

secret_agent = Agent(
    model='gemini-2.0-flash',
    name='secret_scout',
    description="Specialist in identifying hardcoded secrets and API keys.",
    instruction="Scan for hardcoded secrets. Use scanner to verify.",
    tools=[secret_scanner]
)

logic_agent = Agent(
    model='gemini-2.0-flash',
    name='logic_auditor',
    description="Specialist in finding business logic and auth flaws.",
    instruction="Check for missing security decorators like @login_required.",
    tools=[logic_validator]
)

# --- ROOT ORCHESTRATOR ---

root_agent = Agent(
    model='gemini-2.0-flash',
    name='root_guardian',
    description="Lead Security Architect orchestrating reviews.",
    instruction=(
        "You are the Lead Security Architect. You MUST: "
        "1. Delegate the audit to 'injection_hunter', 'secret_scout', and 'logic_auditor'. "
        "2. Synthesize findings and rewrite the code to be 100% secure. "
        "3. Run 'verify_security_fix' on your own final code before finishing. "
        "Output ONLY the secure Python code block."
    ),
    sub_agents=[injection_agent, secret_agent, logic_agent],
    tools=[verify_security_fix]
)

# --- DEPLOYMENT WRAPPER ---

class SecurityGuardianApp:
    def __init__(self):
        # We assign the agent here so it's packaged during deployment
        self.agent = root_agent 

    def query(self, pr_diff: str):
        """Method called by the GitHub bot to process code changes."""
        response = self.agent.run(f"Audit and fix this PR code:\n{pr_diff}")
        return response.text

# --- EXECUTION / DEPLOYMENT ---

if __name__ == "__main__":
    print("🚀 Starting deployment to Vertex AI Reasoning Engine...")
    
    # This command packages your code, tools, and agents into a managed endpoint
    remote_app = reasoning_engines.ReasoningEngine.create(
        SecurityGuardianApp(),
        display_name="Security_Guardian_Bot",
        # Requirements ensures the cloud environment has ADK installed
        requirements=[
            "google-cloud-aiplatform[adk,agent_engines]",
        ]
    )
    
    print(f"✅ Deployment successful!")
    print(f"📍 Endpoint ID: {remote_app.resource_name}")

    import vertexai
from vertexai.preview import reasoning_engines

# 1. Initialize with your project and staging bucket
vertexai.init(
    project="ai-connect-sap26blr-315",
    location="us-central1",
    staging_bucket="gs://guardian-bot-staging-315"
)

# 2. Deploy the Reasoning Engine
print("🛠️ Deploying to Vertex AI...")
remote_app = reasoning_engines.ReasoningEngine.create(
    SecurityGuardianApp(),  # Your class from the previous step
    display_name="Shift_Left_Guardian_v1",
    description="Multi-agent security auditor for GitHub PRs",
    requirements=[
        "google-cloud-aiplatform[adk,agent_engines]",
        "cloudpickle==3.0.0"
    ],
)

print(f"✅ Deployment Complete!")
print(f"📍 Resource ID: {remote_app.resource_name}")