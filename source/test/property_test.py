import os.path
import unittest
import uuid
from flask import current_app, json
from property import create_app, db
from property.api.schema import *


class PropertyTestCase(unittest.TestCase):


    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()


    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()


    def post_properties(self):

        payloads = [
                {
                    "name": "my_name1",
                    "pathname": "my_pathname1",
                },
                {
                    "name": "my_name2",
                    "pathname": "my_pathname2",
                },
                {
                    "name": "my_name3",
                    "pathname": "my_pathname3",
                },
            ]

        for payload in payloads:
            response = self.client.post("/properties",
                data=json.dumps({"property": payload}),
                content_type="application/json")
            data = response.data.decode("utf8")

            self.assertEqual(response.status_code, 201, "{}: {}".format(
                response.status_code, data))


    def test_get_all_properties1(self):
        # No properties posted.
        response = self.client.get("/properties")
        data = response.data.decode("utf8")

        self.assertEqual(response.status_code, 200, "{}: {}".format(
            response.status_code, data))

        data = json.loads(data)

        self.assertTrue("properties" in data)
        self.assertEqual(data["properties"], [])


    def test_get_all_properties2(self):
        # Some properties posted.
        self.post_properties()

        response = self.client.get("/properties")
        data = response.data.decode("utf8")

        self.assertEqual(response.status_code, 200, "{}: {}".format(
            response.status_code, data))

        data = json.loads(data)

        self.assertTrue("properties" in data)

        properties = data["properties"]

        self.assertEqual(len(properties), 3)


    def test_get_property(self):
        self.post_properties()

        response = self.client.get("/properties")
        data = response.data.decode("utf8")
        data = json.loads(data)
        properties = data["properties"]
        property = properties[0]
        uri = property["_links"]["self"]
        response = self.client.get(uri)

        data = response.data.decode("utf8")

        self.assertEqual(response.status_code, 200, "{}: {}".format(
            response.status_code, data))

        data = json.loads(data)

        self.assertTrue("property" in data)

        self.assertEqual(data["property"], property)

        self.assertTrue("id" not in property)
        self.assertTrue("posted_at" not in property)

        self.assertTrue("name" in property)
        self.assertEqual(property["name"], "my_name1")

        self.assertTrue("pathname" in property)
        self.assertEqual(property["pathname"], "my_pathname1")

        self.assertTrue("_links" in property)

        links = property["_links"]

        self.assertTrue("self" in links)
        self.assertEqual(links["self"], uri)

        self.assertTrue("collection" in links)


    def test_get_unexisting_property(self):
        self.post_properties()

        response = self.client.get("/properties")
        data = response.data.decode("utf8")
        data = json.loads(data)
        properties = data["properties"]
        property = properties[0]
        uri = property["_links"]["self"]
        # Invalidate uri
        uri = os.path.join(os.path.split(uri)[0], str(uuid.uuid4()))
        response = self.client.get(uri)

        data = response.data.decode("utf8")

        self.assertEqual(response.status_code, 400, "{}: {}".format(
            response.status_code, data))

        data = json.loads(data)

        self.assertTrue("message" in data)


    def test_post_property(self):
        payload = {
                "name": "my_name",
                "pathname": "my_pathname",
            }
        response = self.client.post("/properties",
            data=json.dumps({"property": payload}),
            content_type="application/json")
        data = response.data.decode("utf8")

        self.assertEqual(response.status_code, 201, "{}: {}".format(
            response.status_code, data))

        data = json.loads(data)

        self.assertTrue("property" in data)

        property = data["property"]

        self.assertTrue("id" not in property)
        self.assertTrue("posted_at" not in property)

        self.assertTrue("name" in property)
        self.assertEqual(property["name"], "my_name")

        self.assertTrue("pathname" in property)
        self.assertEqual(property["pathname"], "my_pathname")

        self.assertTrue("_links" in property)

        links = property["_links"]

        self.assertTrue("self" in links)
        self.assertTrue("collection" in links)


    def test_post_bad_request(self):
        response = self.client.post("/properties")
        data = response.data.decode("utf8")

        self.assertEqual(response.status_code, 400, "{}: {}".format(
            response.status_code, data))

        data = json.loads(data)

        self.assertTrue("message" in data)


    def test_post_unprocessable_entity(self):
        payload = ""
        response = self.client.post("/properties",
            data=json.dumps({"property": payload}),
            content_type="application/json")
        data = response.data.decode("utf8")

        self.assertEqual(response.status_code, 422, "{}: {}".format(
            response.status_code, data))

        data = json.loads(data)

        self.assertTrue("message" in data)


    def test_delete_property(self):
        payload = {
                "name": "my_name",
                "pathname": "my_pathname",
            }
        response = self.client.post("/properties",
            data=json.dumps({"property": payload}),
            content_type="application/json")
        data = response.data.decode("utf8")

        self.assertEqual(response.status_code, 201, "{}: {}".format(
            response.status_code, data))

        data = json.loads(data)
        property = data["property"]
        links = property["_links"]
        self_uri = links["self"]

        response = self.client.delete(self_uri)
        data = response.data.decode("utf8")

        self.assertEqual(response.status_code, 204)


if __name__ == "__main__":
    unittest.main()
