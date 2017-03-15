import unittest
from flask import current_app, json
from emis_property import create_app


class AppTest(unittest.TestCase):

    def setUp(self):
        self.app = create_app("test")
        self.app_context = self.app.app_context()
        self.app_context.push()

        self.client = self.app.test_client()


    def tearDown(self):
        self.app_context.pop()


    def test_app_exists(self):
        self.assertFalse(current_app is None)


    def test_app_is_testing(self):
        self.assertTrue(current_app.config["TESTING"])


    def test_ping(self):
        response = self.client.get("/ping")
        data = response.data.decode("utf8")
        self.assertEqual(response.status_code, 200, data)
        data = json.loads(data)
        self.assertEqual(data, {"response": "pong"})


    def test_not_found(self):
        response = self.client.get("/meh")
        data = response.data.decode("utf8")
        self.assertEqual(response.status_code, 404, data)
        data = json.loads(data)
        self.assertEqual(data["status_code"], 404)
        self.assertNotEqual(data["message"].find(
            "requested URL was not found on the server"), -1)


if __name__ == "__main__":
    unittest.main()
