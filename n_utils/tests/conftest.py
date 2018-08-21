import pytest

BASE_MODULE_NAME = 'n_utils'


def get_test_target_module(test_module):
    if test_module.endswith('_test'):
        return test_module[:-5]
    if test_module.startswith('test_'):
        return test_module[5:]
    return test_module


@pytest.fixture(scope='function')
def boto3_client(mocker, request):
    target = '{}.{}.boto3'.format(BASE_MODULE_NAME, get_test_target_module(request.module.__name__))
    if load_class(target):
        print('Mocking {}'.format(target))
        client = mocker.MagicMock()
        boto3 = mocker.patch(target)
        boto3.client.return_value = client
        return client


@pytest.fixture(scope='function')
def paginator(mocker, boto3_client):
    paginator = mocker.MagicMock()
    boto3_client.get_paginator.return_value = paginator
    return paginator

def load_class(name):
    components = name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod