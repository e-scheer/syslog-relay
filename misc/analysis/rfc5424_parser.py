import re
from dateutil.parser import parse

rfc5424_pattern = r'^<(?P<priority>\d{1,3})>(?P<version>\d{1,2})\s(?P<timestamp>-|(?P<fullyear>[12]\d{3})-(?P<month>0\d|[1][012])-(?P<mday>[012]\d|3[01])T(?P<hour>[01]\d|2[0-4]):(?P<minute>[0-5]\d):(?P<second>[0-5]\d|60)(?#60seconds can be used for leap year!)(?:\.(?P<secfrac>\d{1,6}))?(?P<numoffset>Z|[+-]\d{2}:\d{2})(?#=timezone))\s(?P<hostname>[\S]{1,255})\s(?P<appname>[\S]{1,48})\s(?P<procid>[\S]{1,128})\s(?P<msgid>[\S]{1,32})\s(?P<structureddata>-|(?:\[.+?(?<!\\)\])+)(?:\s(?P<msg>.+))?$'

msgs_by_seq = {}
#14-08-2022_23-00-23.log
filename = "14-08-2022_23-22-23.log"
with open(filename, encoding="utf8", errors='ignore') as f:
    for line in f.readlines():
        match = re.match(rfc5424_pattern, line, flags=re.I|re.M|re.X)
        try:
            groups = match.groupdict()
        except:
            print(line)
            exit(1)
        
        seq = int(groups['msg'].split(',')[0].split(':')[1].strip())
        msgs_by_seq[seq] = groups
        msgs_by_seq[seq]['timestamp'] = parse(msgs_by_seq[seq]['timestamp'])

sorted_msgs = sorted(msgs_by_seq.items(), key=lambda x: x[0])

missing_counter = 0
date_mismatch_counter = 0
date_cannot_tie_counter = 0
date_tieable_counter = 0

hostname_chain = []

prev_msg = None
for i, (seq, msg) in enumerate(sorted_msgs):
    if i != seq:
        missing_counter += 1

    if prev_msg:
        if prev_msg['timestamp'] > msg['timestamp']:
            date_mismatch_counter += 1
            if prev_msg['hostname'] == msg['hostname'] or msg['hostname'] in hostname_chain:
                date_tieable_counter += 1
            hostname_chain.append(prev_msg['hostname'])
        elif prev_msg['timestamp'] == msg['timestamp']:
            date_cannot_tie_counter += 1
            if prev_msg['hostname'] == msg['hostname'] or msg['hostname'] in hostname_chain:
                date_tieable_counter += 1
            hostname_chain.append(prev_msg['hostname'])
        else:
            hostname_chain = []

    prev_msg = msg

print(f"File {filename} contains {len(sorted_msgs)} messages")
print(f"Summary: {missing_counter} missing message(s), {date_mismatch_counter} date(s) are misplaced, {date_cannot_tie_counter} date(s) ex-aequo (cannot break a tie), {date_tieable_counter} date(s) could be untied using device localtime")