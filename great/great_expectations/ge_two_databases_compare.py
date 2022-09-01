from ruamel import yaml

import great_expectations as ge
from great_expectations.core.batch import BatchRequest
from great_expectations.profile.user_configurable_profiler import (
    UserConfigurableProfiler,
)

context = ge.data_context.DataContext(
    context_root_dir='/great_expectations'
)

t1_batch_request = BatchRequest(
    datasource_name="postgres_airflow",
    data_connector_name="default_inferred_data_connector_name",
    data_asset_name="public.countries_python",
)

t2_batch_request = BatchRequest(
    datasource_name="postgres_airflow",
    data_connector_name="default_inferred_data_connector_name",
    data_asset_name="public.countries_python_mv",
)

validator = context.get_validator(batch_request=t1_batch_request)
profiler = UserConfigurableProfiler(
    profile_dataset=validator,
    excluded_expectations=[
        "expect_column_quantile_values_to_be_between",
        "expect_column_mean_to_be_between",
        "expect_column_proportion_of_unique_values_to_be_between",
    ],
)

expectation_suite_name = "compare_two_tables"

# Comment below code to not generate expectations from dataset_1 every time
# suite = profiler.build_suite()
# context.save_expectation_suite(
#     expectation_suite=suite, expectation_suite_name=expectation_suite_name
# )

my_checkpoint_name = "comparison_checkpoint"

yaml_config = f"""
name: {my_checkpoint_name}
config_version: 1.0
class_name: SimpleCheckpoint
run_name_template: "%Y%m%d-%H%M%S-my-run-name-template"
expectation_suite_name: {expectation_suite_name}
"""

context.add_checkpoint(**yaml.load(yaml_config))

results = context.run_checkpoint(
    checkpoint_name=my_checkpoint_name, batch_request=t2_batch_request
)
