def main():

    # Module imports

    import argparse

    # Argument parser

    parser = argparse.ArgumentParser(
        prog='TelstraCallToCSV',
        description="""A simple Python program to export Telstra call"""
                    """ histories to CSV files.""",
        epilog=("TelstraCallToCSV\n"
                "Copyright (c) 2023 capta1nt0ad.\n"
                "This program comes with ABSOLUTELY NO WARRANTY; for details"
                " type `telstracall --copying`.\n"
                "This is free software, and you are welcome to redistribute it"
                "\nunder the conditions of the GNU General Public License v3."
                )
    )

    parser.add_argument(
        '-c', '--copying',
        help='show the license information',
        action="store_true"
    )

    parser.add_argument(
        '-v', '--version',
        help='show the version information',
        action="store_true"
    )

    parser.add_argument(
        'key',
        help='My Telstra session key',
        nargs="?"
    )

    # parser.add_argument(
    #     'output',
    #     help='location of output file (default: ./out.csv)',
    #     type=argparse.FileType('w'),
    #     default="./out.csv",
    #     nargs='?'
    # )

    args = parser.parse_args()

    if args.copying:
        print("GPLv3 Placeholder")

    if args.version:
        print("TelstraCallToCSV version 2.0dev")

    if args.copying or args.version:
        exit(0)

    if (args.key is None):

        print("TelstraCallToCSV: error: the following arguments "
              "are required: key, correlation-id, output\n")
        parser.print_help()

    else:
        get_parse_json(args.key)


def get_parse_json(key):

    import requests
    import config
    import json
    from datetime import datetime, date
    from dateutil.relativedelta import relativedelta

    today = datetime.now()

    for i in range(6):

        if i == 0:

            start_date = str(today.strftime("%Y")) + str(today.strftime("%m"))

            end_date = str(date(int(today.strftime("%Y")),
                                int(today.strftime("%m")),
                                1) + relativedelta(months=1))
            end_date = end_date.replace("-", "")
            end_date = end_date[:-2]

        else:

            start_date = str(date(int(today.strftime("%Y")),
                                  int(today.strftime("%m")),
                                  1) - relativedelta(months=i))
            start_date = start_date.replace("-", "")
            start_date = start_date[:-2]

            end_date = str(date(int(today.strftime("%Y")),
                                int(today.strftime("%m")),
                                1) - relativedelta(months=i-1))
            end_date = end_date.replace("-", "")
            end_date = end_date[:-2]

        headers = {
            'Authorization': 'Bearer ' + key,
            'correlation-id': "0",
            'source-system': 'MyTelstraWeb',
        }

        params = {
            'paymentType': config.payment_type,
            'accountUuid': config.account_uuid,
            'serviceId': config.phone_number,
            'startDate': start_date + '01',
            'endDate': end_date + '01',
            'usageGroup': 'CALL',
            'pageNumber': '1',
        }

        response = requests.get(
            'https://tapi.telstra.com/presentation/v1/mytelstra-web/'
            'strategic-prepaid/usage-history/itemised',
            params=params,
            headers=headers,
        )

        if response.status_code != 200:
            print(response.status_code)
            exit(76)

        filename = str(start_date) + ".csv"
        print(filename)

        jparser = json.loads(response.text)

        day_no = 0

        write_data = open(filename, "w")
        write_data.write("Entry, Date, Caller, Recipient,"
                         " Time taken, Amount charged")
        while True:
            try:
                write_data.write("\n" + str(day_no + 1) + "," + jparser["data"]
                                 ["strategicUsageHistory"]["usageHistory"]
                                 [day_no]["eventDateAndTime"] + "," +
                                 jparser["data"]
                                 ["strategicUsageHistory"]["serviceId"] + "," +
                                 jparser["data"]
                                 ["strategicUsageHistory"]["usageHistory"]
                                 [day_no]["calledPartyNumber"]
                                 + "," + jparser["data"]
                                 ["strategicUsageHistory"]["usageHistory"]
                                 [day_no]["usageDisplay"]
                                 + "," + jparser["data"]
                                 ["strategicUsageHistory"]["usageHistory"]
                                 [day_no]["chargeAmount"])

                day_no = day_no + 1
            except IndexError:
                break

        write_data.close()

        pages = jparser["data"]["strategicUsageHistory"]["totalPages"]

        if pages != 1:
            for i in range(pages - 1):
                headers = {
                    'Authorization': 'Bearer ' + key,
                    'correlation-id': "0",
                    'source-system': 'MyTelstraWeb',
                }

                params = {
                    'paymentType': config.payment_type,
                    'accountUuid': config.account_uuid,
                    'serviceId': config.phone_number,
                    'startDate': start_date + '01',
                    'endDate': end_date + '01',
                    'usageGroup': 'CALL',
                    'pageNumber': str(i + 2),
                }

                response = requests.get(
                    'https://tapi.telstra.com/presentation/v1/mytelstra-web/'
                    'strategic-prepaid/usage-history/itemised',
                    params=params,
                    headers=headers,
                )

                if response.status_code != 200:
                    print(response.status_code)
                    exit(76)

                jparser = json.loads(response.text)

                day_no = 0

                ext_page_filename = str(start_date)
                + "pg" + str(i + 2) + ".csv"

                print(ext_page_filename)

                append_data = open(ext_page_filename, "w")
                while True:
                    try:
                        append_data.write("\n" + str(day_no + 1) + ","
                                          + jparser["data"]
                                          ["strategicUsageHistory"]
                                          ["usageHistory"]
                                          [day_no]["eventDateAndTime"]
                                          + "," + jparser["data"]
                                          ["strategicUsageHistory"]
                                          ["serviceId"] + "," +
                                          jparser["data"]
                                          ["strategicUsageHistory"]
                                          ["usageHistory"]
                                          [day_no]["calledPartyNumber"]
                                          + "," + jparser["data"]
                                          ["strategicUsageHistory"]
                                          ["usageHistory"]
                                          [day_no]["usageDisplay"]
                                          + "," + jparser["data"]
                                          ["strategicUsageHistory"]
                                          ["usageHistory"]
                                          [day_no]["chargeAmount"])

                        day_no = day_no + 1

                    except IndexError:
                        break

                append_data.close()


if __name__ == "__main__":
    main()
