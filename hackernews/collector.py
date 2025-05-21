from enum import Enum
from http.client import HTTPException
from typing import List

from pydantic_core import from_json
import requests
from sqlmodel import Field, SQLModel, Session, create_engine, select


class TypeEnum(Enum):
    JOB = "job"
    STORY = "story"
    COMMENT = "comment"
    POLL = "poll"
    POLLOPT = "pollopt"


class Item(SQLModel, table=True):
    id: int = Field(primary_key=True)
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


def get_item(item_id: int) -> Item:
    url = f"{ITEM_URL}/{item_id}.json"
    r = requests.get(url)

    if r.status_code != 200:
        raise HTTPException

    item = Item.model_validate(from_json(r.text, allow_partial=True))

    return item


if __name__ == "__main__":
    engine = create_engine("sqlite:///hn.db")

    with Session(engine) as session:
        max_item_id = get_max_item()
        item = get_item(max_item_id)
        session.add(item)
        session.commit()

        statement = select(Item).where(Item.id == max_item_id)
        item = session.exec(statement).first()
        print(item)
