from rest_framework import serializers
from .objects import Profile


class OutputSerializer(serializers.Serializer):
    auto = serializers.ListField(child=serializers.DictField())
    disability = serializers.CharField()
    home = serializers.ListField(child=serializers.DictField())
    life = serializers.CharField()
    umbrella = serializers.CharField()

    def create(self, validated_data):
        return Profile(**validated_data)
