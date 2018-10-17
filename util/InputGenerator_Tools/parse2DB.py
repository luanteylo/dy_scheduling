import glob, os
import database as db

parse_dir = "/home/luan/google_trace/clusterdata-2011-2/parse/"

instances = []


# def loadInstances():
#     conn = db.create_connection("db.bin")


def parse2DB():
    os.chdir(parse_dir)
    onlyfiles = glob.glob("*.csv")

    conn = db.create_connection("/home/luan/project/phd_project/dy_scheduling/util/InputGenerator_Tools/db.bin")

    with conn:

        for file in onlyfiles:

            print file

            with open(file) as f:
                for line in f.readlines():
                    jobid = line.split(",")[0]                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
                    taskid = line.split(",")[1]
                    memory = line.split(",")[4]
                    runtime = line.split(",")[5]

                    db.insert_task(conn, int(jobid), int(taskid), "t_" + taskid, float(memory), 0.0)



parse2DB()
