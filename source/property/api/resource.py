from werkzeug.exceptions import *
from flask_restful import Resource
from flask import request
from .. import db
from .model import PropertyModel
from .schema import PropertySchema


property_schema = PropertySchema()


class PropertyResource(Resource):

    def get(self,
            user_id,
            property_id):

        # user_id is not needed
        property = PropertyModel.query.get(property_id)

        if property is None or property.user != user_id:
            raise BadRequest("Property could not be found")


        data, errors = property_schema.dump(property)

        if errors:
            raise InternalServerError(errors)


        return data


class PropertiesResource(Resource):

    def get(self,
            user_id):

        properties = PropertyModel.query.filter_by(user=user_id)
        data, errors = property_schema.dump(properties, many=True)

        if errors:
            raise InternalServerError(errors)

        assert isinstance(data, dict), data


        return data


class PropertiesAllResource(Resource):


    # TODO Only call this from admin interface!
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
