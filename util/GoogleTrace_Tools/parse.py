import glob, os
from intervaltree import Interval, IntervalTree

jobEvents_dir = "/home/luan/google-clusterdata/clusterdata-2011-2/job_events/"
taskEvents_dir = "/home/luan/google-clusterdata/clusterdata-2011-2/task_events/"
taskUsage_dir = "/home/luan/google-clusterdata/clusterdata-2011-2/task_usage/"

parse_dir = "/home/luan/google-clusterdata/clusterdata-2011-2/parse/"

print "#\t"
print "#\tGoogleTrace_Parse tool 1.0 "
print "#\t"

jobs_scheduling = dict()
jobs_finished = dict()

tasks = dict()

usage = dict()


# jobInterval = IntervalTree()


def load_job():
    os.chdir(jobEvents_dir)
    onlyfiles = glob.glob("*.csv")

    onlyfiles.sort()
    print "#\tLoading job_events ..."
    for file_name in onlyfiles:
        # print file
        with open(jobEvents_dir + file_name) as f:
            for line in f.readlines():
                timestamp = line.split(",")[0]
                jobid = line.split(",")[2]
                event_id = line.split(",")[3]
                jobname = line.split(",")[6]

                # filter events.
                # Just scheduling and finished events will be selected

                if jobname != "az6deRYpwSer9flVi+rwI3joMXbJMAm5FkkxjRsvKWc=":
                    if event_id == "1" and timestamp != "0":
                        if jobid in jobs_scheduling:
                            print "error...", jobid, jobname
                            continue
                        jobs_scheduling[jobid] = [timestamp, jobname]
                    elif event_id == "4" and timestamp != "0":
                        if jobid in jobs_finished:
                            print "error...", jobid, jobname
                            continue
                        jobs_finished[jobid] = [timestamp, jobname]

                    # # load interval
                    # if jobid in jobs_scheduling and jobid in jobs_finished:
                    #     startInt = int(jobs_scheduling[jobid][0])
                    #     endInt = int(jobs_finished[jobid][0])
                    #
                    #     jobInterval[startInt:endInt] = jobid


def parse_job():
    load_job()
    print "#\tWriting job parse ..."

    output = "jobname, jobid, timestamp1, timestamp2, runtime\n"

    max = 0
    min = -1

    for jobid in jobs_scheduling:
        if jobid in jobs_finished:

            jobname1 = jobs_scheduling[jobid][1]
            jobname2 = jobs_finished[jobid][1]

            if jobname1 != jobname2:
                print "jobname error", jobname1, jobname2

            timestamp1 = jobs_scheduling[jobid][0]
            timestamp2 = jobs_finished[jobid][0]

            runtime = (int(timestamp2) - int(timestamp1)) / 1000.0

            hours = (runtime / 60.0) / 60.0

            output += jobname1 + "," + jobid + "," + timestamp1 + "," + timestamp2 + "," + str(runtime) + "\n"

            if max < hours:
                max = hours
            if min == -1 or min > hours:
                min = hours

    print "#\t\tmax(hr):", max
    print "#\t\tmin(hr):", min

    with open(parse_dir + "jobs_parse.csv", "w") as f:
        f.write(output)


def load_tasks():
    os.chdir(taskEvents_dir)
    onlyfiles = glob.glob("*.csv")

    onlyfiles.sort()

    print "#\tLoading task_events ..."

    for file in onlyfiles:
        print "#\t\t", file, "... reading"

        if file == "part-00011-of-00500.csv":
            break

        with open(file) as f:
            for line in f.readlines():
                timestamp = line.split(",")[0]
                jobid = line.split(",")[2]
                taskIndex = int(line.split(",")[3])
                event = line.split(",")[5]
                cpuRequest = line.split(",")[9]
                memoryRequest = line.split(",")[10]

                if timestamp != "0" and (event == "1" or event == "4"):

                    if jobid not in tasks:
                        tasks[jobid] = [dict(), dict()]

                    if event == "1":

                        if taskIndex not in tasks[jobid][0]:
                            tasks[jobid][0][taskIndex] = [timestamp, cpuRequest, memoryRequest]
                    elif event == "4":

                        if taskIndex not in tasks[jobid][1]:
                            tasks[jobid][1][taskIndex] = [timestamp, cpuRequest, memoryRequest]


def parse_task():
    load_tasks()

    print "#\tWriting task parse ..."

    # head = "job id, taskindex, timestamp1, timestamp2, cpu1, cpu2, memory1, memory2, runtime \n"
    #
    # with open(parse_dir + "task_parse.csv", "w") as f:
    #     f.write(head)

    # with open(parse_dir + "task_parse.csv", "w") as f:

    for jobid in tasks:

        start_dict = tasks[jobid][0]
        finish_dict = tasks[jobid][1]

        hadTasks = False
        line = ""

        for task_id in sorted([k for k in start_dict]):

            if task_id in finish_dict:

                timestamp1 = start_dict[task_id][0]
                timestamp2 = finish_dict[task_id][0]

                memory = float(start_dict[task_id][2]) * 128

                runtime = (int(timestamp2) - int(timestamp1)) / 1000.0

                if runtime < 0:
                    print  runtime
                    hadTasks = False
                    break

                line += jobid + "," + str(task_id) + "," + timestamp1 + "," + timestamp2 + "," + str(memory) + "," + str(
                    runtime) + "\n"

                hadTasks = True

        if hadTasks and len(line.split("\n")) > 10:
            with open(parse_dir + jobid + ".csv", "w") as f:
                f.write(line)


parse_task()