from pydantic import BaseModel


class SendSMSRequest(BaseModel):
    phone_numbers: list[str]
    text: str
    sim_number: int = 1
    with_delivery_report: bool = True


class WebhookRegistration(BaseModel):
    url: str
    event: str = "sms:received"  # sms:received | sms:delivered


class IncomingSMS(BaseModel):
    event: str
    payload: dict
