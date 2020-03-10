from copy import deepcopy
from typing import List, Optional, Callable
from datetime import datetime
from sqlalchemy import create_engine

from ja.common.work_machine import ResourceAllocation
from ja.common.docker_context import DockerContext, DockerConstraints, MountPoint
from ja.common.job import Job, JobStatus, JobSchedulingConstraints, JobPriority
from ja.server.database.types.job_entry import DatabaseJobEntry, JobRuntimeStatistics
from ja.server.database.types.work_machine import WorkMachine, WorkMachineResources, WorkMachineConnectionDetails, \
    WorkMachineState
from ja.server.database.database import ServerDatabase
from sqlalchemy import Table, Column, Integer, String, MetaData, DateTime, Enum, ForeignKey, Boolean, ARRAY
from sqlalchemy.orm import mapper, synonym, relationship, sessionmaker, scoped_session, joinedload


class SQLDatabase(ServerDatabase):
    """!
    SQL Database is the actual implementation of the database used by default in JobAdder.
    """
    _metadata: MetaData = None

    def __init__(self, host: str = None, user: str = None, password: str = None):
        """!
        Create the SQLDatabase object and connect to the given database.

        @param host The host of the database to connect to.
        @param user The username to use for the connection.
        @param password The password to use for the connection.
        """
        self.scheduler_callback: Callable[["ServerDatabase"], None] = lambda *args: None
        self.status_callback: Callable[["Job"], None] = lambda *args: None
        self.in_scheduler_callback: bool = False
        if SQLDatabase._metadata:
            return

        metadata = MetaData()
        SQLDatabase._metadata = metadata
        resource_allocation = Table("resource_allocation", metadata,
                                    Column("id", Integer, primary_key=True),
                                    Column("_cpu_threads", Integer),
                                    Column("_memory", Integer),
                                    Column("_swap", Integer))
        mapper(ResourceAllocation, resource_allocation)

        work_machine_resources = Table("work_machine_resources", metadata,
                                       Column("id", Integer, primary_key=True),
                                       Column("total_resources_id", Integer, ForeignKey("resource_allocation.id")),
                                       Column("free_resources_id", Integer, ForeignKey("resource_allocation.id")))
        mapper(WorkMachineResources, work_machine_resources, properties={
            "_total_resources": relationship(ResourceAllocation,
                                             foreign_keys=work_machine_resources.c.total_resources_id,
                                             uselist=False),
            "_free_resources": relationship(ResourceAllocation, foreign_keys=work_machine_resources.c.free_resources_id,
                                            uselist=False),
        })

        work_machine_connection = Table("work_machine_connection", metadata,
                                        Column("id", Integer, primary_key=True))
        mapper(WorkMachineConnectionDetails, work_machine_connection)

        work_machine = Table("work_machine", metadata,
                             Column("id", Integer, primary_key=True),
                             Column("_uid", String, unique=True),
                             Column("_state", Enum(WorkMachineState)),
                             Column("resources_id", Integer, ForeignKey("work_machine_resources.id")),
                             Column("connection_id", Integer, ForeignKey("work_machine_connection.id")))
        mapper(WorkMachine, work_machine, properties={
            "_resources": relationship(WorkMachineResources, uselist=False),
            "_connection": relationship(WorkMachineConnectionDetails, uselist=False),
            "uid": synonym("_uid", descriptor=WorkMachine.uid)
        })

        mount_point = Table("mount_point", metadata,
                            Column("id", Integer, primary_key=True),
                            Column("_source_path", String),
                            Column("_mount_path", String),
                            Column("docker_context_id", Integer, ForeignKey("docker_context.id")))
        mapper(MountPoint, mount_point)

        docker_context = Table("docker_context", metadata,
                               Column("id", Integer, primary_key=True),
                               Column("_dockerfile_source", String))
        mapper(DockerContext, docker_context, properties={
            "_mount_points": relationship(MountPoint, uselist=True),
            "job_mount_points": synonym("_mount_points", descriptor=DockerContext.mount_points)
        })

        docker_constraints = Table("docker_constraints", metadata,
                                   Column("id", Integer, primary_key=True),
                                   Column("_cpu_threads", Integer),
                                   Column("_memory", Integer))
        mapper(DockerConstraints, docker_constraints)

        job_constrains = Table("job_constrains", metadata,
                               Column("id", Integer, primary_key=True),
                               Column("_priority", Enum(JobPriority)),
                               Column("_is_preemptible", Boolean),
                               Column("_special_resources", ARRAY(String)))

        mapper(JobSchedulingConstraints, job_constrains, properties={
            "job_priority": synonym("_priority", descriptor=JobSchedulingConstraints.priority),
            "job_is_preemptible": synonym("_is_preemptible",
                                          descriptor=JobSchedulingConstraints.is_preemptible),
            "job_special_resources": synonym("_special_resources",
                                             descriptor=JobSchedulingConstraints.special_resources),
        })
        job = Table("job", metadata,
                    Column("id", Integer, primary_key=True),
                    Column("_status", Enum(JobStatus)),
                    Column("_owner_id", Integer),
                    Column("_email", String),
                    Column("_label", String),
                    Column("_uid", String, unique=True),
                    Column("scheduling_constraints_id", Integer, ForeignKey("job_constrains.id")),
                    Column("docker_context_id", Integer, ForeignKey("docker_context.id")),
                    Column("docker_constraints_id", Integer, ForeignKey("docker_constraints.id")),
                    Column("job_entry", Integer, ForeignKey("database_job.id")))

        mapper(Job, job, properties={
            "_scheduling_constraints": relationship(JobSchedulingConstraints, uselist=False),
            "_docker_context": relationship(DockerContext, uselist=False),
            "_docker_constraints": relationship(DockerConstraints, uselist=False),
            "uid": synonym("_uid", descriptor=Job.uid),
            "status": synonym("_status", descriptor=Job.status),
            "owner_id": synonym("_owner_id", descriptor=Job.owner_id),
            "scheduling_constraints": synonym("_scheduling_constraints",
                                              descriptor=Job.scheduling_constraints),
            "docker_context": synonym("_docker_context", descriptor=Job.docker_context)
        })

        job_statistics = Table('job_stats', metadata,
                               Column('id', Integer, primary_key=True),
                               Column('_added', DateTime),
                               Column('_started', DateTime),
                               Column("_running_time", Integer),
                               Column("_paused_time", Integer))
        mapper(JobRuntimeStatistics, job_statistics, properties={
            "added": synonym("_added", descriptor=JobRuntimeStatistics.time_added),
            "started": synonym("_started", descriptor=JobRuntimeStatistics.time_started),
            "running_time": synonym("_running_time", descriptor=JobRuntimeStatistics.running_time),
            "paused_time": synonym("_paused_time", descriptor=JobRuntimeStatistics.paused_time)
        })

        database_job = Table("database_job", metadata,
                             Column("id", Integer, primary_key=True),
                             Column("stats_id", Integer, ForeignKey("job_stats.id")),
                             Column("machine_id", Integer, ForeignKey("work_machine.id")))
        mapper(DatabaseJobEntry, database_job, properties={
            "_job": relationship(Job, uselist=False),
            "_statistics": relationship(JobRuntimeStatistics, uselist=False),
            "_machine": relationship(WorkMachine, uselist=False),
            "job": synonym("_job", descriptor=DatabaseJobEntry.job),
            "statistics": synonym("_statistics", descriptor=DatabaseJobEntry.statistics),
            "machine": synonym("_machine", descriptor=DatabaseJobEntry.assigned_machine)
        })
        if user is not None and password is not None and host is not None:
            # example: "postgresql://pesho:pesho@127.0.0.1:5432/jobadd"
            _conn: str = "postgresql://" + user + ":" + password + "@" + host + "/jobadder"
            self.engine = create_engine(_conn)
            self.scoped = scoped_session(sessionmaker(self.engine))
            SQLDatabase._metadata.create_all(self.engine)

    def __del__(self) -> None:
        self.scoped.remove()  # type: ignore

    def find_job_by_id(self, job_id: str) -> Optional[DatabaseJobEntry]:
        session = self.scoped()
        job: Optional[Job] = session.query(Job).filter(Job.uid == job_id).options(joinedload("*")).first()
        jobs_entry: Optional[DatabaseJobEntry] = session.query(DatabaseJobEntry). \
            join(Job, DatabaseJobEntry.job == job).first()
        if jobs_entry is not None:
            if jobs_entry.job.status is JobStatus.RUNNING:
                jobs_entry.statistics.running_time \
                    = (datetime.now() - jobs_entry.statistics.time_started).seconds - jobs_entry.statistics.paused_time
            if jobs_entry.job.status is JobStatus.PAUSED:
                jobs_entry.statistics.paused_time \
                    = (datetime.now() - jobs_entry.statistics.time_started).seconds - jobs_entry.statistics.running_time
            session.commit()
        return jobs_entry

    def update_job(self, job: Job) -> None:
        session = self.scoped()
        old_job_entry: Optional[DatabaseJobEntry] = self.find_job_by_id(job.uid)
        old_job = old_job_entry.job if old_job_entry else None
        if old_job is None:
            job_entry = DatabaseJobEntry(job=deepcopy(job),
                                         stats=JobRuntimeStatistics(datetime.now(), None,
                                                                    0, 0),
                                         machine=None)
            session.add(job_entry)
        else:
            if old_job.status == JobStatus.PAUSED and job.status != JobStatus.PAUSED:
                old_job_entry.statistics.paused_time = \
                    (datetime.now() - old_job_entry.statistics.time_started).seconds \
                    - old_job_entry.statistics.running_time
            # first start
            elif old_job.status != JobStatus.RUNNING and job.status == JobStatus.RUNNING:
                old_job_entry.statistics.time_started = datetime.now()
            elif old_job.status == JobStatus.RUNNING and job.status != JobStatus.RUNNING:
                old_job_entry.statistics.running_time = \
                    (datetime.now() - old_job_entry.statistics.time_started).seconds \
                    - old_job_entry.statistics.paused_time
            if old_job != job:
                if job.status != old_job.status:
                    old_job_entry.job.status = job.status
                    self.status_callback(job)
        session.commit()
        self._call_scheduler()

    def get_jobs_on_machine(self, machine: WorkMachine) -> Optional[List[Job]]:
        session = self.scoped()
        jobs: Optional[List[Job]] = session.query(Job).join(DatabaseJobEntry). \
            join(WorkMachine, WorkMachine.uid == machine.uid).options(joinedload("*")).all()
        return jobs

    def assign_job_machine(self, job: Job, machine: WorkMachine) -> None:
        session = self.scoped()
        job_entry = self.find_job_by_id(job.uid)
        job_entry.assigned_machine = machine
        session.commit()
        self._call_scheduler()

    def update_work_machine(self, machine: WorkMachine) -> None:
        session = self.scoped()
        work_machine: WorkMachine = session.query(WorkMachine).filter(WorkMachine.uid == machine.uid).first()
        if work_machine is None:
            session.add(machine)
        else:
            work_machine.state = machine.state
            work_machine.connection_details = machine.connection_details
            work_machine.resources = machine.resources
        session.commit()
        self._call_scheduler()

    def get_work_machines(self) -> Optional[List[WorkMachine]]:
        session = self.scoped()
        work_machines: Optional[List[WorkMachine]] = session.query(WorkMachine).options(joinedload("*")).all()
        return work_machines

    def get_current_schedule(self) -> Optional[ServerDatabase.JobDistribution]:
        session = self.scoped()
        jobs: Optional[List[DatabaseJobEntry]] = session.query(DatabaseJobEntry).join(Job) \
            .filter((Job.status == JobStatus.RUNNING) | (Job.status == JobStatus.NEW) | (
                Job.status == JobStatus.PAUSED) | (Job.status == JobStatus.QUEUED)).all()
        return jobs

    def query_jobs(self, since: Optional[datetime], user_id: Optional[int], work_machine: Optional[WorkMachine]) \
            -> List[DatabaseJobEntry]:
        session = self.scoped()
        jobs_query = session.query(DatabaseJobEntry)
        if work_machine is not None:
            jobs_query = jobs_query.join(WorkMachine).filter(WorkMachine.uid == work_machine.uid)
        if user_id != -1:
            jobs_query = jobs_query.join(Job).filter(Job.owner_id == user_id)
        jobs: List[DatabaseJobEntry] = jobs_query.all()
        if since is None:
            return jobs
        return [job for job in jobs if job.statistics.time_added >= since]

    def _call_scheduler(self) -> None:
        if not self.in_scheduler_callback:
            self.in_scheduler_callback = True
            self.scheduler_callback(self)
            self.in_scheduler_callback = False

    def set_scheduler_callback(self, callback: ServerDatabase.RescheduleCallback) -> None:
        self.scheduler_callback = callback

    def set_job_status_callback(self, callback: ServerDatabase.JobStatusCallback) -> None:
        self.status_callback = callback
