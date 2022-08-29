from typing import Optional

from great_expectations.core.expectation_configuration import \
    ExpectationConfiguration
from great_expectations.execution_engine import SqlAlchemyExecutionEngine

from great_expectations.expectations.expectation import ColumnMapExpectation
from great_expectations.expectations.metrics import (ColumnMapMetricProvider,
                                                     column_condition_partial)


class CustomSqlDataset(ColumnMapMetricProvider):
    condition_metric_name = "expect_column_values_to_start_with_vowel"
    condition_value_keys = ("start",)

    @column_condition_partial(engine=SqlAlchemyExecutionEngine)
    def _sqlalchemy(cls, column, start, **kwargs):
        return column.startswith(start)


class ExpectColumnValuesToStartWithVowel(ColumnMapExpectation):
    """
    Expect the column value to start with substring ("start" :parameter)
    """

    examples = [
        {
            "data": {
                "all_vowels": ["oakland", "oak", "oasis"],
                "not_all_vowels": ["big", "bad", "wolf"],
            },
            "tests": [
                {
                    "title": "basic_positive_test",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {
                        "column": "all_vowels",
                        "start": "oa",
                        "mostly": 0.8
                    },
                    "out": {
                        "success": True,
                    },
                },
                {
                    "title": "basic_negative_test",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {
                        "column": "not_all_vowels",
                        "start": "oa",
                        "mostly": 0.8
                    },
                    "out": {
                        "success": False,
                    },
                },
            ],
            "test_backends": [
                {
                    "backend": "sqlalchemy",
                    "dialects": ["sqlite", "postgresql"],
                },
            ],
        }
    ]

    map_metric = "expect_column_values_to_start_with_vowel"
    success_keys = ("mostly", "start")
    default_kwarg_values = {
        "start": "oa"
    }

    def validate_configuration(
        self, configuration: Optional[ExpectationConfiguration]
    ) -> None:

        super().validate_configuration(configuration)
        if configuration is None:
            configuration = self.configuration


if __name__ == "__main__":
    ExpectColumnValuesToStartWithVowel().print_diagnostic_checklist()
