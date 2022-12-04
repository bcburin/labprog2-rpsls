from pydantic import BaseModel


FORMAT = 'utf-8'


def encode(schema: BaseModel) -> bytes:
    return (schema.json() + '\n').encode(FORMAT)
