import pytest
import json

BASE_MODULE_NAME = 'n_utils'

from n_utils.aws_infra_util import yaml_to_dict

def test_import(mocker):
    result = yaml_to_dict('n_utils/tests/templates/test.yaml')
    print(json.dumps(result))
    assert result['Parameters']['paramTest2']['Default'] == 'test2'