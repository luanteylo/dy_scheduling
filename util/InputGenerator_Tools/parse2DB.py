import glob, os
import database as db

parse_dir = "/home/luan/google-clusterdata/clusterdata-2011-2/parse/"




def parse2DB():
    os.chdir(parse_dir)
    onlyfiles = glob.glob("*.csv")

    for file in onlyfiles:

        conn = db.create_connection("db.bin")

        with open(file) as f:
            print file
            for line in f.readlines():
                jobid = line.split(",")[0]
                taskid = line.split(",")[1]
                memory = line.split(",")[4]
                runtime = line.split(",")[5]

                db.insert_task(conn, job_id, taskid)




parse2DB()