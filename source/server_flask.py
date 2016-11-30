import os
os.environ["EMIS_PROPERTY_CONFIGURATION"] = "development"
from server import app


app.run(host="0.0.0.0")
