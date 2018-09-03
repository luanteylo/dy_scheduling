import getSpotPrices as prices
import database as db


def insert_all_instances():
    # insert all instances on DB
    output = prices.get_ondemand_price()

    conn = db.create_connection("db.bin")
    with conn:
        for region in output:
            for instance in output[region]:
                type = instance[0]
                vcpu = instance[1]
                memory = instance[2]
                price = instance[3]

                db.insert_instance(conn, type, memory, vcpu)


def insert_all_prices():
    output = prices.get_ondemand_price()

    # On - demand prices

    conn = db.create_connection("db.bin")

    with conn:

        # for region in output:
        #     for instance in output[region]:
        #         type = instance[0]
        #         vcpu = instance[1]
        #         memory = instance[2]
        #         price = instance[3]
        #
        #         db.insert_price(conn, type, 0, region, price)

        for region in output.keys():
            zones = prices.get_all_zones(region)
            for instance in output[region]:
                for zone in zones:
                    spot_price = prices.get_spot_price(instance[0], region, zone)
                    type = instance[0]

                    if spot_price is not None:
                        db.insert_price(conn, type, 1, region, spot_price, zone=zone)
                    # db.insert_price(conn, instance[0], 1, region, spot_price, zone)


# insert_all_instances()
insert_all_prices()

# insert_all_instances()


# for region in output.keys():
#     zones = prices.get_all_zones(region)
#     for instance in output[region]:
#         on_demand_price = instance[-1]
#         for zone in zones:
#             spot_price = prices.get_spot_price(instance[0], region, zone)
#
#             print on_demand_price, spot_price, region, zone
