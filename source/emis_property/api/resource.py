from werkzeug.exceptions import *
from flask_restful import Resource
from flask import request
from .. import db
from .model import PropertyModel
from .schema import PropertySchema


property_schema = PropertySchema()


class PropertyResource(Resource):

    def get(self,
            property_id):

        property = PropertyModel.query.get(property_id)

        if property is None:
            raise BadRequest("Property could not be found")


        data, errors = property_schema.dump(property)

        if errors:
            raise InternalServerError(errors)


        return data


    def delete(self,
            property_id):

        property = PropertyModel.query.get(property_id)

        if property is None:
            raise BadRequest("Property could not be found")


        db.session.delete(property)
        db.session.commit()


        # From property to dict representing a property.
        data, errors = property_schema.dump(property)
        assert not errors, errors
        assert isinstance(data, dict), data

        # # Remove links, there is no resource anymore.
        # # TODO Use Marshmallow contexts?
        # del data["property"]["_links"]


        # return data, 204

        return "", 204


class PropertiesResource(Resource):


    def get(self):

        properties = PropertyModel.query.all()
        data, errors = property_schema.dump(properties, many=True)

        if errors:
            raise InternalServerError(errors)

        assert isinstance(data, dict), data


        return data


    def post(self):

        json_data = request.get_json()

        if json_data is None:
            raise BadRequest("No input data provided")


        # Validate and deserialize input.
        property, errors = property_schema.load(json_data)

        if errors:
            raise UnprocessableEntity(errors)


        # Write property to database.
        db.session.add(property)
        db.session.commit()


        # From record in database to dict representing a property.
        data, errors = property_schema.dump(
            PropertyModel.query.get(property.id))
        assert not errors, errors
        assert isinstance(data, dict), data


        return data, 201
