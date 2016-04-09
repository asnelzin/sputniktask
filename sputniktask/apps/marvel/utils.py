from rest_framework_extensions.key_constructor.bits import (ArgsKeyBit,
                                                            HeadersKeyBit,
                                                            KwargsKeyBit,
                                                            QueryParamsKeyBit,
                                                            UserKeyBit)
from rest_framework_extensions.key_constructor.constructors import \
    DefaultKeyConstructor


class RequestKeyConstructor(DefaultKeyConstructor):
    arguments = ArgsKeyBit()
    key_arguments = KwargsKeyBit()
    query_params = QueryParamsKeyBit()
    user = UserKeyBit()
    headers = HeadersKeyBit()
