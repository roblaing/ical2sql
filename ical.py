import sys, datetime, pytz

tz = "Africa/Johannesburg"
# http://www.twinsun.com/tz/tz-link.htm
table_name = "vevents"

def sql_text(quoted_text):
    """ http://tools.ietf.org/html/rfc5545#section-3.3.11 """
    unquoted = quoted_text.replace('\,', ',')
    unquoted = unquoted.replace('\;', ';')
    unquoted = unquoted.replace('\\n', '\n')
    unquoted = unquoted.replace('\\N', '\n')
    unquoted = unquoted.replace('\\\\;', '\\')
    # escape single quotes in text with another single quote
    unquoted = unquoted.replace("'", "''")
    return "'" + unquoted + "'"

def utc2local(date_text,date_params):
    """http://tools.ietf.org/html/rfc5545#section-3.3.5 """
    utc = pytz.utc
    tzid = pytz.timezone(tz)
    # FORM #1: DATE WITH LOCAL TIME (floating)
    # 19980118T230000  YYYYMMDDThhmmss   %Y%m%dT%H%M%S 
    # FORM #2: DATE WITH UTC TIME (fixed)
    # 19980119T070000Z
    if date_text[-1].upper() == "Z":
        utc_dt = utc.localize(datetime.datetime.strptime(date_text,"%Y%m%dT%H%M%SZ"))
        loc_dt = utc_dt.astimezone(tzid)
        return "'" + loc_dt.strftime("%Y-%m-%d %H:%M:%S " + tz) + "'"       
    # FORM #3: DATE WITH LOCAL TIME AND TIME ZONE REFERENCE
    # TZID=America/New_York:19980119T020000 
    # print(date_text)
    return "'" + date_text + "'"   
    
# do the unfolding in this step
f = open(sys.argv[1], 'rU')
data = f.readlines()
f.close
unfolded_data = [data[0].rstrip()]
for line_number in range(1,len(data)):
    if data[line_number][0] == ' ':
        unfolded_data[-1] = unfolded_data[-1].rstrip() + data[line_number][1:]
    else:
        unfolded_data = unfolded_data + [data[line_number].rstrip()]

# contentline   = name *(";" param ) ":" value CRLF
# convert to tuple (name,param_dict,value)
contentlines = [line.partition(':') for line in unfolded_data]
new_contentlines = []
for (name,colon,value) in contentlines:
    params_dict = {}
    params=name.split(';')
    for i in range(1,len(params)):
        param = params[i].split('=')
        params_dict[param[0]] = param[1]
    new_contentlines = new_contentlines + [(params[0],params_dict,value)]

# get starts and ends of vevents
vevent_begin = []
vevent_end = []
for i in range(len(new_contentlines)):
    if (new_contentlines[i][0].upper() == "BEGIN") and (new_contentlines[i][2].upper() == "VEVENT"): vevent_begin.append(i)
    elif (new_contentlines[i][0].upper() == "END") and (new_contentlines[i][2].upper() == "VEVENT"): vevent_end.append(i)

# create list of vevent lists
vevents = []
for i in range(len(vevent_begin)):
    vevents.append(new_contentlines[vevent_begin[i]+1:vevent_end[i]])

# create an sql insert statement for each vevent element
# http://tools.ietf.org/html/rfc5545#section-3.6.1
for i in range(len(vevents)):
    event_dir = {}
    for eventprop in vevents[i]:
        if eventprop[0].upper() == "DTSTAMP":
            # must be left as UTC
            event_dir["dtstamp"] = sql_text(eventprop[2])
        elif eventprop[0].upper() == "UID":
            event_dir["uid"] = sql_text(eventprop[2])
        elif eventprop[0].upper() == "DTSTART":
            event_dir["dtstart"] = utc2local(eventprop[2],eventprop[1])
        elif eventprop[0].upper() == "CLASS":
            event_dir["class"] = sql_text(eventprop[2])
        elif eventprop[0].upper() == "CREATED":
            # must be left as UTC
            event_dir["created"] = sql_text(eventprop[2])
        elif eventprop[0].upper() == "DESCRIPTION":
            event_dir["description"] = sql_text(eventprop[2])
        elif eventprop[0].upper() == "GEO":
            event_dir["geo"] = sql_text(eventprop[2])
        elif eventprop[0].upper() == "LAST-MOD":
            event_dir["last_mod"] = utc2local(eventprop[2],eventprop[1])
        elif eventprop[0].upper() == "LOCATION":
            event_dir["location"] = sql_text(eventprop[2])
        elif eventprop[0].upper() == "ORGANIZER":
            event_dir["organizer"] = sql_text(eventprop[2])
        elif eventprop[0].upper() == "PRIORITY":
            event_dir["priority"] = sql_text(eventprop[2])
        elif eventprop[0].upper() == "SEQUENCE":
            event_dir["seq"] = eventprop[2]
        elif eventprop[0].upper() == "STATUS":
            event_dir["status"] = sql_text(eventprop[2])
        elif eventprop[0].upper() == "SUMMARY":
            event_dir["summary"] = sql_text(eventprop[2])
        elif eventprop[0].upper() == "TRANSP":
            event_dir["transp"] = sql_text(eventprop[2])
        elif eventprop[0].upper() == "URL":
            event_dir["url"] = sql_text(eventprop[2])
        elif eventprop[0].upper() == "RECURID":
            event_dir["recurid"] = sql_text(eventprop[2])
        elif eventprop[0].upper() == "RRULE":
            event_dir["rrule"] = sql_text(eventprop[2])
        elif eventprop[0].upper() == "DTEND":
            event_dir["dtend"] = utc2local(eventprop[2],eventprop[1])
        elif eventprop[0].upper() == "DURATION":
            event_dir["duration"] = sql_text(eventprop[2])
        elif eventprop[0].upper() == "ATTACH":
            event_dir["attach"] = sql_text(eventprop[2])
        elif eventprop[0].upper() == "ATTENDEE":
            event_dir["attendee"] = sql_text(eventprop[2])
        elif eventprop[0].upper() == "CATEGORIES":
            event_dir["categories"] = sql_text(eventprop[2])
        elif eventprop[0].upper() == "COMMENT":
            event_dir["comment"] = sql_text(eventprop[2])
        elif eventprop[0].upper() == "CONTACT":
            event_dir["contact"] = sql_text(eventprop[2])
        elif eventprop[0].upper() == "EXDATE":
            event_dir["exdate"] = utc2local(eventprop[2],eventprop[1])
        elif eventprop[0].upper() == "RSTATUS":
            event_dir["rstatus"] = sql_text(eventprop[2])
        elif eventprop[0].upper() == "RELATED":
            event_dir["related"] = sql_text(eventprop[2])
        elif eventprop[0].upper() == "RESOURCES":
            event_dir["resources"] = sql_text(eventprop[2])
        elif eventprop[0].upper() == "RDATE":
            event_dir["rdate"] = sql_text(eventprop[2])
        # x-prop / iana-prop
    vevents[i] = event_dir

f = open(sys.argv[2], 'w')
f.write("CREATE TABLE " + table_name + " (\n")
f.write("    uid         TEXT PRIMARY KEY,\n")
f.write("    dtstamp     TEXT NOT NULL,\n")
f.write("    dtstart     TEXT,\n")
f.write("    class       TEXT,\n")
f.write("    created     TEXT,\n")
f.write("    description TEXT,\n")
f.write("    geo         TEXT,\n")
f.write("    last_mod    TEXT,\n")
f.write("    location    TEXT,\n")
f.write("    organizer   TEXT,\n")
f.write("    priority    TEXT,\n")
f.write("    seq         INTEGER,\n")
f.write("    status      TEXT,\n")
f.write("    summary     TEXT,\n")
f.write("    transp      TEXT,\n")
f.write("    url         TEXT,\n")
f.write("    recurid     TEXT,\n")
f.write("    rrule       TEXT,\n")
f.write("    dtend       TEXT,\n")
f.write("    duration    TEXT,\n")
f.write("    attach      TEXT,\n")
f.write("    attendee    TEXT,\n") 
f.write("    categories  TEXT,\n") 
f.write("    comment     TEXT,\n") 
f.write("    contact     TEXT,\n") 
f.write("    exdate      TEXT,\n") 
f.write("    rstatus     TEXT,\n") 
f.write("    related     TEXT,\n") 
f.write("    resources   TEXT,\n") 
f.write("    rdate       TEXT\n")
f.write(");\n")
for event in vevents:
    insert_statement = "INSERT INTO " + table_name + "("
    values_statement = "VALUES (" 
    for attribute in event.iteritems():
        insert_statement = insert_statement + attribute[0] + ", " 
        values_statement = values_statement + attribute[1] + ", "
    f.write(insert_statement[:-2] + ")\n")
    f.write(values_statement[:-2] + ");\n")
f.close

# sqlite3
# .read joeblog.sql
# SELECT summary FROM vevents WHERE location = 'Amuse Cafe Linden';

