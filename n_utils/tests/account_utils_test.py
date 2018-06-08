from n_utils.account_utils import find_role_arn


def test_find_role_arn(mocker):
    boto3 = mocker.patch('n_utils.account_utils.boto3')

    find_role_arn('foo')

    boto3.client.assert_called_with('cloudformation')
