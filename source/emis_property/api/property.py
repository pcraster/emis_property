from . import api_restful
from .resource import *


# - Get all properties
# - Post property
api_restful.add_resource(PropertiesResource,
    "/properties",
    endpoint="properties")


# - Get property by property-id
api_restful.add_resource(PropertyResource,
    "/properties/<uuid:property_id>",
    endpoint="property")

