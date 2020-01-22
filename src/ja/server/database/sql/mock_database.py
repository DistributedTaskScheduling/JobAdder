from copy import deepcopy
from typing import List, Optional
from datetime import datetime
import testing.postgresql
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from ja.common.job import Job, JobStatus
from ja.server.database.types.job_entry import DatabaseJobEntry, JobRuntimeStatistics
from ja.server.database.types.work_machine import WorkMachine
from ja.server.database.sql.database import SQLDatabase
from ja.server.database.database import ServerDatabase

Postgresql = testing.postgresql.PostgresqlFactory(cache_initialized_db=True)


class MockDatabase(SQLDatabase):

    def __init__(self) -> None:
        super().__init__()
        self.postgresql = Postgresql()
        # connect to PostgreSQL
        self.engine = create_engine(self.postgresql.url())
        self.scoped = scoped_session(sessionmaker(self.engine))
        SQLDatabase._metadata.create_all(self.engine)
        self.session = self.scoped()

    def __del__(self) -> None:
        self.scoped.remove()  # type: ignore

    def find_job_by_id(self, job_id: str) -> Optional[DatabaseJobEntry]:
        job: Optional[Job] = self.session.query(Job).filter(Job.uid == job_id).first()
        jobs_entry: Optional[DatabaseJobEntry] = self.session.query(DatabaseJobEntry). \
            join(Job, DatabaseJobEntry.job == job).first()
        if jobs_entry is not None:
            if jobs_entry.job.status is JobStatus.RUNNING:
                jobs_entry.statistics.running_time = (datetime.now() - jobs_entry.statistics.time_started).seconds \
                    - jobs_entry.statistics.paused_time
            if jobs_entry.job.status is JobStatus.PAUSED:
                jobs_entry.statistics.paused_time = (datetime.now() - jobs_entry.statistics.time_started).seconds \
                    - jobs_entry.statistics.running_time
            self.session.commit()
        return jobs_entry

    def update_job(self, job: Job) -> None:
        old_job_entry: Optional[DatabaseJobEntry] = self.find_job_by_id(job.uid)
        old_job = old_job_entry.job if old_job_entry else None
        if old_job is None:
            job_entry = DatabaseJobEntry(job=deepcopy(job),
                                         stats=JobRuntimeStatistics(datetime.now(), None,
                                                                    0, 0),
                                         machine=None)
            self.session.add(job_entry)
        else:
            job_entry = self.find_job_by_id(old_job.uid)
            if old_job.status == JobStatus.PAUSED and job.status != JobStatus.PAUSED:
                job_entry.statistics.paused_time = \
                    (datetime.now() - job_entry.statistics.time_started).seconds - job_entry.statistics.running_time
            # first start
            elif old_job.status != JobStatus.RUNNING and job.status == JobStatus.RUNNING:
                job_entry.statistics.time_started = datetime.now()
            elif old_job.status == JobStatus.RUNNING and job.status != JobStatus.RUNNING:
                job_entry.statistics.running_time = \
                    (datetime.now() - job_entry.statistics.time_started).seconds - job_entry.statistics.paused_time
            if old_job != job:
                self.session.delete(old_job)
                self.session.flush()
                job_entry.job = deepcopy(job)
        self.session.commit()

    def get_jobs_on_machine(self, machine: WorkMachine) -> Optional[List[Job]]:
        jobs: Optional[List[Job]] = self.session.query(Job).join(DatabaseJobEntry). \
            join(WorkMachine, WorkMachine.uid == machine.uid).all()
        return jobs

    def assign_job_machine(self, job: Job, machine: WorkMachine) -> None:
        job_entry = self.find_job_by_id(job.uid)
        job_entry.assigned_machine = machine
        self.session.commit()

    def update_work_machine(self, machine: WorkMachine) -> None:
        work_machine = self.session.query(WorkMachine).filter(WorkMachine.uid == machine.uid).first()
        if work_machine is None:
            self.session.add(machine)
        else:
            self.session.delete(work_machine)
            self.session.flush()
            self.session.add(machine)
        self.session.commit()

    def get_work_machines(self) -> Optional[List[WorkMachine]]:
        work_machines: Optional[List[WorkMachine]] = self.session.query(WorkMachine).all()
        return work_machines

    def get_current_schedule(self) -> Optional[ServerDatabase.JobDistribution]:
        jobs: Optional[List[DatabaseJobEntry]] = self.session.query(DatabaseJobEntry).join(Job) \
            .filter((Job.status == JobStatus.RUNNING) | (Job.status == JobStatus.NEW) | (
                Job.status == JobStatus.PAUSED) | (Job.status == JobStatus.QUEUED)).all()
        return jobs

    def query_jobs(self, since: datetime, user_id: Optional[int], work_machine: Optional[WorkMachine]) \
            -> List[DatabaseJobEntry]:
        jobs_query = self.session.query(DatabaseJobEntry)
        if work_machine is not None:
            jobs_query = jobs_query.join(WorkMachine).filter(WorkMachine.uid == work_machine.uid)
        if user_id != -1:
            jobs_query = jobs_query.join(Job).filter(Job.owner_id == user_id)
        jobs: List[DatabaseJobEntry] = jobs_query.all()
        if since is None:
            return jobs
        return [job for job in jobs if job.statistics.time_added >= since]

    def set_scheduler_callback(self, callback: ServerDatabase.RescheduleCallback) -> None:
        pass

    def set_job_status_callback(self, callback: ServerDatabase.JobStatusCallback) -> None:
        pass
