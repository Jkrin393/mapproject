#this model represents a single instance of a map
from django.db import models
import re #regex library

class Map(models.Model):
   ###### primary keys ######
    external_map_id=models.IntegerField(
        null=True,
        unique=True,
        help_text="ID from Excel source"
    )

    #####  map details #########
    map_maker=models.CharField(max_length=200,null=True)
    map_year=models.CharField(
        max_length=50,
        blank=True,
        help_text="year the map depicts"
        )
    map_height=models.IntegerField(null=True)
    map_width=models.IntegerField(null=True)
    map_title=models.CharField(max_length=200)
    description=models.TextField(blank=True)
    map_price=models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Listed Price"
        )
    map_info_memo=models.CharField(max_length=200, blank=True)
    planned_use=models.CharField(max_length=25, blank=True)
    physical_location=models.CharField(max_length=200, blank=True)

    # Relationships to other models
    image=models.ImageField(upload_to='maps/', blank=True)
    tags=models.ManyToManyField('Tag', blank=True, related_name='maps')
    collection=models.ForeignKey(  
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
    
    
    #functions to pull sort year from map_year
    #dates from source are not all 4 digit years. Some are estimates, ranges, or others noted by specific characters (<year>*,<year>c, approx:<year>, etc)
    def get_sort_year(self): #convert years stored as strings(to account for ranges, estimates, non-numeric charactesr) to integer for sorting  
        if not self.map_year:
            return None
        matched_year = re.search(r'\d{4}', self.map_year)
        return int(matched_year.group()) if matched_year else None
    ##perhaps add more sorting regex functions to differenciate map_years that are estimates/ranges from specific years

class Collection(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Tag(models.Model):
    TAG_CATEGORIES = [
        ('region', 'Region'),
        ('state', 'US State'),
        ('country', 'Country'),
        ('cont','Continent'),
        ('city','City'),
        ('river','River'),
        ('content','Content'),
        ('era', 'Historical Era'),
        ('type', 'Print Type'),#wood carving, framed, catalog, map
        ('misc', 'Miscellaneous'),
    ]
    
    name = models.CharField(max_length=50)
    category = models.CharField(
        max_length=20,
        choices=TAG_CATEGORIES,
        default='region'
    )

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"
    
    class Meta:
        ordering = ['category', 'name']
        unique_together = ['name', 'category']