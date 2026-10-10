import unittest

from chat_service import trim_history


class HistoryTests(unittest.TestCase):
    def test_system_prompt_is_preserved(self):
        messages = [{"role": "system", "content": "system"}]
        messages += [
            {"role": "user" if index % 2 == 0 else "assistant", "content": str(index)}
            for index in range(8)
        ]
        trimmed = trim_history(messages, max_messages=4)
        self.assertEqual(trimmed[0]["role"], "system")
        self.assertEqual([item["content"] for item in trimmed[1:]], ["4", "5", "6", "7"])


if __name__ == "__main__":
    unittest.main()
