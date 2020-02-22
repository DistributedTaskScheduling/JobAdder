from ja.common.message.server import ServerCommand, ServerResponse
from ja.user.config.base import UserConfig
from ja.common.job import JobPriority, JobStatus
from datetime import datetime
from typing import List, Tuple, Dict, Iterable, cast

from ja.server.database.database import ServerDatabase


class QueryCommand(ServerCommand):
    """
    Command for querying the server.
    """
    datetime_format: str = "%Y-%d-%m %H:%M:%S"

    def __init__(self, config: UserConfig, uid: List[str] = None, label: List[str] = None, owner: List[str] = None,
                 priority: List[JobPriority] = None, status: List[JobStatus] = None, is_preemptible: bool = None,
                 special_resources: List[List[str]] = None, cpu_threads: Tuple[int, int] = None,
                 memory: Tuple[int, int] = None, before: datetime = None, after: datetime = None):
        if cpu_threads is not None and (cpu_threads[0] > cpu_threads[1] or cpu_threads[0] < 1):
            raise ValueError("Invalid range for cpu_threads.")
        if memory is not None and (memory[0] > memory[1] or memory[0] < 1):
            raise ValueError("Invalid range for memory.")
        if after is not None and before is not None:
            if after > before:
                raise ValueError("'after' argument must be a date that comes before the 'before' argument!")
        self._config = config
        self._uid = uid
        self._label = label
        self._owner = owner
        self._priority = priority
        self._status = status
        self._is_preemptible = is_preemptible
        self._special_resources = special_resources
        self._cpu_threads = cpu_threads
        self._memory = memory
        self._before = before
        self._after = after

    @property
    def uid(self) -> List[str]:
        """!
        @return: Job uid(s) to filter query results by.
        """
        return self._uid

    @property
    def label(self) -> List[str]:
        """!
        @return: Job label(s) to filter query results by.
        """
        return self._label

    @property
    def owner(self) -> List[str]:
        """!
        @return: Job owner name(s) to filter query results by.
        """
        return self._owner

    @property
    def priority(self) -> List[JobPriority]:
        """!
        @return: Job priority/priorities to filter query results by.
        """
        return self._priority

    @property
    def status(self) -> List[JobStatus]:
        """!
        @return: Job status(es) to filter query results by.
        """
        return self._status

    @property
    def is_preemptible(self) -> bool:
        """!
        @return: Job.is_preemptible value to filter query results by.
        """
        return self._is_preemptible

    @property
    def special_resources(self) -> List[List[str]]:
        """!
        @return: Special resources to filter query results by.
        """
        return self._special_resources

    @property
    def cpu_threads(self) -> Tuple[int, int]:
        """!
        @return: Lower and upper bound of job CPU thread count to filter query results by.
        """
        return self._cpu_threads

    @property
    def memory(self) -> Tuple[int, int]:
        """!
        @return: Lower and upper bound of job memory allocation in MB to filter query results by.
        """
        return self._memory

    @property
    def before(self) -> datetime:
        """!
        Only return jobs scheduled before this point in time.
        @return: The latest point in time a job of interest was scheduled.
        """
        return self._before

    @property
    def after(self) -> datetime:
        """!
        Only return jobs scheduled after this point in time.
        @return: The earliest point in time a job of interest was scheduled.
        """
        return self._after

    @property
    def config(self) -> UserConfig:
        return self._config

    def __eq__(self, o: object) -> bool:
        if isinstance(o, QueryCommand):
            return self._uid == o.uid \
                and self._label == o.label \
                and self._owner == o.owner \
                and self._priority == o.priority \
                and self._status == o.status \
                and self._is_preemptible == o.is_preemptible \
                and self._special_resources == o.special_resources \
                and self._cpu_threads == o.cpu_threads \
                and self._memory == o.memory \
                and self._before == o.before \
                and self._after == o.after \
                and self._config == o._config
        else:
            return False

    def __dir__(self) -> Iterable[str]:
        return ["_uid", "_label", "_owner", "_priority", "_status", "_is_preemptible",
                "_special_resources", "_cpu_threads", "_memory", "_before", "_after"]

    def to_dict(self) -> Dict[str, object]:
        q_dict: Dict[str, object] = dict()
        q_dict["config"] = self._config.to_dict()
        q_dict["uid"] = self._uid
        q_dict["label"] = self._label
        q_dict["owner"] = self._owner
        q_dict["priority"] = None if self._priority is None else [a.value for a in self._priority]
        q_dict["status"] = None if self._status is None else [a.value for a in self._status]
        q_dict["is_preemptible"] = self._is_preemptible
        q_dict["special_resources"] = self._special_resources
        q_dict["cpu_threads"] = self._cpu_threads
        q_dict["memory"] = self._memory
        q_dict["before"] = None if self._before is None else self._before.strftime(self.datetime_format)
        q_dict["after"] = None if self._after is None else self._after.strftime(self.datetime_format)
        return q_dict

    @classmethod
    def from_dict(cls, property_dict: Dict[str, object]) -> "QueryCommand":
        config = UserConfig.from_dict(
            cls._get_dict_from_dict(property_dict=property_dict, key="config", mandatory=True))
        uid = None
        if "uid" in property_dict:
            uid = cls._get_str_list_from_dict(property_dict=property_dict, key="uid", mandatory=False)
        label = None
        if "label" in property_dict:
            label = cls._get_str_list_from_dict(property_dict=property_dict, key="label", mandatory=False)
        owner = None
        if "owner" in property_dict:
            owner = cls._get_str_list_from_dict(property_dict=property_dict, key="owner", mandatory=False)

        job_priority_list: List[JobPriority] = []
        if "priority" in property_dict:
            prop: object = cls._get_from_dict(property_dict=property_dict, key="priority")
            if not isinstance(prop, list):
                cls._raise_error_wrong_type(
                    key="priority", expected_type="List[JobPriority]",
                    actual_type=prop.__class__.__name__
                )
            object_list = cast(List[object], prop)
            for obj in object_list:
                if not isinstance(obj, int):
                    cls._raise_error_wrong_type(
                        key="priority", expected_type="List[JobPriority]",
                        actual_type="List[object]"
                    )
                job_priority_list.append(JobPriority(obj))

        job_status_list: List[JobStatus] = []
        if "status" in property_dict:
            prop = cls._get_from_dict(property_dict=property_dict, key="status")
            if not isinstance(prop, list):
                cls._raise_error_wrong_type(
                    key="status", expected_type="List[JobStatus]",
                    actual_type=prop.__class__.__name__
                )
            object_list = cast(List[object], prop)
            for obj in object_list:
                if not isinstance(obj, int):
                    cls._raise_error_wrong_type(
                        key="status", expected_type="List[JobStatus]",
                        actual_type="List[object]"
                    )
                job_status_list.append(JobStatus(obj))

        is_preemptible = cls._get_bool_from_dict(property_dict=property_dict, key="is_preemptible", mandatory=False)

        special_resources_list: List[List[str]] = []
        if "special_resources" in property_dict:
            prop = cls._get_from_dict(property_dict=property_dict, key="special_resources")
            if not isinstance(prop, list):
                cls._raise_error_wrong_type(
                    key="special_resources", expected_type="List[List[str]",
                    actual_type=prop.__class__.__name__
                )
            object_list = cast(List[object], prop)
            for obj in object_list:
                if not isinstance(obj, list):
                    cls._raise_error_wrong_type(
                        key="special_resources", expected_type="List[List[str]]",
                        actual_type="List[object]"
                    )
                special_resources_list.append(cast(List[str], obj))

        cpu_threads = None
        if "cpu_threads" in property_dict:
            prop = cls._get_from_dict(property_dict=property_dict, key="cpu_threads", mandatory=False)
            if not isinstance(prop, tuple):
                cls._raise_error_wrong_type(
                    key="cpu_threads", expected_type="Tuple[int, int]",
                    actual_type=prop.__class__.__name__
                )
            cpu_threads = cast(Tuple[int, int], prop)

        memory = None
        if "memory" in property_dict:
            prop = cls._get_from_dict(property_dict=property_dict, key="memory")
            if not isinstance(prop, tuple):
                cls._raise_error_wrong_type(
                    key="memory", expected_type="Tuple[int, int]",
                    actual_type=prop.__class__.__name__
                )
            memory = cast(Tuple[int, int], prop)

        before_string = cls._get_str_from_dict(property_dict=property_dict, key="before", mandatory=False)
        before = None
        if before_string is not None:
            before = datetime.strptime(before_string, cls.datetime_format)

        after_string = cls._get_str_from_dict(property_dict=property_dict, key="after", mandatory=False)
        after = None
        if after_string is not None:
            after = datetime.strptime(after_string, cls.datetime_format)

        cls._assert_all_properties_used(property_dict)
        a = QueryCommand(config, uid, label, owner, job_priority_list, job_status_list, is_preemptible,
                         special_resources_list, cpu_threads, memory, before, after)
        return a

    def execute(self, database: ServerDatabase) -> "ServerResponse":
        pass
