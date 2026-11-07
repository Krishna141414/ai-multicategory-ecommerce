"""Send the test-report models to their own SQLite file ("reports").

Shop data stays in the "default" database; automated test results live in
"reports" so a test run can never modify shop data (brief rule 7).
"""

REPORTS_APP = "testreports"
REPORTS_DB = "reports"


class ReportsRouter:
    """Route the testreports app to the reports DB and everything else to default."""

    def db_for_read(self, model, **hints):
        return REPORTS_DB if model._meta.app_label == REPORTS_APP else None

    def db_for_write(self, model, **hints):
        return REPORTS_DB if model._meta.app_label == REPORTS_APP else None

    def allow_relation(self, obj1, obj2, **hints):
        in_reports = {obj1._meta.app_label == REPORTS_APP, obj2._meta.app_label == REPORTS_APP}
        return len(in_reports) == 1  # only relations inside one database

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == REPORTS_APP:
            return db == REPORTS_DB
        return db == "default"
