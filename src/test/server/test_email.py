from ja.common.job import Job, JobStatus
from ja.server.email import EmailNotifier, EmailServerBase
from unittest import TestCase


_global_job_counter = 0


def get_job(st: JobStatus = None, email: str = None) -> Job:
    global _global_job_counter
    job = Job(owner_id=0, email=email, status=st, scheduling_constraints=None,
              docker_context=None, docker_constraints=None)
    job.uid = str(_global_job_counter)
    _global_job_counter += 1
    return job


class MockEmailServer(EmailServerBase):
    def __init__(self, unit: TestCase):
        self._unit = unit
        self._subject: str = None
        self._msg: str = None
        self._email: str = None

    def set_expectation(self, exp_subject: str, exp_msg: str, exp_email: str) -> None:
        # Assert that we do not have leftovers from previous calls
        self._unit.assertIsNone(self._subject)
        self._unit.assertIsNone(self._msg)
        self._unit.assertIsNone(self._email)
        (self._subject, self._msg, self._email) = (exp_subject, exp_msg, exp_email)

    def send_email(self, subject: str, contents: str, send_to: str) -> None:
        self._unit.assertIsNotNone(subject)
        self._unit.assertIsNotNone(contents)
        self._unit.assertIsNotNone(send_to)

        self._unit.assertEqual(subject, self._subject)
        self._unit.assertEqual(contents, self._msg)
        self._unit.assertEqual(send_to, self._email)
        self._subject = self._msg = self._email = None


class EmailNotifierTest(TestCase):
    EMAIL = 'zemisemki@hotmail.com'

    def setUp(self) -> None:
        self._server = MockEmailServer(self)
        self._notifier = EmailNotifier(self._server)

    def test_no_trigger(self) -> None:
        for status in [JobStatus.QUEUED, JobStatus.RUNNING, JobStatus.PAUSED]:
            self._notifier.handle_job_status_updated(get_job(status, email=self.EMAIL))

    def test_email_sent(self) -> None:
        for status in EmailNotifier._send_email_for:
            job = get_job(status, email=self.EMAIL)
            msg = EmailNotifier._EMAIL_TEMPLATE % (job.uid, EmailNotifier._send_email_for[status])
            self._server.set_expectation("JobAdder " + job.uid, msg, self.EMAIL)
            self._notifier.handle_job_status_updated(job)

        # Test all have been called
        self._server.set_expectation(None, None, None)

    def test_no_email(self) -> None:
        self._notifier.handle_job_status_updated(get_job(JobStatus.DONE, email=None))
