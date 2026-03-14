import hmac
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Header, HTTPException

from adb import ADBManager
from config import settings
from gateway import gateway
from models import IncomingSMS, SendSMSRequest, WebhookRegistration

inbox: list[dict] = []
adb = ADBManager(local_port=settings.android_gateway_port, remote_port=8080)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup ADB port forwarding on startup
    if await adb.is_device_connected():
        device = await adb.get_device_info()
        print(f"Android device: {device['model']} (Android {device['android']})")
        await adb.setup_port_forward()
        print(f"ADB forward: localhost:{settings.android_gateway_port} -> device:8080")
    else:
        print("WARNING: No Android device connected via USB")

    healthy = await gateway.health()
    status = "connected" if healthy else "not reachable (check USB + SMS Gateway app)"
    print(f"Android Gateway: {status}")
    yield
    # Cleanup port forward on shutdown
    await adb.remove_port_forward()


app = FastAPI(title="SMS Gate", version="0.1.0", lifespan=lifespan)


def verify_api_key(x_api_key: str = Header()):
    if not hmac.compare_digest(x_api_key, settings.api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")


@app.get("/health")
async def health():
    device_connected = await adb.is_device_connected()
    gw_ok = await gateway.health()
    return {
        "status": "ok",
        "usb_device": "connected" if device_connected else "disconnected",
        "gateway": "connected" if gw_ok else "disconnected",
    }


@app.get("/device")
async def device_info(x_api_key: str = Header()):
    verify_api_key(x_api_key)
    info = await adb.get_device_info()
    if not info:
        raise HTTPException(status_code=503, detail="No Android device connected via USB")
    forwards = await adb.list_forwards()
    return {"device": info, "port_forwards": forwards}


@app.post("/device/reconnect")
async def reconnect_device(x_api_key: str = Header()):
    verify_api_key(x_api_key)
    if not await adb.is_device_connected():
        raise HTTPException(status_code=503, detail="No Android device connected via USB")
    await adb.setup_port_forward()
    healthy = await gateway.health()
    return {"status": "reconnected", "gateway": "connected" if healthy else "disconnected"}


@app.post("/sms/send")
async def send_sms(req: SendSMSRequest, x_api_key: str = Header()):
    verify_api_key(x_api_key)
    result = await gateway.send_sms(
        phone_numbers=req.phone_numbers,
        text=req.text,
        sim_number=req.sim_number,
        with_delivery_report=req.with_delivery_report,
    )
    return result


@app.get("/sms/{message_id}")
async def get_message_status(message_id: str, x_api_key: str = Header()):
    verify_api_key(x_api_key)
    return await gateway.get_message(message_id)


@app.get("/sms/inbox")
async def get_inbox(x_api_key: str = Header(), limit: int = 50):
    verify_api_key(x_api_key)
    return inbox[-limit:]


@app.post("/webhook/incoming")
async def webhook_incoming(data: IncomingSMS):
    """Endpoint for Android SMS Gateway to push incoming SMS."""
    entry = {
        "event": data.event,
        "payload": data.payload,
        "received_at": datetime.now().isoformat(),
    }
    inbox.append(entry)
    return {"status": "ok"}


@app.post("/webhooks/register")
async def register_webhook(req: WebhookRegistration, x_api_key: str = Header()):
    verify_api_key(x_api_key)
    result = await gateway.register_webhook(
        webhook_id=f"smsgate_{req.event.replace(':', '_')}",
        url=req.url,
        event=req.event,
    )
    return result


@app.get("/webhooks")
async def list_webhooks(x_api_key: str = Header()):
    verify_api_key(x_api_key)
    return await gateway.list_webhooks()


@app.delete("/webhooks/{webhook_id}")
async def delete_webhook(webhook_id: str, x_api_key: str = Header()):
    verify_api_key(x_api_key)
    await gateway.delete_webhook(webhook_id)
    return {"status": "deleted"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=settings.api_host, port=settings.api_port, reload=True)
