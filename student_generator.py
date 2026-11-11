"""
Student Data Generator for SheerID Verification
Generates realistic student profiles (PSU Pattern)
"""
from faker import Faker
import random
from datetime import datetime, timedelta
import universities

fake = Faker('en_US')

def generate_student_profile(university=None):
    """
    Generate a full student profile with PSU-specific email format
    """
    if not university:
        university = universities.get_random_university()
        
    first_name = fake.first_name()
    last_name = fake.last_name()
    
    # Generate DOB (18-24 years old)
    age = random.randint(18, 24)
    dob_date = datetime.now() - timedelta(days=age*365 + random.randint(0, 364))
    birth_date = dob_date.strftime("%Y-%m-%d")
    
    # Generate Email based on University Domain
    domain = university.get("domain", "edu")
    digits = "".join([str(random.randint(0, 9)) for _ in range(random.choice([2, 3]))])
    
    # Randomize email format: first.last / f.last / firstl
    fmt = random.choice(["dot", "shrd", "fl"])
    if fmt == "dot":
         email = f"{first_name.lower()}.{last_name.lower()}{digits}@{domain}"
    elif fmt == "shrd":
         email = f"{first_name[0].lower()}{last_name.lower()}{digits}@{domain}"
    else:
         email = f"{first_name.lower()}{last_name[0].lower()}{digits}@{domain}"
    
    return {
        "firstName": first_name,
        "lastName": last_name,
        "birthDate": birth_date,
        "email": email,
        "organization": university,
        "metadata": {
            "locale": "en-US"
        },
        "display_info": {
            "full_name": f"{first_name} {last_name}",
            "age": age,
            "university": university["name"]
        }
    }

if __name__ == "__main__":
    print(generate_student_profile())
