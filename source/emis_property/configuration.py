import os
import tempfile


class Configuration:

    # Flask
    SECRET_KEY = os.environ.get("EMIS_PROPERTY_SECRET_KEY") or \
        "yabbadabbadoo!"
    JSON_AS_ASCII = False

    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # EMIS_PROPERTY_DATA = \
    #     os.environ.get("EMIS_PROPERTY_DATA") or \
    #     tempfile.gettempdir()


    @staticmethod
    def init_app(
            app):
        pass


class DevelopmentConfiguration(Configuration):

    DEBUG = True
    DEBUG_TOOLBAR_ENABLED = True
    FLASK_DEBUG_DISABLE_STRICT = True

    SQLALCHEMY_DATABASE_URI = \
        os.environ.get("EMIS_PROPERTY_DEV_DATABASE_URI") or \
        "sqlite:///" + os.path.join(tempfile.gettempdir(),
            "emis_property-dev.sqlite")


    @staticmethod
    def init_app(
            app):
        Configuration.init_app(app)

        from flask_debug import Debug
        Debug(app)


class TestConfiguration(Configuration):

    SERVER_NAME = os.environ.get("EMIS_PROPERTY_SERVER_NAME") or \
        "localhost"
    TESTING = True

    SQLALCHEMY_DATABASE_URI = \
        os.environ.get("EMIS_PROPERTY_TEST_DATABASE_URI") or \
        "sqlite:///" + os.path.join(tempfile.gettempdir(),
            "emis_property-test.sqlite")


class ProductionConfiguration(Configuration):

    SQLALCHEMY_DATABASE_URI = \
        os.environ.get("EMIS_PROPERTY_DATABASE_URI") or \
        "sqlite:///" + os.path.join(tempfile.gettempdir(),
            "emis_property.sqlite")


configuration = {
    "development": DevelopmentConfiguration,
    "test": TestConfiguration,
    "acceptance": ProductionConfiguration,
    "production": ProductionConfiguration
}
