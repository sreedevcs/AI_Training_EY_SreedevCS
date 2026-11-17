
from app.repositories import dashboard_repository


def get_dashboard_summary(conn):
    return dashboard_repository.get_dashboard_summary(conn)
