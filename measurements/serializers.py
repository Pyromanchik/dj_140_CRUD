from rest_framework import serializers

from measurements.models import Product, StockProduct, Stock


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description']


class ProductPositionSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = StockProduct
        fields = ['product', 'quantity', 'price']


class StockSerializer(serializers.ModelSerializer):
    positions = ProductPositionSerializer(many=True)

    class Meta:
        model = Stock
        fields = ['id', 'address', 'positions']

    def create(self, validated_data):
        positions_data = validated_data.pop('positions')
        stock = Stock.objects.create(**validated_data)
        for position in positions_data:
            StockProduct.objects.create(stock=stock, **position)
        return stock

    def update(self, instance, validated_data):
        instance.address = validated_data.get('address', instance.address)
        instance.save()

        positions_data = validated_data.pop('positions', [])
        for position in positions_data:
            product = position['product']
            StockProduct.objects.update_or_create(
                stock=instance,
                product=product,
                defaults={
                    'quantity': position.get('quantity'),
                    'price': position.get('price')
                }
            )
        return instance