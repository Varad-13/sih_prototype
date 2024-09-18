# Useful functions we will frequently use in views and APIs for making model interactions simpler


days_to_bit = {
    'monday': 1000000,
    'tuesday': 100000,
    'wednesday': 10000,
    'thursday': 1000,
    'friday': 100,
    'saturday': 10,
    'sunday': 1
}

def days_to_bitmap(days):
    bitmap = 0
    for day in days:
        bitmap += days_to_bit[day]
    return bitmap

def bitmap_to_days(bitmap):
    days = []
    for day, value in days_to_bit.items():
        if bitmap >= value:
            days.append(day)
            bitmap -= value
    return days

