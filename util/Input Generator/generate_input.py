import json
import database as db

PATH = "/home/luan/project/static_heuristic/input/"

env_file = "aws.json"
job_file = "job.json"


def get_all_prices(db_file, type, regions):
    dict = {}
    ondemand_prices = {}

    spot_prices = {}

    conn = db.create_connection(db_file)
    with conn:
        # get ondemand price
        for region in regions:
            rows = db.select_instance_price(conn, type, 0, region)
            if len(rows) > 0:
                ondemand_prices[rows[0][2]] = rows[0][4]

        dict["ondemand"] = ondemand_prices

        for region in regions:
            zone_dict = {}
            for zone in regions[region]:
                rows = db.select_instance_price(conn, type, 1, region, zone)
                if len(rows) > 0:
                    zone_dict[zone] = rows[0][4]
            spot_prices[region] = zone_dict

        dict["spot"] = spot_prices
    return dict


def get_instances(db_file, job_id):

    conn = db.create_connection(db_file)

    instances = []

    with conn:
        rows = db.select_all_job_instances(conn, job_id)

        for row in rows:
            instances.append(row[0])

    return instances

# generate env file


def generate_envFile(db_file, job_id, regions):

    instances = get_instances(db_file, job_id)

    instances_dict = {}

    conn = db.create_connection(db_file)

    with conn:

        # get instances associate to a job

        for type in instances:

            row = db.select_instance(conn, type)

            # get all prices

            prices = get_all_prices(db_file, type, regions)

            if len(row) > 0:
                # print row
                instances_dict[row[0][0]] = {"memory": row[0][1], "vcpu": row[0][2], "price": prices}

    with open(PATH + env_file, 'w') as fp:
        json.dump(instances_dict, fp, indent=4, sort_keys=True)

    generate_jobFile(db_file, instances, job_id)


def generate_jobFile(db_file, instances,  job_id):

    tasks_dict = {}

    conn = db.create_connection(db_file)

    with conn:

        rows = db.select_job(conn, job_id)

        for row in rows:
            task_id = row[1]
            name = row[2]
            memory = row[3]
            io_size = row[4]

            # get runtime
            runtime_dict = {}

            for instance in instances:
                runtime = db.select_runtime(conn, job_id, task_id, instance)
                runtime_dict[instance] = runtime

            tasks_dict[name] = {"id": task_id, "memory": memory, "io": io_size, "runtime" : runtime_dict}

    with open(PATH + job_file, 'w') as fp:
        json.dump({"environment": PATH + env_file, "tasks": tasks_dict}, fp, indent=4, sort_keys=True)






# instances = [
#     "c5.large",
#     "m5.large",
#     "m4.large",
#     "c4.large",
#     "c5.xlarge",
#     "m5.xlarge",
#     "m4.xlarge",
#     "c4.xlarge",
#     "c5.2xlarge",
#     "m5.2xlarge",
#     "m4.2xlarge",
#     "c4.2xlarge",
#     "c5.4xlarge",
#     "m5.4xlarge",
#     "m4.4xlarge",
#     "c4.4xlarge",
#     "c5.9xlarge",
#     "c4.8xlarge"]

regions = {"us-east-1": ["us-east-1a"], "us-west-1": ["us-west-1b", "us-west-1c"]}



generate_envFile("db.bin", 41, regions)


# generate_jobFile("db.bin", instances, 41)
