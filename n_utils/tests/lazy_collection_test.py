from n_utils.lazy_dict import LazyOrderedDict, LazyParam

def test_lazy_collection(mocker):
    my_dict = LazyOrderedDict()
    matcher = lambda key: True
    resolver = lambda key: "baz"
    my_dict.add_lazyparam(matcher, resolver)
    foo = my_dict["bar"]
    my_dict["zab"] = "zoo"
    assert foo == "baz"
    assert my_dict["zab"] == "zoo"