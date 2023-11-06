import json
import os

from utility.models import GlobalSettings
from ....models import Country, Document
import json
from django.core.management.base import BaseCommand
import json
from utility.models import District, PostCode, Division, Upazilla
GEO_DATA = "data/countries.json"


# Opening JSON file
def load_json(name):
    f = open(os.path.join(os.path.dirname(os.path.dirname(__file__)), name, ), encoding="utf8")
    data = json.load(f)
    f.close()
    return data

def load_json_local(name):
    file_path = os.path.abspath(name)  # Use the absolute path directly
    with open(file_path, encoding="utf8") as f:
        data = json.load(f)
    return data


def load_geo_json():
    if Country.objects.count() <= 0:
        countries_json = load_json(GEO_DATA)
        countries = []
        for data in countries_json:
            country = Country(
                name=data['name'],
                code=data['isoCode'],
                phone_code=data['dialCode'],
                flag=data['flag']
            )
            countries.append(country)
        Country.objects.bulk_create(countries)





def load_bd_json(local=False):
    if local:
        DISTRICT_PATH = r"H:\Devsstream_NEW\kaaruj-backend-v2\coreapp\management\commands\data\bd_districts.json"
        POSTCODE_PATH = r"H:\Devsstream_NEW\kaaruj-backend-v2\coreapp\management\commands\data\bd_postcodes.json"
        DIVISION_PATH = r"H:\Devsstream_NEW\kaaruj-backend-v2\coreapp\management\commands\data\bd_divisions.json"
        UPAZILA_PATH = r"H:\Devsstream_NEW\kaaruj-backend-v2\coreapp\management\commands\data\bd_upazillas.json"
                
        district_data = load_json_local(DISTRICT_PATH)
        postcode_data = load_json_local(POSTCODE_PATH)
        division_data = load_json_local(DIVISION_PATH)
        upazila_data = load_json_local(UPAZILA_PATH)

    else:
        DISTRICT_PATH = "data/bd_districts.json"
        POSTCODE_PATH = "data/bd_postcodes.json"
        DIVISION_PATH = "data/bd_divisions.json"
        UPAZILA_PATH = "data/bd_upazillas.json"
        
        district_data = load_json(DISTRICT_PATH)
        postcode_data = load_json(POSTCODE_PATH)
        division_data = load_json(DIVISION_PATH)
        upazila_data = load_json(UPAZILA_PATH)
        
    for district_entry in district_data:
        district = District(
            id=district_entry["id"],
            division_id=district_entry["division_id"],
            name=district_entry["name"]
        )
        district.save()

    # Insert data into PostCode model
    for postcode_entry in postcode_data:
        postcode = PostCode(
            upazila=postcode_entry["upazila"],
            name=postcode_entry["name"],
            postCode=postcode_entry["postCode"]
        )
        postcode.save()

    # Insert data into Division model
    for division_entry in division_data:
        division = Division(
            id=division_entry["id"],
            name=division_entry["name"],
            bn_name="",
            # bn_name=division_entry["bn_name"],
            lat=division_entry["lat"],
            long=division_entry["long"]
        )
        division.save()

    # Insert data into Upazila model
    for upazila_entry in upazila_data:
        upazila = Upazilla(
            id=upazila_entry["id"],
            district_id=upazila_entry["district_id"],
            name=upazila_entry["name"]
        )
        upazila.save()


def LoadRedexLocationData(local=False):
    import openpyxl
    from utility.models import RedexDivision, RedexDistrict, RedexArea
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "address_data_kaaruj.xlsx")
    workbook = openpyxl.load_workbook(path)
    sheet = workbook.active

    # Iterate through the rows in the Excel sheet
    for row in sheet.iter_rows(min_row=2, values_only=True):
        division_name, division_id, district_name, district_id, area_name, area_id, inside_dhaka, delivery_charge = row

        # Create or get the division
        division, created = RedexDivision.objects.get_or_create(id=division_id, defaults={'name': division_name})

        # Create or get the district
        district, created = RedexDistrict.objects.get_or_create(id=district_id, defaults={'name': district_name, 'division': division})
        is_area_exists = RedexArea.objects.filter(id=area_id).first()
        if is_area_exists:
            if is_area_exists.name != area_name or is_area_exists.district != district or is_area_exists.division != division or is_area_exists.delivery_charge != delivery_charge or is_area_exists.inside_dhaka != inside_dhaka:
                print(f"Updating area {area_name}")
                RedexArea.objects.filter(id=area_id).update(
                    name=area_name,
                    district=district,
                    division=division,
                    delivery_charge=delivery_charge,
                    inside_dhaka=inside_dhaka
                )
        else:
            print(f"creating area {area_name}")

            RedexArea.objects.create(
                id=area_id,
                name=area_name,
                district=district,
                division=division,
                delivery_charge=delivery_charge,
                inside_dhaka=inside_dhaka
            )