from datetime import datetime

import pytest

from n_utils.cloudfront_utils import distributions, distribution_comments

DISTRIBUTION = {
    'DistributionList': {
        'Marker': 'string',
        'NextMarker': 'string',
        'MaxItems': 123,
        'IsTruncated': False,
        'Quantity': 123,
        'Items': [
            {
                'Id': 'id1',
                'ARN': 'arn1',
                'Status': 'status1',
                'LastModifiedTime': datetime(2015, 1, 1),
                'DomainName': 'string',
                'Comment': 'comment1',
            },
            {
                'Id': 'id2',
                'ARN': 'arn2',
                'Status': 'status2',
                'LastModifiedTime': datetime(2016, 1, 1),
                'DomainName': 'string',
                'Comment': 'comment2',
            }
        ]
    }
}


@pytest.fixture(scope="function")
def paginator(mocker):
    client = mocker.MagicMock()
    paginator = mocker.MagicMock()
    client.get_paginator.return_value = paginator
    boto3 = mocker.patch('n_utils.cloudfront_utils.boto3')
    boto3.client.return_value = client
    return paginator


def test_distributions(mocker, paginator):
    paginator.paginate.return_value = [DISTRIBUTION]
    assert list(distributions()) == ['id1', 'id2']


def test_distribution_comments(mocker, paginator):
    paginator.paginate.return_value = [DISTRIBUTION]
    assert list(distribution_comments()) == ['comment1', 'comment2']
