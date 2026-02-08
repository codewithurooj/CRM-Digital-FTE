"""
Chat Endpoint E2E Testing Script
Tests AI-powered task management via natural language chat endpoint.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    print("Warning: python-dotenv not installed. Using environment variables directly.")


class ChatEndpointTester:
    """E2E test runner for chat endpoint with natural language commands"""

    def __init__(self, api_url: str):
        self.api_url = api_url
        self.results: List[Dict[str, Any]] = []
        self.jwt_token: str = ""
        self.user_id: str = ""
        self.conversation_id: Optional[int] = None
        self.test_task_ids: List[int] = []

    def run_curl_command(self, cmd: List[str]) -> Dict[str, Any]:
        """Execute curl command and return parsed response"""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            lines = result.stdout.strip().split('\n')
            status_code = int(lines[-1])
            body = '\n'.join(lines[:-1])

            # Try to parse JSON response
            try:
                body_json = json.loads(body) if body else None
            except json.JSONDecodeError:
                body_json = None

            return {
                "status_code": status_code,
                "body": body_json,
                "raw_body": body
            }
        except subprocess.TimeoutExpired:
            return {"error": "timeout", "status_code": 0}
        except Exception as e:
            return {"error": str(e), "status_code": 0}

    def authenticate(self, email: str, password: str) -> bool:
        """Authenticate user and get JWT token"""
        print("=" * 80)
        print("AUTHENTICATION SETUP")
        print("=" * 80)

        # Try to sign up first
        signup_cmd = [
            "curl", "-X", "POST", "-s", "-w", "\n%{http_code}",
            f"{self.api_url}/api/auth/signup",
            "-H", "Content-Type: application/json",
            "-d", json.dumps({"email": email, "password": password})
        ]

        print(f"\n[SETUP] Attempting signup for {email}...")
        signup_result = self.run_curl_command(signup_cmd)

        if signup_result.get("status_code") == 201:
            print(f"[SETUP] [OK] New user created: {email}")
        elif signup_result.get("status_code") == 400:
            print(f"[SETUP] [INFO] User already exists (expected if re-running tests)")
        else:
            print(f"[SETUP] [WARN] Signup returned status {signup_result.get('status_code')}")

        # Sign in to get token
        signin_cmd = [
            "curl", "-X", "POST", "-s", "-w", "\n%{http_code}",
            f"{self.api_url}/api/auth/signin",
            "-H", "Content-Type: application/json",
            "-d", json.dumps({"email": email, "password": password})
        ]

        print(f"[SETUP] Signing in as {email}...")
        signin_result = self.run_curl_command(signin_cmd)

        if signin_result.get("status_code") == 200 and signin_result.get("body"):
            body = signin_result["body"]
            self.jwt_token = body.get("token", "")
            user_data = body.get("user", {})
            self.user_id = str(user_data.get("id", ""))

            if self.jwt_token and self.user_id:
                print(f"[SETUP] [OK] Authentication successful")
                print(f"[SETUP]   User ID: {self.user_id}")
                print(f"[SETUP]   JWT Token: {self.jwt_token[:20]}...{self.jwt_token[-20:]}")
                return True
            else:
                print(f"[SETUP] [FAIL] Failed to extract token or user_id from response")
                return False
        else:
            print(f"[SETUP] [FAIL] Sign-in failed with status {signin_result.get('status_code')}")
            return False

    def send_chat_message(
        self,
        test_name: str,
        message: str,
        expected_tool: Optional[str] = None,
        expected_keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Send a chat message and validate response"""

        print(f"\n{'-' * 80}")
        print(f"TEST: {test_name}")
        print(f"{'-' * 80}")
        print(f"Message: \"{message}\"")

        # Build request payload
        payload = {"message": message}
        if self.conversation_id:
            payload["conversation_id"] = self.conversation_id

        # Build curl command
        cmd = [
            "curl", "-X", "POST", "-s", "-w", "\n%{http_code}",
            f"{self.api_url}/api/{self.user_id}/chat",
            "-H", f"Authorization: Bearer {self.jwt_token}",
            "-H", "Content-Type: application/json",
            "-d", json.dumps(payload)
        ]

        # Execute request
        result = self.run_curl_command(cmd)
        status_code = result.get("status_code", 0)
        body = result.get("body")

        # Initialize test result
        test_result = {
            "name": test_name,
            "message": message,
            "status": "pending",
            "expected_tool": expected_tool,
            "expected_keywords": expected_keywords or [],
            "actual_status": status_code,
            "timestamp": datetime.now().isoformat(),
            "validations": {}
        }

        # Validation checks
        validations = {}
        all_passed = True

        # Check 1: HTTP 200 response
        http_ok = status_code == 200
        validations["http_200"] = http_ok
        if http_ok:
            print(f"  [OK] HTTP 200 response")
        else:
            print(f"  [FAIL] HTTP {status_code} (expected 200)")
            all_passed = False

        if not body:
            print(f"  [FAIL] No response body received")
            test_result["status"] = "failed"
            test_result["validations"] = validations
            test_result["error"] = "No response body"
            self.results.append(test_result)
            return test_result

        # Store response data
        test_result["response"] = body

        # Check 2: conversation_id in response
        has_conversation_id = "conversation_id" in body
        validations["has_conversation_id"] = has_conversation_id
        if has_conversation_id:
            print(f"  [OK] conversation_id present: {body['conversation_id']}")
            # Update conversation_id for next request
            self.conversation_id = body["conversation_id"]
        else:
            print(f"  [FAIL] conversation_id missing from response")
            all_passed = False

        # Check 3: assistant_message in response
        has_message = "assistant_message" in body and body["assistant_message"]
        validations["has_assistant_message"] = has_message
        if has_message:
            assistant_message = body["assistant_message"]
            print(f"  [OK] assistant_message present ({len(assistant_message)} chars)")
            print(f"    Response: \"{assistant_message[:200]}{'...' if len(assistant_message) > 200 else ''}\"")
            test_result["assistant_message"] = assistant_message
        else:
            print(f"  [FAIL] assistant_message missing or empty")
            all_passed = False

        # Check 4: tool_calls array
        has_tool_calls = "tool_calls" in body
        validations["has_tool_calls"] = has_tool_calls
        if has_tool_calls:
            tool_calls = body["tool_calls"]
            print(f"  [OK] tool_calls array present: {tool_calls}")
            test_result["tool_calls"] = tool_calls

            # Check 5: Expected tool was called
            if expected_tool:
                tool_matched = expected_tool in tool_calls
                validations["expected_tool_called"] = tool_matched
                if tool_matched:
                    print(f"  [OK] Expected tool '{expected_tool}' was called")
                else:
                    print(f"  [FAIL] Expected tool '{expected_tool}' NOT called (got: {tool_calls})")
                    all_passed = False
        else:
            print(f"  [WARN] tool_calls array missing (AI may not have used tools)")
            if expected_tool:
                validations["expected_tool_called"] = False
                all_passed = False

        # Check 6: Response contains expected keywords
        if expected_keywords and has_message:
            keyword_matches = []
            assistant_message_lower = body["assistant_message"].lower()
            for keyword in expected_keywords:
                if keyword.lower() in assistant_message_lower:
                    keyword_matches.append(keyword)

            validations["keywords_found"] = keyword_matches
            if keyword_matches:
                print(f"  [OK] Found expected keywords: {keyword_matches}")
            else:
                print(f"  [WARN] No expected keywords found (looking for: {expected_keywords})")
                # Don't fail test for missing keywords, just note it

        # Check 7: Response is natural and relevant (heuristic)
        if has_message:
            message_length = len(body["assistant_message"])
            is_natural = message_length > 10  # At least a sentence
            validations["is_natural_response"] = is_natural
            if is_natural:
                print(f"  [OK] Response appears natural and complete")
            else:
                print(f"  [WARN] Response seems unusually short ({message_length} chars)")

        # Final status
        test_result["status"] = "passed" if all_passed else "failed"
        test_result["validations"] = validations

        status_icon = "[OK] PASS" if all_passed else "[FAIL] FAIL"
        print(f"\n{status_icon}: {test_name}")

        self.results.append(test_result)
        return test_result

    def generate_report(self):
        """Generate comprehensive test report"""
        passed = sum(1 for r in self.results if r.get("status") == "passed")
        failed = sum(1 for r in self.results if r.get("status") == "failed")
        total = len(self.results)
        pass_rate = (passed / total * 100) if total > 0 else 0

        # Save JSON report
        report_dir = Path(__file__).parent / "reports"
        report_dir.mkdir(exist_ok=True)

        json_file = report_dir / "chat-test-results.json"
        with open(json_file, 'w') as f:
            json.dump({
                "generated_at": datetime.now().isoformat(),
                "summary": {
                    "total": total,
                    "passed": passed,
                    "failed": failed,
                    "pass_rate": round(pass_rate, 2)
                },
                "results": self.results
            }, f, indent=2)

        # Generate markdown report
        md_report = f"""# Chat Endpoint E2E Test Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**API URL:** {self.api_url}
**User ID:** {self.user_id}
**Conversation ID:** {self.conversation_id or 'N/A'}

## Summary

- **Total Tests:** {total}
- **Passed:** {passed} [OK]
- **Failed:** {failed} [FAIL]
- **Pass Rate:** {pass_rate:.1f}%

## Test Objectives

This test suite validates that the chat endpoint correctly:
1. Understands natural language task commands
2. Calls appropriate MCP tools (add_task, list_tasks, complete_task, delete_task, update_task)
3. Returns natural, relevant responses
4. Maintains conversation context
5. Handles errors gracefully

## Test Results

"""
        for idx, result in enumerate(self.results, 1):
            status_icon = "[OK] PASS" if result["status"] == "passed" else "[FAIL] FAIL"
            md_report += f"### {idx}. {status_icon} {result['name']}\n\n"
            md_report += f"**User Message:** \"{result['message']}\"\n\n"

            if "assistant_message" in result:
                md_report += f"**AI Response:** \"{result['assistant_message']}\"\n\n"

            if "tool_calls" in result:
                md_report += f"**Tools Called:** {', '.join(result['tool_calls']) if result['tool_calls'] else 'None'}\n\n"

            if result.get("expected_tool"):
                md_report += f"**Expected Tool:** {result['expected_tool']}\n\n"

            # Validation details
            md_report += "**Validations:**\n\n"
            validations = result.get("validations", {})
            for check, passed_check in validations.items():
                if isinstance(passed_check, bool):
                    check_icon = "[OK]" if passed_check else "[FAIL]"
                    check_name = check.replace("_", " ").title()
                    md_report += f"- {check_icon} {check_name}\n"
                elif isinstance(passed_check, list):
                    # For keyword matches
                    check_name = check.replace("_", " ").title()
                    md_report += f"- {check_name}: {', '.join(passed_check) if passed_check else 'none'}\n"

            if "error" in result:
                md_report += f"\n**Error:** {result['error']}\n"

            md_report += f"\n**Timestamp:** {result['timestamp']}\n\n"
            md_report += "---\n\n"

        # Analysis section
        md_report += "## Analysis\n\n"

        # Tool usage analysis
        tool_calls_count = {}
        for result in self.results:
            for tool in result.get("tool_calls", []):
                tool_calls_count[tool] = tool_calls_count.get(tool, 0) + 1

        if tool_calls_count:
            md_report += "### Tool Usage\n\n"
            for tool, count in sorted(tool_calls_count.items()):
                md_report += f"- **{tool}:** {count} call{'s' if count > 1 else ''}\n"
            md_report += "\n"

        # Command understanding analysis
        md_report += "### Command Understanding\n\n"
        understood = sum(1 for r in self.results if r.get("validations", {}).get("expected_tool_called", False))
        total_with_expected = sum(1 for r in self.results if r.get("expected_tool"))
        if total_with_expected > 0:
            understanding_rate = (understood / total_with_expected * 100)
            md_report += f"- **Commands correctly understood:** {understood}/{total_with_expected} ({understanding_rate:.1f}%)\n"

        md_report += f"\n### Response Quality\n\n"
        natural_responses = sum(1 for r in self.results if r.get("validations", {}).get("is_natural_response", False))
        if total > 0:
            natural_rate = (natural_responses / total * 100)
            md_report += f"- **Natural responses:** {natural_responses}/{total} ({natural_rate:.1f}%)\n"

        # Save markdown report
        md_file = report_dir / "chat-test-report.md"
        with open(md_file, 'w') as f:
            f.write(md_report)

        # Print summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed} [OK]")
        print(f"Failed: {failed} [FAIL]")
        print(f"Pass Rate: {pass_rate:.1f}%")

        if tool_calls_count:
            print("\nTool Usage:")
            for tool, count in sorted(tool_calls_count.items()):
                print(f"  - {tool}: {count} call{'s' if count > 1 else ''}")

        print("=" * 80)
        print(f"\nReports saved:")
        print(f"  JSON: {json_file}")
        print(f"  Markdown: {md_file}")
        print()


def check_backend_health(api_url: str) -> bool:
    """Check if backend is running and healthy"""
    print("=" * 80)
    print("BACKEND HEALTH CHECK")
    print("=" * 80)
    print(f"Checking {api_url}...\n")

    try:
        # Try /health endpoint
        result = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", f"{api_url}/health"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.stdout == "200":
            print(f"[OK] Backend is healthy at {api_url}")
            return True

        # Try /docs endpoint as fallback
        result = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", f"{api_url}/docs"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.stdout == "200":
            print(f"[OK] Backend is accessible at {api_url}")
            return True

        print(f"[FAIL] Backend returned status {result.stdout}")
        print(f"\nPlease ensure the backend is running:")
        print(f"  cd backend")
        print(f"  uvicorn app.main:app --reload")
        return False

    except Exception as e:
        print(f"[FAIL] Cannot connect to backend: {e}")
        print(f"\nPlease ensure the backend is running:")
        print(f"  cd backend")
        print(f"  uvicorn app.main:app --reload")
        return False


def run_test_suite():
    """Run the complete chat endpoint test suite"""

    # Load environment variables
    if DOTENV_AVAILABLE:
        load_dotenv(Path(__file__).parent / ".env")

    api_url = os.getenv("API_URL", "http://localhost:8000")
    test_email = os.getenv("TEST_USER_EMAIL", "chat-test@example.com")
    test_password = os.getenv("TEST_USER_PASSWORD", "TestPassword123!")

    print("\n" + "=" * 80)
    print("CHAT ENDPOINT E2E TEST SUITE")
    print("=" * 80)
    print(f"API URL: {api_url}")
    print(f"Test User: {test_email}")
    print("=" * 80)

    # Check backend health
    if not check_backend_health(api_url):
        print("\n[FAIL] Testing aborted: Backend is not running")
        sys.exit(1)

    tester = ChatEndpointTester(api_url)

    # Authenticate
    if not tester.authenticate(test_email, test_password):
        print("\n[FAIL] Testing aborted: Authentication failed")
        sys.exit(1)

    # Run chat tests
    print("\n" + "=" * 80)
    print("CHAT ENDPOINT TESTS")
    print("=" * 80)

    # Test 1: Add task via natural language
    tester.send_chat_message(
        test_name="Add Task: 'buy milk'",
        message="add task buy milk",
        expected_tool="add_task",
        expected_keywords=["task", "created", "buy milk"]
    )

    # Test 2: Show tasks
    tester.send_chat_message(
        test_name="List Tasks: 'show my tasks'",
        message="show my tasks",
        expected_tool="list_tasks",
        expected_keywords=["task"]
    )

    # Test 3: Mark task as complete (natural phrasing)
    tester.send_chat_message(
        test_name="Complete Task: 'mark buy milk as complete'",
        message="mark the buy milk task as complete",
        expected_tool="complete_task",
        expected_keywords=["complete", "task"]
    )

    # Test 4: Update task
    tester.send_chat_message(
        test_name="Update Task: 'change buy milk to buy groceries'",
        message="change the buy milk task to buy groceries",
        expected_tool="update_task",
        expected_keywords=["update", "groceries"]
    )

    # Test 5: Delete task
    tester.send_chat_message(
        test_name="Delete Task: 'delete buy groceries'",
        message="delete the buy groceries task",
        expected_tool="delete_task",
        expected_keywords=["delete", "removed"]
    )

    # Test 6: Add another task with more natural phrasing
    tester.send_chat_message(
        test_name="Natural Add: 'I need to...'",
        message="I need to finish my homework tomorrow",
        expected_tool="add_task",
        expected_keywords=["task", "homework"]
    )

    # Test 7: Casual list request
    tester.send_chat_message(
        test_name="Casual List: 'what do I have to do?'",
        message="what do I have to do?",
        expected_tool="list_tasks",
        expected_keywords=["task"]
    )

    # Test 8: Conversational complete request
    tester.send_chat_message(
        test_name="Conversational Complete: 'I finished...'",
        message="I finished my homework",
        expected_tool="complete_task",
        expected_keywords=["complete", "homework"]
    )

    # Generate final report
    tester.generate_report()


if __name__ == "__main__":
    try:
        run_test_suite()
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
