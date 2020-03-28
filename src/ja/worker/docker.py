from io import BytesIO
from threading import Thread
from typing import Dict
import yaml
import docker  # type: ignore
from docker.models.containers import Container  # type: ignore
from docker.types import Mount  # type: ignore

from ja.common.job import Job
from ja.worker.proxy.proxy import IWorkerServerProxy

import logging
logger = logging.getLogger(__name__)


class DockerInterface:
    def __init__(self, server_proxy: IWorkerServerProxy, worker_uid: str):
        self._server_proxy = server_proxy
        self._worker_uid = worker_uid
        self._client = docker.from_env()
        self._jobs_by_container_id: Dict[str, Job] = dict()
        self._containers_by_job_uid: Dict[str, Container] = dict()
        self._listen_thread = Thread(target=self._listen)
        self._listen_thread.daemon = True  # Terminate thread when main thread finishes
        self._listen_thread.start()

    def _listen(self) -> None:
        events = self._client.events()
        while True:
            event = yaml.load(events.next().decode(), Loader=yaml.SafeLoader)
            actor = event["Actor"]
            attributes = actor["Attributes"]
            if event["Type"] == "container" and event["Action"] == "die":
                job = self._jobs_by_container_id.pop(event["id"], None)
                if job is not None:
                    self._containers_by_job_uid.pop(job.uid)
                    if attributes["exitCode"] == "0":
                        self._server_proxy.notify_job_finished(job.uid)
                    else:
                        self._server_proxy.notify_job_crashed(job.uid)

    @property
    def worker_uid(self) -> str:
        return self._worker_uid

    def add_job(self, job: Job) -> None:
        if job.uid in self._containers_by_job_uid:
            raise ValueError("Job with UID %s already exists." % job.uid)
        logger.info("adding job: %s" % job.uid)
        logger.debug(str(job))
        image, build_log = self._client.images.build(fileobj=BytesIO(job.docker_context.dockerfile_source.encode()))
        mounts = [Mount(target=mount_point.mount_path, source=mount_point.source_path, type="bind")
                  for mount_point in job.docker_context.mount_points]
        container = self._client.containers.run(
            image=image, detach=True, mounts=mounts, cpu_count=job.docker_constraints.cpu_threads,
            mem_limit="%sm" % job.docker_constraints.memory, user=job.owner_id
        )
        self._jobs_by_container_id[container.id] = job
        logger.debug("container id: " + container.id)
        self._containers_by_job_uid[job.uid] = container

    def cancel_job(self, uid: str) -> None:
        logger.info("cancelling job: %s" % uid)
        container = self._containers_by_job_uid.pop(uid)
        self._jobs_by_container_id.pop(container.id)
        logger.debug("container id: " + container.id)
        container.kill()

    def pause_job(self, uid: str) -> None:
        logger.info("pausing job: %s" % uid)
        container = self._containers_by_job_uid[uid]
        logger.debug("container id: " + container.id)
        container.pause()

    def resume_job(self, uid: str) -> None:
        logger.info("resuming job: %s" % uid)
        container = self._containers_by_job_uid[uid]
        logger.debug("container id: " + container.id)
        container.unpause()

    def has_running_jobs(self) -> bool:
        return len(self._jobs_by_container_id) > 0
