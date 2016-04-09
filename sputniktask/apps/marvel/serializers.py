from rest_framework import serializers


class OffsetPaginationSerializer(serializers.Serializer):
    limit = serializers.IntegerField(label='limit', min_value=1, max_value=100, required=False)
    offset = serializers.IntegerField(label='offset', min_value=0, required=False)


class ComicsListSerializer(OffsetPaginationSerializer):
    title = serializers.CharField(label='title', max_length=200)
