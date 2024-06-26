# Copyright 2024 Broadcom. All Rights Reserved.
from starlette import status
from starlette.testclient import TestClient

from config_modules_vmware.app import app
from config_modules_vmware.services.apis.controllers.consts import ABOUT_ENDPOINT
from config_modules_vmware.services.apis.controllers.consts import HEALTH_ENDPOINT
from config_modules_vmware.services.apis.models.about import About
from config_modules_vmware.services.apis.models.healthcheck import HealthCheck


class TestMiscController:

    def setup_method(self):
        self.client = TestClient(app)

    def test_get_about_endpoint(self):
        response = self.client.get(ABOUT_ENDPOINT)
        assert response.status_code == status.HTTP_200_OK
        assert response.content is not None
        about = About()
        assert response.json().get("name") == about.name
        assert response.json().get("description") == about.description
        assert response.json().get("version") == about.version
        assert response.json().get("author") == about.author

    def test_get_health_endpoint(self):
        response = self.client.get(HEALTH_ENDPOINT)
        assert response.status_code == status.HTTP_200_OK
        assert response.content is not None
        assert response.json().get("status") == HealthCheck().status
