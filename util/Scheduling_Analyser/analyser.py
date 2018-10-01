from intervaltree import Interval, IntervalTree
import json

path = "/home/luan/Dropbox/UFF - Doutorado/traces/spot_history/by_type/"

SLOT = 60
THRESHOLD = 0.01974


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

                # print key1, key2, second, price
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

        self.allocated = False

    def print_vm(self):
        print self.id, self.type, self.market, self.region, self.zone, self.price, self.end
        print self.intervals

    def add_interval(self, start, end, task_id):
        self.intervals[start:end] = task_id
        self.assigned_tasks.append(task_id)

        # put in exec_tasks tasks that will
        # execute at period start
        self.exec_tasks = []
        interval = self.intervals.search(start)
        for itv in interval:
            self.exec_tasks.append(itv.data)

    def update(self, period):
        # check if the execution get
        # a new slot of time
        if period >= self.end_slot:
            self.end_slot += SLOT
            self.cost += self.price

        # put in exec_tasks tasks
        #  that are executing at that period
        self.exec_tasks = []
        interval = self.intervals.search(period)
        for itv in interval:
            self.exec_tasks.append(itv.data)

        self.allocated = True


running = []
finished = []
hibernate = []

vm_type = []

backup = dict()

deadline = None


# return a vm
def build_VM(data, vm_id, start_bkp=-1):
    type = data[vm_id]["type"]
    market = data[vm_id]["market"]
    region = data[vm_id]["region"]
    zone = data[vm_id]["zone"]
    price = data[vm_id]["price"]

    if market == "spot" and type not in vm_type:
        vm_type.append(type)

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
            # intervals[start:end] = task_id
            vm.add_interval(start, end, task_id)

    if start_bkp != -1:
        vm.end_slot += start_bkp

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

    global backup, deadline, vm_type
    global running, hibernate, finished

    load_primary(file_primary)
    load_backup(file_backup)

    history = dict()

    for type in vm_type:
        print "\n#\t Loading Spot History instance [%s] ... \n" % (type,)
        history[type] = load_spot_history("us-west-1-%s.csv" % (type,))

    print "\n#\n#\tStart Execution "
    print "#"
    print "#\tPrimary: " + file_primary
    print "#\tBackups: " + file_backup
    print "#\tDeadline: " + str(deadline)
    print "#\n\n"

    deadline_flag = False
    period = 0

    number_hibernation = 0
    number_recovery = 0
    number_resume = 0

    while len(running) > 0 or len(hibernate) > 0:

        print "%d: [%f]\t" % (period, history["c4.large"].search(period).pop().data)

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

                number_recovery += 1
                print "\t [%s] RECOVERING (HT: %s, vm_bkp: %s)" % (vm.id, head_task, vm_bkp.id)
                continue

            # check if vm have to be resumed
            if history[vm.type].search(period).pop().data < THRESHOLD:
                # if vm resume, then we have to update its interval
                size = period - vm.hibernate_start

                vm.end_slot += size

                for it in vm.intervals[:]:
                    start = it.begin
                    end = it.end
                    task_id = it.data

                    if task_id not in vm.exec_tasks or vm.allocated is False:
                        start += size

                    end += size

                    vm.intervals.remove(it)

                    vm.intervals[start: end] = task_id

                hibernate.remove(vm)
                running.append(vm)

                number_resume += 1
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
            if vm.market == "spot" and history[vm.type].search(period).pop().data > THRESHOLD:
                running.remove(vm)
                vm.hibernate_start = period
                hibernate.append(vm)

                number_hibernation += 1
                print "\t [%s] HIBERNATING" % (vm.id,)
                continue

            vm.update(period)
            print "\t [%s] = " % (vm.id,), [id for id in vm.exec_tasks]

        # update period
        period += 1

    print "\n\n"
    if not deadline_flag:
        print "#\tExecution Finished with Success at Period ", period -1
    else:
        print "#\tExecution Finished with ERROR at Period ", period -1
    print "#\tHibernation:", number_hibernation, "\tResume:", number_resume, "\tRecovery:", number_recovery
    print "#\tRunning: ", [vm.id for vm in running]
    print "#\tHibernate: ", [vm.id for vm in hibernate]
    print "#\tFinished: ", [vm.id for vm in finished]

    # compute the execution cos
    cost = 0.0
    # if the is in the finished list and it was allocated,
    # then we add its cost
    for vm in finished:
        if vm.allocated is True:
            # print vm.id, vm.market, vm.cost
            cost += vm.cost
    print "#\tExecution Cost: ", cost


start_execution("job1_primaryMap.json", "job1_backupMap.json")

# load_backup("job1_backupMap.json")
