from math import ceil


def get_pagination(page: int, page_size: int, total_records: int):
    offset = (page - 1) * page_size
    total_pages = ceil(total_records / page_size) if total_records else 1

    return {
        "offset": offset,
        "total_records": total_records,
        "total_pages": total_pages,
        "page": page,
        "page_size": page_size
    }