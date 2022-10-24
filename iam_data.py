import datetime
from typing import Literal
import numpy as np

import pandas as pd
from rich.console import Console
from rich.table import Table


def get_aws_docs(service: str) -> list[pd.DataFrame]:
    """
    read the iam actions docs
    """
    return pd.read_html(
        f"https://docs.aws.amazon.com/service-authorization/latest/reference/list_{service}.html"
    )


def convert_df_to_list_of_dict(
    dataframes, aws_doc_type: Literal["actions", "resources", "conditions"]
):
    """
    retrieve the specific html table element of interest
    """
    aws_doc_type_list_keys = {
        "actions": {"index": 0, "column": "Actions"},
        "resources": {"index": 1, "column": "Resource Types"},
        "conditions": {"index": 2, "column": "Conditions"},
    }
    index = aws_doc_type_list_keys[aws_doc_type]["index"]
    column = aws_doc_type_list_keys[aws_doc_type]["column"]
    return (
        dataframes[index].sort_values(by=column).replace(np.nan, "").to_dict("records")
    )


def create_table(iam_info: list[dict]) -> Table:
    """
    create a rich table
    """
    table = Table(
        title=f"Last updated: {datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')}",
        show_lines=True,
        safe_box=False,
        min_width=180
    )
    _ = [table.add_column(col) for col in iam_info[0]]
    for row in iam_info:
        table.add_row(*tuple(row.values()))
    return table


def write_data_to_files(
    data: Table,
    service_name: str,
    aws_doc_type: Literal["actions", "resources", "conditions"],
) -> None:
    """
    write an easier to read ascii table
    """
    with open(f"data/{aws_doc_type}/{service_name}.txt", "w") as f:
        console = Console(file=f)
        console.print(data)


def main():

    service_mapping = {
        "athena": "amazonathena",
        "ecr": "amazonelasticcontainerregistry",
        "emr": "amazonelasticmapreduce",
        "emr-on-eks": "amazonemroneksemrcontainers",
        "emr-serverless": "amazonemrserverless",
        "glue": "awsglue",
        "glue-databrew": "awsgluedatabrew",
        "iam": "identityandaccessmanagement",
        "kms": "awskeymanagementservice",
        "lakeformation": "awslakeformation",
        "lambda": "awslambda",
        "sagemaker": "amazonsagemaker",
        "s3": "amazons3",
        "sts": "awssecuritytokenservice",
    }

    for service in service_mapping:
        list_of_dataframes = get_aws_docs(service=service_mapping[service])
        for item in (
            "actions",
            # "resources",
        ):
            list_of_dict = convert_df_to_list_of_dict(
                dataframes=list_of_dataframes, aws_doc_type="actions"
            )
            table = create_table(iam_info=list_of_dict)
            write_data_to_files(data=table, service_name=service, aws_doc_type=item)


if __name__ == "__main__":
    main()
