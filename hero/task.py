import uuid
import json

from typing import Optional
from dataclasses import dataclass, field
from decimal import Decimal

READY = "ready"
CLAIMED = "claimed"
COMPLETE = "complete"
FAILED = "failed"


def _convert_to_decimal_json(data):
    return json.loads(json.dumps(data), parse_float=Decimal)


def get_new_uuid() -> str:
    return str(uuid.uuid4())


@dataclass
class Task:
    project: str
    queue_name: str
    queue_url: str
    inputs: dict
    # defaults
    task_id: Optional[str] = field(default_factory=get_new_uuid)
    status: str = READY
    created_by: str = None

    insert_time: str = None
    claimed_time: str = None
    complete_time: str = None

    insert_resource_name: str = None
    claimed_resource_name: str = None
    complete_resource_name: str = None

    attempts: int = 0
    inputs_s3: str = None
    results: dict = field(default_factory=dict)
    results_s3: str = None

    @property
    def data(self):
        tmp = self.__dict__
        # need these to match dynamo table
        tmp["id"] = self.task_id
        tmp["queue"] = self.queue_name
        return tmp
