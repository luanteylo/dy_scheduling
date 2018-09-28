from intervaltree import Interval, IntervalTree
import json

path = "/home/luan/Dropbox/UFF - Doutorado/traces/spot_history/by_type/"


SLOT = 60


def load_spot_history(file_name):
    key1 = None
    aux_price = None

    T = IntervalTree()

    with open(path + file_name) as f:
        f.readline()
        for line in f.readlines():
            second = int(float(line.split(",")[1]))
            price = float(line.split(",")[3])

            if key1 is None:  # first line
                key1 = second
                aux_price = price
            else:
                key2 = second

                print key1, key2, second, price
                T[key1:key2] = aux_price

                # update to nex insertion
                key1 = second
                aux_price = price

    return T


class VM:

    def __init__(self, id, type, market, region, zone, price):
        self.id = id
        self.type = type
        self.market = market
        self.region = region
        self.zone = zone
        self.price = price

        self.intervals = IntervalTree()

        self.end_slot = SLOT
        self.cost = price
        self.assigned_tasks = []
        self.exec_tasks = []

        self.hibernate_start = -1

    def print_vm(self):
        print self.id, self.type, self.market, self.region, self.zone, self.price, self.end
        print self.intervals

    def add_interval(self, start, end, task_id):
        self.intervals[start:end] = task_id
        self.assigned_tasks.append(task_id)

    def update(self, period):
        # check if the execution get
        # a new slot of time
        if period == self.end_slot:
            self.end_slot += SLOT
            self.cost += self.price

        self.exec_tasks = []
        interval = self.intervals.search(period)
        for itv in interval:
            self.exec_tasks.append(itv.data)


running = []
finished = []
hibernate = []

backup = dict()

deadline = None


# return a vm
def build_VM(data, vm_id, start_bkp=-1):
    type = data[vm_id]["type"]
    market = data[vm_id]["market"]
    region = data[vm_id]["region"]
    zone = data[vm_id]["zone"]
    price = data[vm_id]["price"]

    vm = VM(vm_id, type, market, region, zone, price)

    map = data[vm_id]["map"]

    for core in map:
        for task_id in map[core]:
            # print map[core]
            start = map[core][task_id]['start']
            end = map[core][task_id]['end']

            if start_bkp != -1:
                start += start_bkp
                end += start_bkp
                vm.end_slot += start_bkp

            # intervals[start:end] = task_id
            vm.add_interval(start, end, task_id)

    return vm


def load_primary(file_name):
    global deadline

    with open(file_name) as f:
        data = json.load(f)

    deadline = int(data["deadline"])

    for vm_id in data["vms"]:
        running.append(build_VM(data["vms"], vm_id))


def load_backup(file_name):
    with open(file_name) as f:
        data = json.load(f)

    # print data
    for head_task in data:

        start_bkp = data[head_task]["start_bkp"]

        for vm_id in data[head_task]["vms"]:
            # print data[head_task]["vms"]
            vm = build_VM(data[head_task]["vms"], vm_id, start_bkp)
            # vm.print_vm()

        backup[head_task] = [start_bkp, vm]


def start_execution(file_primary, file_backup):
    # T = build_intervalTree()

    # load scheduling map

    global backup, deadline
    global running, hibernate, finished

    load_primary(file_primary)
    load_backup(file_backup)

    # History = dict()
    #
    # for vm_type = history_files:
    #     History[vm_type]  = load_spot_history("us-west-1-%s.csv")

    print "\n#\n#\tStart Execution "
    print "#"
    print "#\tPrimary: " + file_primary
    print "#\tBackups: " + file_backup
    print "#\tDeadline: " + str(deadline)
    print "#\n\n"

    deadline_flag = False
    period = 0

    while len(running) > 0 or len(hibernate) > 0:

        print "%d:\t" % (period,)

        # check if the solution
        # has passed the deadline
        if period >= deadline + 1:
            deadline_flag = True
            break

        # Check hibernated VMS
        for vm in hibernate[:]:
            # check if vm return before start_time
            head_task = None
            group_size = 0
            # to each task that was executing at moment of tha fault.
            # He have to define which is the head task
            for ftask in vm.exec_tasks:
                vm_bkp = backup[ftask][1]
                if len(vm_bkp.assigned_tasks) > group_size:
                    group_size = len(vm_bkp.assigned_tasks)
                    head_task = ftask

            start_bkp, vm_bkp = backup[head_task]

            # if vm still hibernated and
            # start_bkp is equal the period
            # then we have to start the recovery procedure
            if start_bkp == period:
                hibernate.remove(vm)
                finished.append(vm)
                running.append(vm_bkp)
                print "\t [%s] RECOVERING (HT: %s, vm_bkp: %s)" % (vm.id, head_task, vm_bkp.id)
                continue

            # check if vm resume
            if vm.id == "1" and period == 150:
                # if vm resume, then we have to update its interval
                size = period - vm.hibernate_start

                vm.end_slot += size

                for it in vm.intervals[:]:
                    start = it.begin
                    end = it.end
                    task_id = it.data

                    if task_id not in vm.exec_tasks:
                        start += size

                    end += size

                    vm.intervals.remove(it)

                    vm.intervals[start: end] = task_id

                hibernate.remove(vm)
                running.append(vm)
                print "\t [%s] RESUMING = Wait Period: %d" % (vm.id, size)
                continue

            print "\t [%s] HIBERNATE" % (vm.id,)

        # check the running VMs
        for vm in running[:]:

            interval = vm.intervals.search(period)

            # if there is no task to be executed in that vm
            # we have to remove it from the running_vms
            # and put in the finished_vms

            if len(interval) == 0:
                running.remove(vm)
                finished.append(vm)
                continue

            # check if there is a fault in that period
            # if true, we have to move the vm to hibernate
            if vm.id == "1" and period == 100:
                running.remove(vm)
                vm.hibernate_start = period
                hibernate.append(vm)
                print "\t [%s] HIBERNATING" % (vm.id,)
                continue

            vm.update(period)
            print "\t [%s] = " % (vm.id,), [id for id in vm.exec_tasks]

        # update period
        period += 1

    print "\n\n"
    if not deadline_flag:
        print "#\tExecution Finished with Success."
    else:
        print "#\tExecution Finished with ERROR: Deadline was not meeting"

    print "#\tFinished Period: ", period - 1
    print "#\tRunning: ", [vm.id for vm in running]
    print "#\tHibernate: ", [vm.id for vm in hibernate]
    print "#\tFinished: ", [vm.id for vm in finished]

    cost = 0.0
    for vm in finished:
        cost += vm.cost
    print "#\tExecution Cost: ", cost


start_execution("job1_primaryMap.json", "job1_backupMap.json")

# load_backup("job1_backupMap.json")
