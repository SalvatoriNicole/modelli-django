from rest_framework import serializers

class DataSerializer(serializers.Serializer):
    LotId = serializers.CharField()
    year = serializers.IntegerField()
    month = serializers.CharField()
    location = serializers.CharField()
    semina = serializers.CharField()
    vegetables = serializers.ListField(child=serializers.CharField())#per accettare una lista
    coordinates = serializers.ListField(child=serializers.ListField(child=serializers.FloatField())) #per accettare lista di lista
    coordinates_ombra = serializers.ListField(child=serializers.ListField(child=serializers.FloatField()))

class CropdistributionListSerializer(serializers.Serializer):
    data = DataSerializer(many=True)