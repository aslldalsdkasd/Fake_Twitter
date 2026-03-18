

def search_user_id(user_id: str ) -> int:
    list_id = user_id.split('-')
    id = int(list_id[1])
    return id
