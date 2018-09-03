import getSpotPrices as prices
import database as db


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


