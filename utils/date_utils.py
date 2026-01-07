import datetime

def get_today_str():
    return datetime.datetime.now().strftime("%Y-%m-%d")

def format_date(dt_obj):
    return dt_obj.strftime("%Y-%m-%d")
