import pytest

BASE_MODULE_NAME = 'n_utils'


def get_test_target_module(test_module):
    if test_module.endswith('_test'):
        return test_module[:-5]
    if test_module.startswith('test_'):
        return test_module[5:]
    return test_module


@pytest.fixture(scope='function')
def paginator(mocker, request):
    target = '{}.{}.boto3'.format(BASE_MODULE_NAME, get_test_target_module(request.module.__name__))
    print('Mocking {}'.format(target))
    client = mocker.MagicMock()
    paginator = mocker.MagicMock()
    client.get_paginator.return_value = paginator
    boto3 = mocker.patch(target)
    boto3.client.return_value = client
    return paginator
