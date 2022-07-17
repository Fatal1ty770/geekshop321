from django.db import models

from django.conf import settings
from mainapp.models import Product


class Order(models.Model):

    FORMING = 'FM'
    SENT_TO_PROCEED = 'STP'
    PROCEEDED = 'PRD'
    PAID = 'PD'
    READY = 'RD'
    CANCEL = 'CNC'
    DELIVERED = 'DVD'

    ORDER_STATUS_CHOICES = (
        (FORMING, 'формируется'),
        (SENT_TO_PROCEED, 'отправлено в обработку'),
        (PROCEEDED, 'обработан'),
        (PAID, 'оплачен'),
        (READY, 'готов к выдаче'),
        (CANCEL, 'отменен'),
        (DELIVERED, 'выдан'),
    )


    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    created = models.DateTimeField(auto_now_add=True, verbose_name='создан')
    updated = models.DateTimeField(auto_now=True, verbose_name='обновлен')
    is_active = models.BooleanField(default=True)

    status = models.CharField(choices=ORDER_STATUS_CHOICES,
                              default=FORMING,
                              verbose_name='статус',
                              max_length=3,
                              )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return 'Текущий заказ : {}'.format (self.id)

    def get_total_quantity(self):
        items = self.orderitems.select_related()
        return sum(list(map(lambda x: x.quantity, items)))


    def get_product_type_quantity(self):
        items = self.orderitems.select_related()
        return len(items)

    def get_total_cost(self):
        items = self.orderitems.select_related()
        return sum(list(map(lambda x: x.quantity * x.product.price, items)))

    def delete(self):
        for item in self.orderitems.select_related():
            item.product.quantity += item.quantity
            item.product.save()

        self.is_active = False
        self.save()

    @staticmethod
    def get_item(pk):
        return Order.objects.get(pk=pk)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='orderitems')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='продукт')
    quantity = models.PositiveSmallIntegerField(default=0, verbose_name='количество')

    def get_product_cost(self):
        return self.product.price * self.quantity

    @staticmethod
    def get_item(pk):
        return Order.objects.get(pk=pk)