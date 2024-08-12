from rest_framework import serializers


class FilterSerializer(serializers.Serializer):
    cities = serializers.ListField(child=serializers.CharField())
    departments = serializers.ListField(child=serializers.CharField())
    positions = serializers.ListField(child=serializers.CharField())

    class Meta:
        swagger_schema_fields = {
            "example": {
                "cities": [
                    "Краснодар",
                    "Пермь",
                    "Саратов",
                ],
                "departments": [
                    "Backend",
                    "DevOps",
                    "Frontend",
                ],
                "positions": [
                    "Backend-разработчик",
                    "Frontend-разработчик",
                    "Fullstack-разработчик",
                ],
            },
        }
