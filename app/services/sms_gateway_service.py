import requests
from typing import List, Optional
from app.src.config.settings import settings


class SMSGatewayService:
    """
    Service for sending SMS notifications via a gateway.
    Supports multiple providers (Twilio, Africa's Talking, etc.)
    """

    def __init__(self, provider: str = "africas_talking"):
        self.provider = provider

        if provider.lower() == "africas_talking":
            self.api_key = settings.AFRICAS_TALKING_API_KEY
            self.sender_id = settings.AFRICAS_TALKING_SENDER_ID
            self.base_url = "https://api.sandbox.africastalking.com/version1/messaging"
        elif provider.lower() == "twilio":
            self.account_sid = settings.TWILIO_ACCOUNT_SID
            self.auth_token = settings.TWILIO_AUTH_TOKEN
            self.phone_from = settings.TWILIO_PHONE_FROM
            self.base_url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json"
        else:
            raise ValueError(f"Unsupported SMS provider: {provider}")

    def send_sms(self, phone_number: str, message: str) -> dict:
        """Send a single SMS."""
        if self.provider.lower() == "africas_talking":
            return self._send_africas_talking(phone_number, message)
        elif self.provider.lower() == "twilio":
            return self._send_twilio(phone_number, message)

    def send_bulk_sms(self, phone_numbers: List[str], message: str) -> dict:
        """Send SMS to multiple recipients."""
        results = {
            "successful": [],
            "failed": [],
        }

        for phone in phone_numbers:
            try:
                result = self.send_sms(phone, message)
                if result.get("success"):
                    results["successful"].append(phone)
                else:
                    results["failed"].append(phone)
            except Exception as e:
                results["failed"].append(phone)

        return results

    def _send_africas_talking(self, phone_number: str, message: str) -> dict:
        """Send SMS via Africa's Talking."""
        try:
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
                "apiKey": self.api_key,
            }

            payload = {
                "username": "sandbox",
                "to": phone_number,
                "message": message,
                "from": self.sender_id,
            }

            response = requests.post(
                self.base_url,
                headers=headers,
                data=payload,
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                if data["SMSMessageData"]["Message"] == "Sent":
                    return {
                        "success": True,
                        "message_id": data["SMSMessageData"]["Recipients"][0]["id"],
                    }

            return {"success": False, "error": response.text}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _send_twilio(self, phone_number: str, message: str) -> dict:
        """Send SMS via Twilio."""
        try:
            auth = (self.account_sid, self.auth_token)
            payload = {
                "From": self.phone_from,
                "To": phone_number,
                "Body": message,
            }

            response = requests.post(
                self.base_url,
                data=payload,
                auth=auth,
                timeout=10,
            )

            if response.status_code == 201:
                data = response.json()
                return {"success": True, "message_id": data["sid"]}

            return {"success": False, "error": response.text}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def send_deposit_notification(
        self,
        phone_number: str,
        amount: float,
        account_number: str,
    ) -> dict:
        """Send deposit confirmation SMS."""
        message = f"Your deposit of {amount:,.2f} to account {account_number} has been received. Thank you!"
        return self.send_sms(phone_number, message)

    def send_withdrawal_notification(
        self,
        phone_number: str,
        amount: float,
        account_number: str,
        balance: float,
    ) -> dict:
        """Send withdrawal confirmation SMS."""
        message = f"Withdrawal of {amount:,.2f} from account {account_number} successful. New balance: {balance:,.2f}"
        return self.send_sms(phone_number, message)

    def send_transfer_notification(
        self,
        phone_number: str,
        amount: float,
        recipient: str,
    ) -> dict:
        """Send fund transfer notification SMS."""
        message = f"You have sent {amount:,.2f} to {recipient}. Thank you!"
        return self.send_sms(phone_number, message)

    def send_loan_approval_notification(
        self,
        phone_number: str,
        loan_amount: float,
        loan_term: int,
    ) -> dict:
        """Send loan approval notification SMS."""
        message = f"Your loan of {loan_amount:,.2f} for {loan_term} months has been approved! Visit your branch for disbursement."
        return self.send_sms(phone_number, message)

    def send_loan_payment_reminder(
        self,
        phone_number: str,
        amount_due: float,
        due_date: str,
    ) -> dict:
        """Send loan payment reminder SMS."""
        message = f"Reminder: {amount_due:,.2f} is due on {due_date}. Pay now to avoid penalties."
        return self.send_sms(phone_number, message)

    def send_dividend_notification(
        self,
        phone_number: str,
        dividend_amount: float,
    ) -> dict:
        """Send dividend notification SMS."""
        message = f"Congratulations! Your dividend of {dividend_amount:,.2f} has been credited to your account."
        return self.send_sms(phone_number, message)


# Global instances
sms_service_africas_talking = SMSGatewayService(provider="africas_talking")
sms_service_twilio = SMSGatewayService(provider="twilio")
