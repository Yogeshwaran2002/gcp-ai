import sys
from google.vertexai.preview import reasoning_engines

def main(diff_file):
    with open(diff_file, 'r') as f:
        diff_content = f.read()
    
    # Connect to your deployed engine
    remote_app = reasoning_engines.ReasoningEngine("YOUR_RESOURCE_NAME")
    secure_code = remote_app.query(diff_content)
    
    # Use 'gh' command to comment on the PR
    print(f"AI SECURITY SUGGESTION:\n{secure_code}")

if __name__ == "__main__":
    main(sys.argv[1])