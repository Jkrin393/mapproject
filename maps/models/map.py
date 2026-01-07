#this model represents a single instance of a map
from django.db import models

class Map(models.Model):
    title=models.CharField(max_length=200)
    description=models.TextField(blank=True)
    date=models.DateField(null=True,blank=True)
    image=models.ImageField(upload_to='maps/')
    tags=models.ManyToManyField('Tag',blank=True)
    #placeholder for collection colletion=models.ForeignKey()

    def __str__(self):
        return self.title

class Collection(models.Model):
    name=models.CharField(max_length=200)
    description=models.TextField(blank=True)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name=models.CharField(max_length=50)

    def __str__(self):
        return self.name

