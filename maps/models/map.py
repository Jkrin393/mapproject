#this model represents a single instance of a map
from django.db import models

class Map(models.Model):
    django_id=models.BigAutoField(primary_key=True)
    external_map_id=models.IntegerField(
        null=True,
        blank=True,
        unique=True
    )
    map_maker=models.CharField(max_length=200)
    map_year=models.DateField(null=True, blank=True)
    map_height=models.IntegerField(null=True)
    map_width=models.IntegerField(null=True)
    map_title=models.CharField(max_length=200)
    description=models.TextField(blank=True)
    map_price=models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    map_info_memo=models.CharField(max_length=200, blank=True)
    planned_use=models.CharField(max_length=25)

    # Relationships to other models
    image=models.ImageField(upload_to='maps/')
    tags=models.ManyToManyField('Tag', blank=True, related_name='maps')
    collection=models.ForeignKey(  # Fixed typo
        'Collection',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='maps',
    )

    #metadata
    upload_date=models.DateTimeField(auto_now_add=True)
    last_edit_date=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.map_title

class Collection(models.Model):
    name=models.CharField(max_length=200)
    description=models.TextField(blank=True)

    def __str__(self):
        return self.name

class Tag(models.Model):
    TAG_CATEGORIES=[
        ('area','Area'),
        ('era','Historical Era'),
        ('phys_loc','Physical storage location'),

    ]

    name=models.CharField(max_length=50)
    category=models.CharField(
        max_length=200,
        choices=TAG_CATEGORIES,
        default="area"
    )

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})" #get_<field_name>_display() returns full name from <field_name> dictionary
