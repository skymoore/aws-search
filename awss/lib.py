from logging import info

def get_regions(session, service):
    info("getting regions...")
    return session.get_available_regions(service)
