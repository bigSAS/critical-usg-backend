def must_exist_by_pk(repository, pk: int):
    o = repository.get(entity_id=pk, ignore_not_found=True)
    if not o: raise ValueError(f'{repository.__class__}.get(entity_id={pk}] not exists')
