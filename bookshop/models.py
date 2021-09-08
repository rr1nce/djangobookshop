from django.conf import settings

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone

from utils import upload_function

class MediaType(models.Model): # Носитель: электронный или бумажный

    name = models.CharField(max_length=100, verbose_name='Название носителя')

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Носитель'
        verbose_name_plural = 'Носитель'

class Author(models.Model):
    """Автор"""
    name = models.CharField(max_length=255, verbose_name='Имя автора')
    slug = models.SlugField()
    image = models.ImageField(upload_to = upload_function, null=True, blank=True)
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Автор'
        verbose_name_plural = 'Авторы'

class Genre(models.Model):
    """Жанр"""
    name = models.CharField(max_length=50, verbose_name='Название жанра')
    slug = models.SlugField()

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

class Book(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, verbose_name='Автор')
    publisher = models.ForeignKey('Publisher', on_delete=models.CASCADE, verbose_name='Издатель')
    name = models.CharField(max_length=255, verbose_name='Название книги')
    slug = models.SlugField()
    image = models.ImageField(upload_to = upload_function)
    media_type = models.ForeignKey(MediaType, verbose_name='Носитель', on_delete=models.CASCADE)
    release_year = models.IntegerField(verbose_name='Год релиза')
    description = models.TextField(verbose_name='Описание', default='Описание появится позже')
    stock = models.IntegerField(default=1, verbose_name='Наличие на складе')
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Цена')
    offer_of_the_week = models.BooleanField(default=False, verbose_name='Предложение недели?')

    def __str__(self):
        return f'{self.id} | {self.author.name} | {self.publisher.name} | {self.name}'
    
    @property
    def ct_model(self):
        return self._meta.model_name

    class Meta:
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'

class CartProduct(models.Model):
    """Продукт корзины"""
    
    user = models.ForeignKey('Customer', verbose_name='Покупатель', on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name='Корзина', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    qty = models.PositiveIntegerField(default = 1)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Общая цена')
    
    def __str__(self):
        return f'Продукт: {self.content_object.name} (для корзины)'
    
    def save(self, *args, **kwargs):
        self.final_price = self.qty * self.content_object.price
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Продукт корзины'
        verbose_name_plural = 'Продукты корзины'
    

class Cart(models.Model):
    """Корзина"""

    owner = models.ForeignKey('Customer', verbose_name='Покупатель', on_delete=models.CASCADE)
    products = models.ManyToManyField(CartProduct, blank=True, null=True, related_name='related_cart', verbose_name="Продукты для корзины")
    total_products = models.IntegerField(default=0, verbose_name='Общее кол-во товара')
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Общая цена')
    in_order = models.BooleanField(default=False)
    for_anonymous_user = models.BooleanField(default=True)

    def __str__(self):
        return str(self.id)
    
    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'


class Publisher(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название издательства')
    slug = models.SlugField()
    image = models.ImageField(upload_to=upload_function, null=True, blank=True)
    description = models.TextField(verbose_name='Описание издательства')

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Издательство'
        verbose_name_plural = 'Издательство'


class Order(models.Model):

    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_READY = 'is_ready'
    STATUS_COMPLETED = 'completed'

    BUYING_TYPE_SELF = 'self'
    BUYING_TYPE_DELIVERY = 'delivery'

    STATUS_CHOICES = (
        (STATUS_NEW, 'Новый заказ'),
        (STATUS_IN_PROGRESS, 'Заказ в обработке'),
        (STATUS_READY, 'Заказ готов'),
        (STATUS_COMPLETED, 'Заказ получен покупателем')
    )

    BUYING_TYPE_CHOICES = (
        (BUYING_TYPE_SELF, 'Самовывоз'),
        (BUYING_TYPE_DELIVERY, 'Доставка')
    )

    customer = models.ForeignKey('Customer', verbose_name='Покупатель', related_name='orders', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, verbose_name='Имя')
    last_name = models.CharField(max_length=255, verbose_name='Фамилия')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    cart = models.ForeignKey(Cart, verbose_name='Корзина', on_delete=models.CASCADE)
    address = models.CharField(max_length=1024, verbose_name='Адрес', null=True, blank=True)
    status = models.CharField(max_length=100, verbose_name='Статус заказа', choices=STATUS_CHOICES, default=STATUS_NEW)
    buying_type = models.CharField(max_length=100, verbose_name='Тип заказа', choices=BUYING_TYPE_CHOICES)
    comment = models.TextField(verbose_name='Комментарий к заказу', null=True, blank=True)
    created_at = models.DateField(verbose_name='Дата создания заказа', auto_now = True)
    order_date = models.DateField(verbose_name='Дата получения заказа', default=timezone.now)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class Customer(models.Model):
    """Покупатель"""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    is_active = models.BooleanField(default=True, verbose_name='Активный?')
    customer_orders = models.ManyToManyField(
        Order, blank = True, related_name='related_customer', verbose_name='Заказы покупателя'
    )
    wishlist = models.ManyToManyField(Book, blank=True, verbose_name='Список ожидаемого')
    phone = models.CharField(max_length=20, verbose_name='Номер телефона')
    address = models.TextField(null = True, blank = True, verbose_name='Адрес проживания')

    def __str__(self):
        return f"{self.user.username}"
    
    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = 'Покупатели'

class Notification(models.Model):
    """Уведомления"""

    recipient = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='Получатель')
    text = models.TextField()
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Уведомление для {self.recipient.user.username} | id = {self.id}"
    
    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'


class ImageGallery(models.Model):

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    image = models.ImageField(upload_to=upload_function)
    use_in_slider = models.BooleanField(default=False)

    def __str__(self):
        return f'Изображение для {self.content_object}'
    
    class Meta:
        verbose_name = 'Галерея изображений'
        verbose_name_plural = 'Галерея изображений'