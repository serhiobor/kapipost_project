from datetime import datetime


def year(request) -> dict[str, int]:
    '''Add actual year'''
    return {
        'year': datetime.now().year
    }
