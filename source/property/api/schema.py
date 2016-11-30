import datetime
import uuid
from marshmallow import fields, post_dump, post_load, pre_load, ValidationError
from .. import ma
from .model import PropertyModel


def must_not_be_blank(
        data):
    if not data:
        raise ValidationError("Data not provided")


# def must_be_one_of(
#         values):
# 
#     def validator(
#             data):
#         if not data in values:
#             raise ValidationError("Value must be one of {}".format(" ".join(
#                 values)))
# 
#     return validator


class PropertySchema(ma.Schema):

    class Meta:
        # Fields to include in the serialized result.
        fields = ("user", "name", "pathname", "_links")


    id = fields.UUID(dump_only=True)
    user = fields.UUID(required=True)
    name = fields.Str(required=True)
    pathname = fields.Str(required=True)
    posted_at = fields.DateTime(dump_only=True,
        missing=datetime.datetime.utcnow().isoformat())
    _links = ma.Hyperlinks({
            "self": ma.URLFor("api.property", user_id="<user>",
                property_id="<id>"),
            "collection": ma.URLFor("api.properties", user_id="<user>")
        })


    def key(self,
            many):
        return "properties" if many else "property"


    @pre_load(
        pass_many=True)
    def unwrap(self,
            data,
            many):
        key = self.key(many)

        if key not in data:
            raise ValidationError("Input data must have a {} key".format(key))

        return data[key]


    @post_dump(
        pass_many=True)
    def wrap(self,
            data, many):
        key = self.key(many)

        return {
            key: data
        }


    @post_load
    def make_object(self,
            data):
        return PropertyModel(
            id=uuid.uuid4(),
            user=data["user"],
            name=data["name"],
            pathname = data["pathname"],
            posted_at=datetime.datetime.utcnow()
        )
