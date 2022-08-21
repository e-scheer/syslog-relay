import re
from matplotlib import pyplot as plot
import matplotlib.dates as mpl_dates
from dateutil.parser import parse
import datetime
import numpy as np

# Dataset used is available here: https://github.com/logpai/loghub/tree/master/Linux

rfc3164_pattern = "^([A-Za-z]{3}\s+[0-9]{1,2}\s+\d{2}:\d{2}:\d{2})\s+([\S]+)\s+([\S\s]+)"

def plot_bar(name, y, x, ylabel, xlabel):
    plot.clf()
    plot.bar(x, y)
    
    plot.xlabel(xlabel)
    plot.ylabel(ylabel)
    plot.tight_layout()
    plot.savefig(name)

def plot_nbr_messages():
    plot.clf()
    messages_per_date = {}
    prev_date = None
    year = 2004
    with open("Linux.log", encoding="utf8", errors='ignore') as f:
        for line in f.readlines():
            match = re.search(rfc3164_pattern, line)
            groups = match.groups()
            date = parse(groups[0])

            if prev_date and prev_date.month == 12 and prev_date.day == 31 and date.day != 31:
                year += 1

            key = datetime.datetime(year, date.month, date.day)
            if key in messages_per_date:
                messages_per_date[key] += 1
            else:
                messages_per_date[key] = 1

            prev_date = date

    dates = []
    nbr_messages = []
    for k, v in messages_per_date.items():
        dates.append(k)
        nbr_messages.append(v)

    plot.plot_date(dates, nbr_messages, linestyle='solid')
    date_format=mpl_dates.DateFormatter("%b, %d")
    plot.gcf().autofmt_xdate()
    plot.gca().xaxis.set_major_formatter(date_format)
    
    plot.ylabel("Days on which logs were generated")
    plot.ylabel("Number of messages")
    plot.tight_layout()

    plot.savefig("messages_per_day")

def logs_grouped(interval_seconds, print_infos=False):
    lengths = []
    content_lengths = []
    inter_arrivals = []

    msgs_in_groups = [0]
    grp_index = 0
    iat_between_groups = []
    iat_inside_groups = []

    prev_date = None

    with open("Linux.log", encoding="utf8", errors='ignore') as f:
        for line in f.readlines():
            match = re.search(rfc3164_pattern, line)
            groups = match.groups()
            date = parse(groups[0])

            lengths.append(len(line))
            content_lengths.append(len(groups[2]))

            if prev_date:
                seconds = (date - prev_date).seconds
                inter_arrivals.append(seconds)

                # more than an hour inbetween
                if seconds > interval_seconds:     
                    grp_index += 1
                    msgs_in_groups.append(0)
                    iat_between_groups.append(seconds)
                else:
                    iat_inside_groups.append(seconds)

                msgs_in_groups[grp_index] += 1

            prev_date = date

    nbr_groups = len(msgs_in_groups)
    avg_nbr_msg_inside_group = len(lengths) / len(msgs_in_groups)
    avg_iat_between_groups = sum(iat_between_groups) / len(msgs_in_groups)
    avg_iat_inside_group = sum(iat_inside_groups) / len(iat_inside_groups)

    if print_infos:
        print("Timestamp: " + str(interval_seconds) + "s.")
        print("Average length: " + str(sum(lengths) / len(lengths)))
        print("Average content length: " + str(sum(content_lengths) / len(content_lengths)))
        print("Average inter-arrival: " + str(sum(inter_arrivals) / len(inter_arrivals))) 
        print("Number of groups: " + str(nbr_groups))
        print("Average number of logs inside a group: " + str(avg_nbr_msg_inside_group))
        print("Average inter-arrival between groups: " + str(avg_iat_between_groups))
        print("Average inter-arrival inside a group: " + str(avg_iat_inside_group))
    
    return (nbr_groups, avg_nbr_msg_inside_group, avg_iat_between_groups, avg_iat_inside_group)

plot_nbr_messages()

timestamps = [1, 5, 15, 30, 60, 120, 240, 480, 720]
str_timestamps = ["1min", "5min", "15min", "30min", "1h", "2h", "4h", "8h", "12h"]

t_nbr_groups = []
t_avg_nbr_msg_inside_group = []
t_avg_iat_between_groups = []
t_avg_iat_inside_group = []

for minutes in timestamps:
    print("Computing groups with " + str(minutes) + " min(s) in-between")
    (nbr_groups, avg_nbr_msg_inside_group, avg_iat_between_groups, avg_iat_inside_group) = logs_grouped(minutes * 60)
    t_nbr_groups.append(nbr_groups)
    t_avg_nbr_msg_inside_group.append(avg_nbr_msg_inside_group)
    t_avg_iat_between_groups.append(avg_iat_between_groups)
    t_avg_iat_inside_group.append(avg_iat_inside_group)

# creating the bar plot
plot_bar("nbr_groups", t_nbr_groups, str_timestamps, "Number of groups", "Minimum time interval between two consecutive groups")
plot_bar("avg_nbr_msg_inside_group", t_avg_nbr_msg_inside_group, str_timestamps, "Average number of messages inside a group", "Minimum time interval between two consecutive groups")
plot_bar("avg_iat_between_groups", t_avg_iat_between_groups, str_timestamps, "Average inter-arrival between groups", "Minimum time interval between two consecutive groups")
plot_bar("avg_iat_inside_group", t_avg_iat_inside_group, str_timestamps, "Average inter-arrival inside groups", "Minimum time interval between two consecutive groups")

# show infos for 1h
logs_grouped(60 * 60, True)