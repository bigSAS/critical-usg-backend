def must_exist_by_pk(repository, pk: int):
    return must_exist_by(repository, by='entity_id', value=pk)


def must_exist_by(repository, by: str, value):
    o = repository.get_by(**{by: value}, ignore_not_found=True)
    if not o: raise ValueError(f'{repository.__class__}.get_by({by}={value}] not exists')
