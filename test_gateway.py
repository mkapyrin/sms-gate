"""Tests for SMS Gate — gateway, models, config."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from models import SendSMSRequest, WebhookRegistration, IncomingSMS


# --- Model tests ---

class TestModels:
    def test_send_sms_request_defaults(self):
        req = SendSMSRequest(phone_numbers=["+79001234567"], text="Hello")
        assert req.sim_number == 1
        assert req.with_delivery_report is True

    def test_send_sms_request_multiple_numbers(self):
        req = SendSMSRequest(
            phone_numbers=["+79001234567", "+79007654321"],
            text="Bulk test",
        )
        assert len(req.phone_numbers) == 2

    def test_webhook_registration_defaults(self):
        reg = WebhookRegistration(url="https://example.com/webhook")
        assert reg.event == "sms:received"

    def test_webhook_registration_custom_event(self):
        reg = WebhookRegistration(url="https://example.com/webhook", event="sms:delivered")
        assert reg.event == "sms:delivered"

    def test_incoming_sms(self):
        sms = IncomingSMS(event="sms:received", payload={"from": "+79001234567", "text": "Hi"})
        assert sms.event == "sms:received"
        assert sms.payload["text"] == "Hi"


# --- Gateway tests ---

class TestGateway:
    @pytest.fixture
    def gateway(self):
        with patch.dict("os.environ", {
            "ANDROID_GATEWAY_URL": "http://test:8081",
            "ANDROID_GATEWAY_USER": "test",
            "ANDROID_GATEWAY_PASS": "test",
            "API_KEY": "test-key",
        }):
            from gateway import AndroidGateway
            return AndroidGateway()

    @pytest.mark.asyncio
    async def test_send_sms_builds_correct_payload(self, gateway):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"id": "msg-123", "state": "Pending"}
        mock_resp.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_resp):
            result = await gateway.send_sms(["+79001234567"], "Test message")
            assert result["id"] == "msg-123"

    @pytest.mark.asyncio
    async def test_get_message(self, gateway):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"id": "msg-123", "state": "Delivered"}
        mock_resp.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_resp):
            result = await gateway.get_message("msg-123")
            assert result["state"] == "Delivered"
