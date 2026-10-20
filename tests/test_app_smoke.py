"""Static regression checks for the Streamlit app's key UX contracts.

These checks do not call Streamlit, Groq, or Google Sheets. They catch syntax
errors and accidental removal of important UI/save-flow safeguards in CI.
"""
import ast
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "app.py"
SOURCE = APP_PATH.read_text(encoding="utf-8")


class AppSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tree = ast.parse(SOURCE, filename=str(APP_PATH))

    def test_app_parses_as_python(self):
        self.assertIsNotNone(self.tree)

    def test_ai_response_renderer_handles_empty_and_warning_responses(self):
        self.assertIn("def render_ai_answer(", SOURCE)
        self.assertIn("if answer is None or not str(answer).strip():", SOURCE)
        self.assertIn('answer_text.startswith(("⚠️", "❌", "Error:", "ERROR:"))', SOURCE)

    def test_ai_prompts_use_shared_response_renderer(self):
        self.assertIn('render_ai_answer(ans)', SOURCE)
        self.assertIn('render_ai_answer(answer)', SOURCE)
        self.assertIn('render_ai_answer(plan, "📅 आपका 30-Day Plan")', SOURCE)
        self.assertNotIn("st.success(ans)", SOURCE)
        self.assertNotIn("st.success(answer)", SOURCE)
        self.assertNotIn("st.success(plan)", SOURCE)

    def test_body_history_csv_export_is_present(self):
        self.assertIn("Body History CSV डाउनलोड करें", SOURCE)
        self.assertIn('df_body.to_csv(index=False).encode("utf-8-sig")', SOURCE)

    def test_workout_csv_export_is_present(self):
        self.assertIn('df.to_csv(index=False).encode("utf-8")', SOURCE)
        self.assertIn('mime="text/csv"', SOURCE)

    def test_existing_save_and_timer_controls_are_present(self):
        for marker in (
            'key="sw_start"',
            'key="sw_pause"',
            'key="sw_reset"',
            'st.session_state.rest_timer = 30',
            'st.session_state.rest_timer = 60',
            'st.session_state.rest_timer = 90',
            'def save_data(',
            'def gsheet_save_body_stats(',
            'def gsheet_save_weekly(',
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, SOURCE)

    def test_existing_workout_log_schema_is_still_referenced(self):
        for field in ('"Date"', '"Time"', '"Body Part"', '"Exercise"', '"Weight (kg)"', '"Status"'):
            with self.subTest(field=field):
                self.assertIn(field, SOURCE)


if __name__ == "__main__":
    unittest.main()
