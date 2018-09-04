import getSpotPrices as prices
import database as db

from random import uniform
from random import randint

import math


def insert_all_instances(db_file):
    # insert all instances on DB
    output = prices.get_ondemand_price()

    conn = db.create_connection(db_file)
    with conn:
        for region in output:
            for instance in output[region]:
                type = instance[0]
                vcpu = instance[1]
                memory = instance[2]
                price = instance[3]

                db.insert_instance(conn, type, memory, vcpu)


def insert_all_prices(db_file):
    output = prices.get_ondemand_price()

    # On - demand prices

    conn = db.create_connection(db_file)

    with conn:

        for region in output:
            for instance in output[region]:
                type = instance[0]
                vcpu = instance[1]
                memory = instance[2]
                price = instance[3]

                db.insert_price(conn, type, 0, region, price)

        for region in output.keys():
            zones = prices.get_all_zones(region)
            for instance in output[region]:
                for zone in zones:
                    spot_price = prices.get_spot_price(instance[0], region, zone)
                    type = instance[0]

                    if spot_price is not None:
                        db.update_price(conn, type, 1, region, 0.0, zone)
                        exit()
                        # db.insert_price(conn, type, 1, region, spot_price, zone=zone)
                    # db.insert_price(conn, instance[0], 1, region, spot_price, zone)


def insert_random_tasks(db_file, min_memory, max_memory, min_io, max_io, number_tasks):
    conn = db.create_connection(db_file)

    with conn:

        job_id = randint(1, 100)
        while len(db.select_job(conn, job_id)):
            job_id = randint(1, 100)

        for i in range(number_tasks):
            task_id = i
            task_name = "t" + str(job_id) + "_" + str(i)
            memory = round(uniform(min_memory, max_memory), 2)
            io_size = round(uniform(min_io, max_io), 2)
            db.insert_task(conn, job_id, task_id, task_name, memory, io_size)


def insert_random_execution(db_file, min_time, max_time, instances_type, job_id):
    # CREATE TABLE executed(job_id INT NOT NULL, task_id INT NOT NULL, run_id INTEGER  NOT NULL, runtime FLOAT NOT NULL, instance_type TEXT NOT NULL,
    # PRIMARY KEY(job_id, task_id, run_id), FOREIGN KEY(instance_type) REFERENCES instances(type));

    conn = db.create_connection(db_file)
    with conn:
        rows = db.select_job(conn, job_id)
        if len(rows) > 0:

            run_id = randint(1, 100)
            while len(db.select_execution(conn, run_id)):
                run_id = randint(1, 100)

            for row in rows:
                task_id = row[1]
                base_time = round(uniform(min_time, max_time), 2)
                ftr = 0.0
                for type in instances_type:
                    # define task runtime
                    runtime = math.ceil(ftr * base_time + base_time)
                    db.insert_execution(conn, job_id, task_id, run_id, type, runtime)
                    ftr += 0.1

        else:
            print "Job " + str(job_id) + " don't exist"


def update_all_spot_prices(db_file):
    output = prices.get_ondemand_price()
    conn = db.create_connection(db_file)

    with conn:

        for region in output:
            for instance in output[region]:
                type = instance[0]
                vcpu = instance[1]
                memory = instance[2]
                price = instance[3]

                db.update_price(conn, type, 0, region, price)

        for region in output.keys():
            zones = prices.get_all_zones(region)
            for instance in output[region]:
                for zone in zones:
                    spot_price = prices.get_spot_price(instance[0], region, zone)
                    type = instance[0]

                    if spot_price is not None:
                        db.update_price(conn, type, 1, region, spot_price, zone)
                    # db.insert_price(conn, instance[0], 1, region, spot_price, zone)


instances = [
    "c5.large",
    "m5.large",
    "m4.large",
    "c4.large",
    "c5.xlarge",
    "m5.xlarge",
    "m4.xlarge",
    "c4.xlarge",
    "c5.2xlarge",
    "m5.2xlarge",
    "m4.2xlarge",
    "c4.2xlarge",
    "c5.4xlarge",
    "m5.4xlarge",
    "m4.4xlarge",
    "c4.4xlarge",
    "c5.9xlarge",
    "c4.8xlarge"]


insert_random_execution("db.bin", 1, 60, instances, 41)