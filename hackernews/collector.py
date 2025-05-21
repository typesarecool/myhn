from enum import Enum
from functools import cache
from http.client import HTTPException
import json
import logging
import time
from typing import List

from pydantic.json import pydantic_encoder
from pydantic import BaseModel, TypeAdapter
from pydantic_core import from_json
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TypeEnum(Enum):
    JOB = "job"
    STORY = "story"
    COMMENT = "comment"
    POLL = "poll"
    POLLOPT = "pollopt"


class Item(BaseModel):
    id: int
    deleted: bool | None = None
    type: TypeEnum | None = None
    by: str | None = None
    time: int | None = None
    text: str | None = None
    dead: bool | None = None
    parent: int | None = None
    poll: int | None = None
    kids: List[int] | None = None
    url: str | None = None
    score: int | None = None
    title: str | None = None
    parts: List[int] | None = None
    descendants: int | None = None


ITEM_URL = "https://hacker-news.firebaseio.com/v0/item"
MAX_ITEM_URL = "https://hacker-news.firebaseio.com/v0/maxitem.json"


def get_max_item() -> int:
    r = requests.get(MAX_ITEM_URL)

    if r.status_code != 200:
        raise HTTPException

    if type(r.json()) != int:
        raise ValueError(f"{MAX_ITEM_URL} didn't return an int")

    return r.json()


@cache
def get_item(item_id: int, rate_limit = 0.00) -> Item:

    time.sleep(rate_limit)

    url = f"{ITEM_URL}/{item_id}.json"
    logger.info(f"Trying to get {url}")

    r = requests.get(url)

    if r.status_code != 200:
        raise HTTPException

    item = Item.model_validate(from_json(r.text, allow_partial=True))

    return item


def save(items: List[Item]):
    with open("data.json", "w") as f:
        data = json.dumps(items, default=pydantic_encoder)
        f.write(data)


def load(file_path: str) -> List[Item]:
    with open(file_path) as f:
        json_data = json.loads(f)
        items = TypeAdapter(List[Item]).validate_json(json_data)
        return items


if __name__ == "__main__":
    items: List[Item] = []

    max_item_id = get_max_item()

    for i in range(5):
        item = get_item(max_item_id - i, rate_limit=0.1)
        items.append(item)

    save(items)
