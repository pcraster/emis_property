import datetime
import unittest
import uuid
from property import create_app
from property.api.schema import *


class PropertySchemaTestCase(unittest.TestCase):


    def setUp(self):
        self.app = create_app("testing")

        self.app_context = self.app.app_context()
        self.app_context.push()

        self.client = self.app.test_client()
        self.schema = PropertySchema()


    def tearDown(self):
        self.schema = None

        self.app_context.pop()


    def test_empty1(self):
        client_data = {
            }
        data, errors = self.schema.load(client_data)

        self.assertTrue(errors)
        self.assertEqual(errors, {
                "_schema": ["Input data must have a property key"]
            })


    def test_empty2(self):
        client_data = {
                "property": {}
            }
        data, errors = self.schema.load(client_data)

        self.assertTrue(errors)
        self.assertEqual(errors, {
                "name": ["Missing data for required field."],
                "pathname": ["Missing data for required field."],
            })


    def test_empty3(self):

        client_data = {
                "property": {
                    "name": "my_name",
                    "pathname": "my_pathname"
                }
            }
        data, errors = self.schema.load(client_data)

        self.assertFalse(errors)

        self.assertTrue(hasattr(data, "id"))
        self.assertTrue(isinstance(data.id, uuid.UUID))

        self.assertTrue(hasattr(data, "name"))
        self.assertEqual(data.name, "my_name")

        self.assertTrue(hasattr(data, "pathname"))
        self.assertEqual(data.pathname, "my_pathname")

        self.assertTrue(hasattr(data, "posted_at"))
        self.assertTrue(isinstance(data.posted_at, datetime.datetime))

        data.id = uuid.uuid4()
        data, errors = self.schema.dump(data)

        self.assertFalse(errors)
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


if __name__ == "__main__":
    unittest.main()
