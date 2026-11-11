"""Automated-test results. These models live in the separate "reports" database.

Test Case: id, test_name, module, test_description, expected_result
Test Execution Report: id, test_case_id, execution_date, actual_result, status, execution_time, screenshot_path
Test Summary Report: id, execution_date, total_tests, passed_tests, failed_tests, skipped_tests,
                     total_execution_time, report_path
"""

from django.db import models
from django.utils import timezone


class TestCase(models.Model):
    __test__ = False  # a model, not a pytest test class
    id = models.CharField(primary_key=True, max_length=20)  # e.g. "TC-ADM-01"
    test_name = models.CharField(max_length=120)
    module = models.CharField(max_length=40)
    test_description = models.TextField()
    expected_result = models.TextField()

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:
        return f"{self.id} {self.test_name}"


class TestSummary(models.Model):
    __test__ = False  # a model, not a pytest test class
    execution_date = models.DateTimeField(default=timezone.now)
    total_tests = models.PositiveIntegerField(default=0)
    passed_tests = models.PositiveIntegerField(default=0)
    failed_tests = models.PositiveIntegerField(default=0)
    skipped_tests = models.PositiveIntegerField(default=0)
    total_execution_time = models.FloatField(default=0.0, help_text="Seconds")
    report_path = models.CharField(max_length=300, blank=True)
    command = models.CharField(max_length=300, blank=True, help_text="How the run was started")
    browser_mode = models.CharField(max_length=10, blank=True, help_text="headless or headed")

    class Meta:
        ordering = ["-execution_date"]
        verbose_name_plural = "test summaries"

    def __str__(self) -> str:
        return f"Run {self.pk} {self.execution_date:%Y-%m-%d %H:%M}"

    @property
    def pass_rate(self) -> int:
        executed = self.total_tests - self.skipped_tests
        return round(self.passed_tests / executed * 100) if executed else 0


class TestExecution(models.Model):
    __test__ = False  # a model, not a pytest test class
    class Status(models.TextChoices):
        PASSED = "Passed", "Passed"
        FAILED = "Failed", "Failed"
        SKIPPED = "Skipped", "Skipped"

    summary = models.ForeignKey(TestSummary, on_delete=models.CASCADE, related_name="executions")
    test_case = models.ForeignKey(TestCase, on_delete=models.SET_NULL, null=True, blank=True, related_name="executions")
    node_id = models.CharField(max_length=300, help_text="pytest node id")
    execution_date = models.DateTimeField(default=timezone.now)
    actual_result = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=Status.choices)
    execution_time = models.FloatField(default=0.0, help_text="Seconds")
    screenshot_path = models.CharField(max_length=300, blank=True)

    class Meta:
        ordering = ["test_case_id", "node_id"]

    def __str__(self) -> str:
        return f"{self.test_case_id or self.node_id} {self.status}"
