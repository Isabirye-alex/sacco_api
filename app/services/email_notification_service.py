"""Module for app.services.email_notification_service."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
from datetime import date
import asyncio
from app.src.config.settings import settings


class EmailNotificationService:
    """Service for sending email notifications."""

    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.sender_email = settings.SENDER_EMAIL
        self.sender_password = settings.SENDER_PASSWORD

    def send_email(
        self,
        recipient_email: str,
        subject: str,
        body: str,
        is_html: bool = False,
    ) -> bool:
        """
        Send a single email.

        Args:
            recipient_email: Email address of recipient
            subject: Email subject
            body: Email body
            is_html: Whether body is HTML formatted

        Returns:
            True if successful, False otherwise
        """
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = recipient_email

            mime_type = "html" if is_html else "plain"
            message.attach(MIMEText(body, mime_type))

            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.sender_email, self.sender_password)
                server.sendmail(
                    self.sender_email,
                    recipient_email,
                    message.as_string(),
                )

            return True
        except Exception as e:
            print(f"Failed to send email to {recipient_email}: {str(e)}")
            return False

    def send_bulk_email(
        self,
        recipient_emails: List[str],
        subject: str,
        body: str,
        is_html: bool = False,
    ) -> dict:
        """Send emails to multiple recipients."""
        results = {
            "successful": [],
            "failed": [],
        }

        for email in recipient_emails:
            if self.send_email(email, subject, body, is_html):
                results["successful"].append(email)
            else:
                results["failed"].append(email)

        return results

    def send_deposit_confirmation(
        self,
        recipient_email: str,
        member_name: str,
        account_number: str,
        amount: float,
        balance_after: float,
    ) -> bool:
        """Send deposit confirmation email."""
        subject = "Deposit Confirmation - SACCO"
        body = f"""
        <html>
            <body>
                <h2>Deposit Confirmation</h2>
                <p>Dear {member_name},</p>
                <p>Your deposit has been successfully processed:</p>
                <ul>
                    <li><strong>Account Number:</strong> {account_number}</li>
                    <li><strong>Amount Deposited:</strong> {amount:,.2f}</li>
                    <li><strong>New Balance:</strong> {balance_after:,.2f}</li>
                    <li><strong>Date:</strong> {date.today()}</li>
                </ul>
                <p>Thank you for your transaction.</p>
                <p>Best Regards,<br/>SACCO Management</p>
            </body>
        </html>
        """
        return self.send_email(recipient_email, subject, body, is_html=True)

    def send_withdrawal_confirmation(
        self,
        recipient_email: str,
        member_name: str,
        account_number: str,
        amount: float,
        balance_after: float,
    ) -> bool:
        """Send withdrawal confirmation email."""
        subject = "Withdrawal Confirmation - SACCO"
        body = f"""
        <html>
            <body>
                <h2>Withdrawal Confirmation</h2>
                <p>Dear {member_name},</p>
                <p>Your withdrawal has been successfully processed:</p>
                <ul>
                    <li><strong>Account Number:</strong> {account_number}</li>
                    <li><strong>Amount Withdrawn:</strong> {amount:,.2f}</li>
                    <li><strong>Remaining Balance:</strong> {balance_after:,.2f}</li>
                    <li><strong>Date:</strong> {date.today()}</li>
                </ul>
                <p>Thank you for your transaction.</p>
                <p>Best Regards,<br/>SACCO Management</p>
            </body>
        </html>
        """
        return self.send_email(recipient_email, subject, body, is_html=True)

    def send_loan_approval_notification(
        self,
        recipient_email: str,
        member_name: str,
        loan_amount: float,
        interest_rate: float,
        maturity_date: str,
    ) -> bool:
        """Send loan approval notification email."""
        subject = "Loan Application Approved - SACCO"
        body = f"""
        <html>
            <body>
                <h2>Loan Application Approved</h2>
                <p>Dear {member_name},</p>
                <p>Congratulations! Your loan application has been approved.</p>
                <p><strong>Loan Details:</strong></p>
                <ul>
                    <li><strong>Approved Amount:</strong> {loan_amount:,.2f}</li>
                    <li><strong>Interest Rate:</strong> {interest_rate}%</li>
                    <li><strong>Maturity Date:</strong> {maturity_date}</li>
                </ul>
                <p>Please visit your nearest branch or login to your account for further details and disbursement instructions.</p>
                <p>Best Regards,<br/>SACCO Management</p>
            </body>
        </html>
        """
        return self.send_email(recipient_email, subject, body, is_html=True)

    def send_transfer_notification(
        self,
        sender_email: str,
        sender_name: str,
        recipient_name: str,
        amount: float,
        from_account: str,
        to_account: str,
    ) -> bool:
        """Send fund transfer notification email."""
        subject = "Fund Transfer Confirmation - SACCO"
        body = f"""
        <html>
            <body>
                <h2>Fund Transfer Confirmation</h2>
                <p>Dear {sender_name},</p>
                <p>Your fund transfer has been successfully processed:</p>
                <ul>
                    <li><strong>From Account:</strong> {from_account}</li>
                    <li><strong>To Account:</strong> {to_account}</li>
                    <li><strong>Recipient:</strong> {recipient_name}</li>
                    <li><strong>Amount Transferred:</strong> {amount:,.2f}</li>
                    <li><strong>Date:</strong> {date.today()}</li>
                </ul>
                <p>Best Regards,<br/>SACCO Management</p>
            </body>
        </html>
        """
        return self.send_email(sender_email, subject, body, is_html=True)

    def send_dividend_notification(
        self,
        recipient_email: str,
        member_name: str,
        dividend_amount: float,
        product_name: str,
    ) -> bool:
        """Send dividend distribution notification email."""
        subject = "Dividend Distribution - SACCO"
        body = f"""
        <html>
            <body>
                <h2>Dividend Distribution</h2>
                <p>Dear {member_name},</p>
                <p>Your dividend has been credited to your account:</p>
                <ul>
                    <li><strong>Product:</strong> {product_name}</li>
                    <li><strong>Dividend Amount:</strong> {dividend_amount:,.2f}</li>
                    <li><strong>Credit Date:</strong> {date.today()}</li>
                </ul>
                <p>Thank you for your investment.</p>
                <p>Best Regards,<br/>SACCO Management</p>
            </body>
        </html>
        """
        return self.send_email(recipient_email, subject, body, is_html=True)


# Global instance
email_service = EmailNotificationService()
