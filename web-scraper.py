import requests
from bs4 import BeautifulSoup
import re
import time
import json

base_url = "https://www.collegetransfer.net/Search/Search-for-Courses/Course-Search-Results"

# convert abbrev to state
us_state_to_abbrev = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
    "District of Columbia": "DC",
    "American Samoa": "AS",
    "Guam": "GU",
    "Northern Mariana Islands": "MP",
    "Puerto Rico": "PR",
    "United States Minor Outlying Islands": "UM",
    "Virgin Islands, U.S.": "VI",
}

# Create reverse mapping (abbreviation to full name)
us_abbrev_to_state = dict(map(reversed, us_state_to_abbrev.items()))

# load colleges data once
with open('high_transfer_community_colleges.json', 'r') as file:
    colleges_data = json.load(file)

# load existing data if file exists
existing_data = []
try:
    with open('high_transfer_college_catalogs.json', 'r') as file:
        existing_data = json.load(file)
    print(f"Loaded {len(existing_data)} existing colleges")
except FileNotFoundError:
    print("No existing file found, starting fresh")

# starting index
start_index = len(existing_data)
print(f"Starting from college index: {start_index}")

# Loop through next x colleges
end_index = min(start_index + 10, len(colleges_data))
for i in range(start_index, end_index):
    college = colleges_data[i]
    college_name = college['name']
    college_city = college.get('city', 'Unknown')
    college_state_abbrev = college.get('state', 'Unknown')
    college_zip = college['zip']
    
    # Convert state abbreviation to full state name
    college_state_converted = us_abbrev_to_state.get(college_state_abbrev, college_state_abbrev)
    
    print(f"\nProcessing college {i+1}/{len(colleges_data)}: {college_name}")
    print(f"State: {college_state_abbrev} -> {college_state_converted}")
    
    page = 1
    college_courses = []
    
    while True:
        # params
        params = {
            'instnm': college_name,
            # 'zip': college_zip,
            'distance': '5',
            'states': college_state_converted,
            'instType': 'AllInstitutions',
            'language': 'en-US',
            'page': page,
            'perpage': '50'
        }
        
        print(f"  Fetching page {page}...")
        response = requests.get(base_url, params=params)
        html = response.content
        soup = BeautifulSoup(html, "html.parser")
        
        # delay between requests
        time.sleep(1)

        ul = soup.find("ul", class_="student-course-search-results-list")
        # stop case
        if not ul:
            break
            
        # stop case
        course_blocks = ul.find_all("li")
        if not course_blocks:
            break

        courses = []
        for course in course_blocks:
            courseTitle = course.find("h3", class_="entityTitle").text.strip()
            courseCredit = course.find("div", class_="entitySubTitle course-search-course-credits").text.strip()
            
            # course title code and name regex
            match = re.match(r'([\w\s,]+):\s*(.+)', courseTitle)
            if match:
                course_code = match.group(1)
                course_name = match.group(2)
                courses.append({
                    "course code": course_code,
                    "course name": course_name,
                    "course credit": courseCredit
                })
        
        college_courses.extend(courses)
        page += 1
    
    # college entry
    college_entry = {
        "name": college_name,
        "city": college_city,
        "state": college_state_converted,
        "catalog": college_courses
    }
    
    # append if alr data
    existing_data.append(college_entry)
    print(f"Found {len(college_courses)} courses for {college_name}")

print(f"\nTotal colleges processed: {len(existing_data)}")
# save to JSON file
with open('high_transfer_college_catalogs.json', 'w') as file:
    json.dump(existing_data, file, indent=4)
print("Data saved to high_transfer_college_catalogs.json")



# testing
# courseTitle = ul.find_all("h3", class_="entityTitle")
# courseCredit = ul.find_all("div", class_="entitySubTitle course-search-course-credits")
# entire_course_block = ul.find_all("li")

# print(entityTitle)
# print(entire_course_block)