from abc import ABC, abstractmethod
from email.utils import formataddr
from email.mime.text import MIMEText
from ja.common.job import Job, JobStatus
from smtplib import SMTP, SMTPConnectError
from typing import Dict

import ssl


class EmailServerBase(ABC):
    """
    A base class for sending emails.
    """
    @abstractmethod
    def send_email(self, subject: str, contents: str, send_to: str) -> None:
        """
        Send an email containing @contents to @send_to.

        @param subject The subject of the email.
        @param contents The contents of the email.
        @param send_to The email address to send the message to.
        """


class BasicEmailServer(EmailServerBase):
    _EMAIL_SENDER = "no-reply@jobadder.com"

    def __init__(self, smtp_server_address: str, smtp_server_port: int, smtp_user: str, smtp_password: str) -> None:
        """
        Construct a basic email server which sends emails using SMTPServer.

        @param smtp_server_address The address of the SMTP server to send emails from.
        @param smtp_server_port The address of the SMTP server to connect to.
        @param smtp_user The username to use when logging in into the SMTP server.
        @param smtp_password The password to use when logging in into the SMTP server.
        """
        self._email_client: SMTP = None
        try:
            self._email_client = SMTP(smtp_server_address, smtp_server_port)
            self._email_client.ehlo()
            self._email_client.starttls(context=ssl.SSLContext(ssl.PROTOCOL_TLS))
            self._email_client.ehlo()
            self._email_client.login(smtp_user, smtp_password)
        except (SMTPConnectError, ConnectionRefusedError) as e:
            print("Failed connecting to SMTP server at %s:%d. No email notifications will be sent" %
                  (smtp_server_address, smtp_server_port))
            print("Reason for the failure:")
            print(e)

    def __del__(self) -> None:
        if self._email_client:
            self._email_client.close()

    def send_email(self, subject: str, contents: str, send_to: str) -> None:
        if not self._email_client:
            return
        msg = MIMEText(contents)
        msg['To'] = formataddr((send_to, send_to))
        msg['From'] = formataddr(('JobAdder', self._EMAIL_SENDER))
        msg['Subject'] = subject

        self._email_client.sendmail(self._EMAIL_SENDER, send_to, msg.as_string())


class EmailNotifier:
    _send_email_for: Dict[JobStatus, str] = {
        JobStatus.CANCELLED: "been cancelled",
        JobStatus.CRASHED: "crashed",
        JobStatus.DONE: "finished running"
    }
    _EMAIL_TEMPLATE = "JobAdder notification: job %s has %s.\n\n" \
        "This email has been automatically generated. Please do not reply."

    """
    EmailNotifier is responsible for sending emails to the owners of a job when the job is finished running.
    """
    def __init__(self, email_server: EmailServerBase):
        """!
        Initialize the email notifier, and set the callback for the given database.

        @param email_server The email server to use for sending emails.
        """
        self._email_server = email_server

    def handle_job_status_updated(self, job: Job) -> None:
        """!
        Check whether a notification should be sent for the given job, and if yes, send it.
        A notification is sent only when the job is no longer running.

        @param job The job whose status was updated.
        """
        if job.status not in self._send_email_for or not job.email:
            return

        msg = self._EMAIL_TEMPLATE % (job.uid, self._send_email_for[job.status])
        subject = "JobAdder " + job.uid
        self._email_server.send_email(subject, msg, job.email)
