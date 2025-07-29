def is_valid_phone(phone):
    return phone.startswith("1") and len(phone) >= 9

def is_valid_name(name):
    return bool(name and name.strip())

def is_valid_dob(month, day, year):
    try:
        month = int(month)
        day = int(day)
        year = int(year)
        return 1 <= month <= 12 and 1 <= day <= 31 and year > 0
    except:
        return False
