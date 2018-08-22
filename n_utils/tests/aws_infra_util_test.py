from n_utils.aws_infra_util import yaml_to_dict

def test_merge_import(mocker):
    result = yaml_to_dict('n_utils/tests/templates/test.yaml')
    assert result['Parameters']['paramTest']['Default'] == 'test2'
    assert result['Parameters']['paramTest3']['Default'] == 'test2'
    assert result['Parameters']['paramTest4']['Default'] == 'test2'
    assert result['Parameters']['paramTestA']['Default'] == 'test2'
    assert result['Parameters']['paramTest5']['Default'] == 'TEST2'
    assert result['Parameters']['paramTest6']['Default'] == 'TEST2'
    assert result['Parameters']['paramTest7']['Default'] == 'tEST2'
    assert result['Parameters']['paramTest2']['Default'] == 'TEST2'
    assert result['Parameters']['paramTest8']['Default'] == 'aaabbbST2'
    assert result['Parameters']['paramTest9']['Default'] == 'aabbbST2'
    assert result['Parameters']['paramTest10']['Default'] == 'b/c/d/e/f'
    assert result['Parameters']['paramTest11']['Default'] == 'f'
    assert result['Parameters']['paramTest12']['Default'] == 'a/b/c/d/e'
    assert result['Parameters']['paramTest13']['Default'] == 'a'
    assert result['Parameters']['paramTest14']['Default'] == 'a/b/c/d/e/f'
    assert result['Parameters']['paramTest15']['Default'] == 'b/c/'
    assert result['Parameters']['paramTest16']['Default'] == 'foo'
    assert result['Parameters']['paramTest17']['Default'] == 'foo'

def test_just_import(mocker):
    result = yaml_to_dict('n_utils/tests/templates/test-param-import.yaml')
    assert result['Parameters']['paramTest']['Default'] == 'test2'
    assert result['Parameters']['paramTest3']['Default'] == 'test2'
    assert result['Parameters']['paramTest4']['Default'] == 'test2'
    assert result['Parameters']['paramTestA']['Default'] == 'test2'
    assert result['Parameters']['paramTest5']['Default'] == 'TEST2'
    assert result['Parameters']['paramTest6']['Default'] == 'TEST2'
    assert result['Parameters']['paramTest7']['Default'] == 'tEST2'


