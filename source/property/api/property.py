from . import api_restful
from .resource import *


# All properties.
# - Get all properties
# - Post property by user-id
api_restful.add_resource(PropertiesAllResource,
    "/properties",
    endpoint="properties_all")

# Property by user-id and property-id.
# - Get property by user-id and property-id
api_restful.add_resource(PropertyResource,
    "/properties/<uuid:user_id>/<uuid:property_id>",
    endpoint="property")

# Properties by user-id.
# - Get properties by user-id
api_restful.add_resource(PropertiesResource,
    "/properties/<uuid:user_id>",
    endpoint="properties")
