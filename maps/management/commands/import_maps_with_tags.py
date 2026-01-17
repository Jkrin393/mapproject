import csv
import re
from django.core.management.base import BaseCommand
from maps.models import Map, Tag

from decimal import Decimal, InvalidOperation
from collections import defaultdict

import us
from rapidfuzz import process, fuzz #https://github.com/rapidfuzz/RapidFuzz/blob/main/README.md


#the tags from the original csv data base are inconsistent in spelling, appreviation, capitalization, comma usage, and number of tags
#this script attempts to clean and apply the tags to allow importing to the admin panel. 
#the "us" library is used to match the variations of state abbreviations. Rapidfuzz to help account for mispellings compared to the offical Tags from the Tag table based on a confidence score.

#cleaning steps line by line. remove whitespace and ensure lowercase. replace etc with nothing. replace "/"" with comma. replace "and" with comma. remove possible extra whitespace. check corrections dictionary. Capitalzie final product.


TAG_MAPPING={ #typos i noticed from the source csv
        "switz": "Switzerland",
        "Central Americ": "Central America",
        "carib.": "caribbean"

}

def normalize_tags(input_string):
    tag=input_string.strip().lower()
    tag=tag.replace("etc","")
    tag=tag.replace("/",",")
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


#notes/reminders for rapidFuzz behavior
##flat tag converts the population from tuples to strings
#extractOne() returns a tuple of size 3 (match, score, index). with the above flat flag match is a string


FUZZ_RATIO=90
def match_to_existing_tag(input_tag, existing_tags_list, tags_by_name):
    #some tags exist in two categories, for example Georgia is both a state and country. To get around this i create a list with similar/duplicated names and prioritize state.

    if not input_tag:
        return None

    result=process.extractOne(input_tag.lower(),existing_tags_list,scorer=fuzz.ratio)
    if not result:
        return None
    
    best_tag_match,score,_=result
    if score<FUZZ_RATIO:
        return None

    candidate_matches=tags_by_name[best_tag_match]
    for match in candidate_matches:
        if match.name.lower()=='georgia' and match.category=='state':
            return match

    if len(candidate_matches)>1:
        return None
    
    return candidate_matches[0]
    
    """best_tag_match,score,_=process.extractOne(input_tag,existing_tags_list,scorer=fuzz.ratio)
    if best_tag_match is None:
        return None
    """  

#guard against empty or invalid inputs in height, width, price fields of the import by explicity casting
def safe_integer_conversion(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return None
    
def safe_decimal_conversion(value):
    if value is None:
        return None
    value=str(value).replace('$','').replace(',','').strip() #add a replace for any non decimal values as they are encountered
    try:
        return Decimal(value)
    except(InvalidOperation,ValueError,TypeError):
        return None 

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
        flagged_tags={} #want to list and note error tags and avoid adding those isntances

        imported_count=0
        updated_count=0
        
        #preload tags in a list to prevent my CPU crashing
        all_tags_in_database=Tag.objects.all() 
        tags_by_name=defaultdict(list) #dict[lowercase name, list[Tag]]
        for tag in all_tags_in_database:
            tags_by_name[tag.name.lower()].append(tag)
        existing_tag_names=list(tags_by_name.keys())#lowercased unique names for rapidfuzz scoring

        with open(csv_file,newline='',encoding='utf-8') as file:
            reader=csv.DictReader(file)

            for row in reader:
                read_external_map_id_from_csv=row.get('Map ID','').strip()
                read_map_title_from_csv=row.get('MapTitle','') or 'No Title'
                
                map_object,success_flag=Map.objects.update_or_create(
                    external_map_id=read_external_map_id_from_csv,
                    defaults={
                        'map_title': read_map_title_from_csv,
                        'map_maker': row.get('MapMaker', ''),
                        'map_year': row.get('MapYear', None),
                        'map_height': safe_decimal_conversion(row.get('MapHeight', None)),
                        'map_width': safe_decimal_conversion(row.get('MapWidth', None)),
                        'description': row.get('description', ''),
                        'map_price': safe_decimal_conversion(row.get('MapPrice', None)),
                        'map_info_memo': row.get('MapInfoMemo', ''),
                        'planned_use': row.get('tag', ''),
                        'image': row.get('image', None),
                        'physical_location': row.get('Location (Physical)',''),
                    }
                )

                if success_flag:
                    imported_count+=1
                else:
                    updated_count+=1

                #The csv can have multiple entries in the MapArea column(which is mapping to Tag.name). Below we:
                # 1) split the entries on commas and remove and edge case nonsense
                # 2) clean the data with normalize_tags(), match any state abbreviations with match_us_state(), 
                # 3) and check if the tag exists with match_to_existing_tag() to either create the new tag or add the existing  tag the new Map entry
                # 4) flag invalid/mismatched tags and instances of multiple tag names(Rome-city vs Rome-region)
                map_area_input_from_csv=row.get('MapArea','')
                if map_area_input_from_csv:
                    split_map_areas_from_csv=[ t.strip() for t in re.split(r',| and ', map_area_input_from_csv)
                        if t.strip()] ##removes empty string after a trailing comma in the case of "Mass.,Conn,"
                    
                    cleaned_tags=[]

                    for tag_fragment in split_map_areas_from_csv:
                        if '(' in tag_fragment or ')' in tag_fragment:
                            key=read_external_map_id_from_csv or read_map_title_from_csv
                            flagged_tags.setdefault(key, []).append(f"{tag_fragment} (Parenthesis detected)")
                            continue

                        potential_tag_name=normalize_tags(tag_fragment)
                        full_state_name=match_us_state(tag_fragment)
                        if full_state_name:
                            potential_tag_name=full_state_name
                        
                        existing_tag=match_to_existing_tag(potential_tag_name,existing_tag_names,tags_by_name)
                        if existing_tag:
                            if existing_tag not in cleaned_tags:
                                cleaned_tags.append(existing_tag)
                        else:
                            key=read_external_map_id_from_csv or read_map_title_from_csv
                            normalized_tag_name=potential_tag_name.lower()
                            if(normalized_tag_name in tags_by_name and len(tags_by_name[normalized_tag_name])>1):
                                tag_categories=", ".join(t.get_category_display() for t in tags_by_name[normalized_tag_name])
                                flagged_tags.setdefault(key, []).append(f"{potential_tag_name} has multiple categories: {tag_categories}")
                            else:
                                flagged_tags.setdefault(key, []).append(potential_tag_name)
                    
                    map_object.tags.set(cleaned_tags)
        self.stdout.write("------import complete-----")
        self.stdout.write(f'created: {imported_count}')
        self.stdout.write(f'updated: {updated_count}')

        if flagged_tags:
            self.stdout.write(self.style.WARNING('Potential Tags for review'))
            with open('flagged_tags.txt','w',encoding='utf-8') as outfile:
                for key, tag in flagged_tags.items():
                    line=f"{key}: {', '.join(tag)}"
                    self.stdout.write(line)
                    outfile.write(line + '\n')
        else:
            self.stdout.write("no entries flagged")
