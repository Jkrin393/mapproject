import csv
import re
from django.core.management.base import BaseCommand
from maps.models import Map, Tag

import us
from rapidfuzz import process, fuzz #https://github.com/rapidfuzz/RapidFuzz/blob/main/README.md


#the tags from the original csv data base are inconsistent in spelling, appreviation, capitalization, comma usage, and number of tags
#this script attempts to clean and apply the tags to allow importing to the admin panel. 
#the "us" library is used to match the variations of state abbreviations. Rapidfuzz to help account for mispellings compared to the offical Tags from the Tag table based on a confidence score.

#cleaning steps line by line. remove whitespace and ensure lowercase. replace etc with nothing. replace "/"" with comma. replace "and" with comma. remove possible extra whitespace. check corrections dictionary. Capitalzie final product.

TAG_MAPPING={ #typos i noticed from the source csv
        "switz": "Switzerland",
        "Central Americ": "Central America",

}

def normalize_tags(input_string):
    tag=input_string.strip().lower()
    tag=input_string.replace("etc","")
    tag=input_string.replace("/",",")
    tag=re.sub(r'\s+',' ',tag) #(pattern, replacement, string)
    
    tag=TAG_MAPPING.get(tag, tag) #replace with found match or return default
    tag=" ".join([word.capitalize() for word in tag.split()])
    return tag


def match_us_state(input_state):
    if not input_state:
        return None
    cleaned_input=input_state.replace('.','').strip()
    state_abbreviation=us.states.lookup(cleaned_input)
    if(state_abbreviation):
        return state_abbreviation.name
    return None

#rapidfuzz matching
FUZZ_RATIO=90
def match_to_existing_tag(input_tag):
    existing_tags_list=Tag.objects.values_list('name')
    #process returns the estimated match and the associated score
    guessed_tag_match,score=process.extractOne(input_tag,existing_tags_list,scorer=fuzz.ratio)
    if score>=FUZZ_RATIO:
        return Tag.objects.get(name=guessed_tag_match)
    return None

#Django mgmt commands have to follow the expected names. inheritence not flexible
#https://dracodes.hashnode.dev/how-to-create-a-custom-managepy-command-in-django#
class Command(BaseCommand):
    help="import map data from raw csv, attempt to normalize region to match rows from Tags table"

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help="path to csv import"
        )
        
    def handle(self, *args, **options):
        csv_file=options['csv_file']
        flagged_tags={} #want to note new tags before adding to table

        with open(csv_file,newline='',encoding='utf-8') as file:
            reader=csv.DictReader(file)
            for row in reader:
                read_external_map_id_from_csv=row.get('Map ID','').strip()
                read_map_title_from_csv=row.get('MapTitle','') or 'No Title'
                map_object,success_bool=Map.objects.update_or_create(
                    external_map_id=read_external_map_id_from_csv,
                    defaults={
                        'map_title': read_map_title_from_csv,
                        'map_maker': row.get('MapMaker', ''),
                        'map_year': row.get('MapYear', None),
                        'map_height': row.get('MapHeight', None),
                        'map_width': row.get('MapWidth', None),
                        'description': row.get('description', ''),
                        'map_price': row.get('MapPrice', None),
                        'map_info_memo': row.get('MapInfoMemo', ''),
                        'planned_use': row.get('tag', ''),
                        'image': row.get('image', None),
                        'physical_location': row.get('Location (Physical)',''),
                    }
                )

                #Maparea of CSV to rows in Tag Table
                map_area_input_from_csv=row.get('MapArea','')
                if map_area_input_from_csv:
                    split_map_areas_from_csv=re.split(r',| and ', map_area_input_from_csv)
                    cleaned_tags=[]

                    for cleaned_tag in split_map_areas_from_csv:
                        potential_tag_name=normalize_tags(cleaned_tag)
                        full_state_name=match_us_state(cleaned_tag)
                        if full_state_name:
                            potential_tag_name=full_state_name
                        existing_tag=match_to_existing_tag(potential_tag_name)
                        
                        if existing_tag:
                            cleaned_tags.append(potential_tag_name)
                        else:
                            key=read_external_map_id_from_csv or read_map_title_from_csv
                            flagged_tags.setdefault(key, []).append(potential_tag_name)
                    
                    map_object.tags.set(cleaned_tags)
        
        if flagged_tags:
            self.stdout.write(self.style.WARNING('Potential Tags for review'))
            with open('flagged_tags.txt','w',encoding='utf-8') as outfile:
                for key, tag in flagged_tags.items():
                    line=f"{key}: {', '.join(tag)}"
                    self.stdout.write(line)
                    outfile.write(line + '\n')



