import sys

def unquoted_string(quoted_text):
    """ http://tools.ietf.org/html/rfc5545#section-3.3.11 """
    unquoted = quoted_text.replace('\,', ',')
    unquoted = unquoted.replace('\;', ';')
    unquoted = unquoted.replace('\\n', '\n')
    unquoted = unquoted.replace('\\N', '\n')
    unquoted = unquoted.replace('\\\\;', '\\')
    return unquoted

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
            event_dir["dtstamp"] = eventprop[2]
        elif eventprop[0].upper() == "UID":
            event_dir["uid"] = eventprop[2]
        elif eventprop[0].upper() == "DTSTART":
            event_dir["dtstart"] = eventprop[2]
        elif eventprop[0].upper() == "CLASS":
            event_dir["class"] = eventprop[2]
        elif eventprop[0].upper() == "CREATED":
            event_dir["created"] = eventprop[2]
        elif eventprop[0].upper() == "DESCRIPTION":
            event_dir["description"] = unquoted_string(eventprop[2])
        elif eventprop[0].upper() == "GEO":
            event_dir["geo"] = eventprop[2]
        elif eventprop[0].upper() == "LAST-MOD":
            event_dir["last-mod"] = eventprop[2]
        elif eventprop[0].upper() == "LOCATION":
            event_dir["location"] = unquoted_string(eventprop[2])
        elif eventprop[0].upper() == "ORGANIZER":
            event_dir["organizer"] = unquoted_string(eventprop[2])
        elif eventprop[0].upper() == "PRIORITY":
            event_dir["priority"] = unquoted_string(eventprop[2])
        elif eventprop[0].upper() == "SEQ":
            event_dir["seq"] = unquoted_string(eventprop[2])
        elif eventprop[0].upper() == "STATUS":
            event_dir["status"] = unquoted_string(eventprop[2])
        elif eventprop[0].upper() == "SUMMARY":
            event_dir["summary"] = unquoted_string(eventprop[2])
        elif eventprop[0].upper() == "TRANSP":
            event_dir["transp"] = unquoted_string(eventprop[2])
        elif eventprop[0].upper() == "URL":
            event_dir["url"] = unquoted_string(eventprop[2])
        elif eventprop[0].upper() == "RECURID":
            event_dir["recurid"] = unquoted_string(eventprop[2])
        elif eventprop[0].upper() == "RRULE":
            event_dir["rrule"] = unquoted_string(eventprop[2])
        elif eventprop[0].upper() == "DTEND":
            event_dir["dtend"] = unquoted_string(eventprop[2])
        elif eventprop[0].upper() == "DURATION":
            event_dir["duration"] = unquoted_string(eventprop[2])
        elif eventprop[0].upper() == "ATTACH":
            event_dir["attach"] = unquoted_string(eventprop[2])
        elif eventprop[0].upper() == "ATTENDEE":
            event_dir["attendee"] = eventprop[2]
        elif eventprop[0].upper() == "CATEGORIES":
            event_dir["categories"] = eventprop[2]
        elif eventprop[0].upper() == "COMMENT":
            event_dir["comment"] = eventprop[2]
        elif eventprop[0].upper() == "CONTACT":
            event_dir["contact"] = eventprop[2]
        elif eventprop[0].upper() == "EXDATE":
            event_dir["exdate"] = eventprop[2]
        elif eventprop[0].upper() == "RSTATUS":
            event_dir["rstatus"] = eventprop[2]
        elif eventprop[0].upper() == "RELATED":
            event_dir["related"] = eventprop[2]
        elif eventprop[0].upper() == "RESOURCES":
            event_dir["resources"] = eventprop[2]
        elif eventprop[0].upper() == "RDATE":
            event_dir["rdate"] = eventprop[2]
        # x-prop / iana-prop
    vevents[i] = event_dir

f = open(sys.argv[2], 'w')
for event in vevents:
    f.write("UID: " + event["uid"] +'\n')
    f.write("DTSTART: " + event["dtstart"] +'\n')
    f.write("SUMMARY: " + event["summary"] +'\n')
    f.write("LOCATION: " + event["location"] + '\n')
    f.write("DESCRIPTION:" + event["description"] + '\n')
f.close

