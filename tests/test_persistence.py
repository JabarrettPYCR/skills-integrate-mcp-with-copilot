import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException

import src.app as app_module


class ActivityPersistenceTests(unittest.TestCase):
    def test_signup_and_unregister_survive_database_reinitialization(self):
        with tempfile.TemporaryDirectory() as directory:
            database_path = Path(directory) / "activities.sqlite"
            with patch.object(app_module, "DATABASE_PATH", database_path):
                app_module.initialize_database()
                app_module.signup_for_activity("Chess Club", "new@mergington.edu")

                app_module.initialize_database()
                participants = app_module.get_activities()["Chess Club"]["participants"]
                self.assertIn("new@mergington.edu", participants)
                with self.assertRaises(HTTPException) as duplicate:
                    app_module.signup_for_activity("Chess Club", "new@mergington.edu")
                self.assertEqual(duplicate.exception.status_code, 400)

                app_module.unregister_from_activity("Chess Club", "new@mergington.edu")
                app_module.initialize_database()
                participants = app_module.get_activities()["Chess Club"]["participants"]
                self.assertNotIn("new@mergington.edu", participants)
                self.assertIn("michael@mergington.edu", participants)


if __name__ == "__main__":
    unittest.main()