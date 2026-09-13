"""Kiểm thử vòng ReAct bằng provider giả lập, không gọi API hoặc ghi trace nghiệm thu."""
import contextlib
import io
import sys
import unittest
from unittest.mock import Mock, patch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from app import run_react_agent
from mcp_server import MCPAcademicServer
from prompts import MAX_ITERATIONS
from providers import GeminiProvider


def tool(name, **arguments):
    return {"type": "tool_call", "tool_name": name, "arguments": arguments}


class SequenceProvider:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.prompts = []

    def generate_with_tools(self, prompt, tools_schema, system_prompt=""):
        self.prompts.append(prompt)
        return next(self.responses)


class RecordingServer(MCPAcademicServer):
    def __init__(self):
        super().__init__()
        self.calls = []

    def call_tool(self, name, arguments):
        self.calls.append((name, arguments))
        return super().call_tool(name, arguments)


class ReActLoopTests(unittest.TestCase):
    def test_api_error_does_not_execute_tools(self):
        logs, server = self.run_agent(SequenceProvider([
            {"type": "error", "content": "Gemini API lỗi 429", "status": "API_ERROR"}
        ]))
        self.assertEqual(server.calls, [])
        self.assertEqual(logs[-1]["status"], "API_ERROR")

    def run_agent(self, provider):
        server = RecordingServer()
        with contextlib.redirect_stdout(io.StringIO()):
            logs = run_react_agent("Tra cứu cố vấn rồi đặt lịch cho SV2026002", provider, server)
        return logs, server

    def test_lookup_then_booking_receives_observations(self):
        provider = SequenceProvider([
            tool("academic_query", student_id="SV2026002"),
            tool("schedule_appointment", student_id="SV2026002",
                 datetime_str="09:00 ngày 16/09/2026", advisor_name="TS. Lê Thị B"),
            {"type": "text", "content": "Đã đặt lịch với TS. Lê Thị B."}
        ])
        logs, server = self.run_agent(provider)
        self.assertEqual([name for name, _ in server.calls],
                         ["academic_query", "schedule_appointment"])
        self.assertIn('"advisor": "TS. Lê Thị B"', provider.prompts[1])
        self.assertIn('"booking_id": "BK-SV2026002-99"', provider.prompts[2])
        self.assertEqual([log["step"] for log in logs], [1, 2, 3])
        self.assertEqual(logs[-1]["output"], "Đã đặt lịch với TS. Lê Thị B.")

    def test_not_found_stops_before_booking(self):
        provider = SequenceProvider([tool("academic_query", student_id="SV9999999")])
        logs, server = self.run_agent(provider)
        self.assertEqual(len(server.calls), 1)
        self.assertEqual(logs[0]["observation"]["status"], "NOT_FOUND")
        self.assertIn("SV9999999", logs[-1]["output"])

    def test_direct_answer_does_not_call_tool(self):
        logs, server = self.run_agent(SequenceProvider([{"type": "text", "content": "Xin chào"}]))
        self.assertEqual(server.calls, [])
        self.assertEqual(logs[-1]["output"], "Xin chào")

    def test_duplicate_booking_is_not_executed_twice(self):
        booking = tool("schedule_appointment", student_id="SV2026002",
                       datetime_str="09:00 ngày 16/09/2026", advisor_name="TS. Lê Thị B")
        logs, server = self.run_agent(SequenceProvider([booking, booking]))
        self.assertEqual(len(server.calls), 1)
        self.assertEqual(logs[-1]["status"], "REPEATED_TOOL_CALL")

    def test_iteration_limit_is_reported(self):
        responses = [tool("schedule_appointment", student_id="SV2026002",
                          datetime_str=f"09:00 ngày {i + 1}/10/2026", advisor_name="TS. Lê Thị B")
                     for i in range(MAX_ITERATIONS)]
        logs, server = self.run_agent(SequenceProvider(responses))
        self.assertEqual(len(server.calls), MAX_ITERATIONS)
        self.assertEqual(logs[-1]["status"], "MAX_ITERATIONS")


class GeminiRateLimitTests(unittest.TestCase):
    @patch("providers.time.sleep")
    def test_rate_limit_retries_then_succeeds(self, sleep):
        error = Exception("quota exceeded")
        error.code = 429
        client = Mock()
        client.models.generate_content.side_effect = [error, "response"]
        provider = GeminiProvider(api_key="test-only")
        with patch("providers.time.monotonic", side_effect=[0, 60, 60]):
            self.assertEqual(provider._generate_content(client, model="test"), "response")
        sleep.assert_called_once_with(60)
        self.assertEqual(client.models.generate_content.call_count, 2)

    @patch("providers.time.sleep")
    def test_requests_are_spaced(self, sleep):
        provider = GeminiProvider(api_key="test-only")
        provider._last_request_at = 100
        with patch("providers.time.monotonic", side_effect=[102, 113]):
            provider._generate_content(Mock(), model="test")
        sleep.assert_called_once_with(11.0)

    @patch("providers.time.sleep")
    def test_persistent_quota_error_has_bounded_retries(self, sleep):
        error = Exception("quota exceeded")
        error.code = 429
        client = Mock()
        client.models.generate_content.side_effect = error
        provider = GeminiProvider(api_key="test-only")
        with patch("providers.time.monotonic", side_effect=[0, 60, 60, 120, 120]):
            with self.assertRaises(Exception):
                provider._generate_content(client, model="test")
        self.assertEqual(client.models.generate_content.call_count, 3)


if __name__ == "__main__":
    unittest.main()
