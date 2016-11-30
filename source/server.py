import os
from property import create_app


app = create_app(os.getenv("EMIS_PROPERTY_CONFIGURATION"))
