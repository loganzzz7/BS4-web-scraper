import json

with open('high_transfer_college_catalogs.json', 'r') as file:
    catalog_data = json.load(file)

count = 0
colleges_with_catalog = []

for i in range(len(catalog_data)):
    if catalog_data[i]["catalog"]:
        count += 1
        colleges_with_catalog.append({
            "verified_college": catalog_data[i]["name"]
        })

print(f"Found {count} colleges with catalogs")

with open("college_list_has_catalog.json", "w") as file:
    json.dump(colleges_with_catalog, file, indent=4)