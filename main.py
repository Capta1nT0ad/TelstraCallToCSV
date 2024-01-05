#!/bin/python3

import config
import glob
import os
import sys

from colorama import Fore, Style


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
        '-C', '--clean',
        help='clean all CSV files in the current directory- use with caution!',
        action="store_true"
    )

    parser.add_argument(
        '-P', '--phone',
        help='override the default account phone number in config.py'
    )

    parser.add_argument(
        '-M', '--months',
        help='specify how many months back to download (default: 6, the max)',
        default=6
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

    if args.clean:

        if glob.glob("*.csv") != []:
            print(Fore.BLUE + ":: " + Fore.RESET + "Cleaning up...")
            for files in glob.glob("*.csv"):
                os.remove(files)
            print(Fore.GREEN + ":: " + Fore.RESET + "Finished all jobs.")

        else:
            print(Fore.BLUE + ":: " + Fore.RESET + "Nothing to clean up.")

    if args.copying or args.version or args.clean:
        sys.exit(0)

    if (args.key is None):

        print(Fore.RED + "error:" + Fore.RESET + " the following arguments "
              "are required: " + Style.BRIGHT + "key" + Style.RESET_ALL + "\n")
        parser.print_help()

    else:

        try:
            if config.payment_type is None or config.account_uuid is None:
                print("Please configure TelstraCallToCSV in 'config.py':")
                print("payment_type = string    # payment type, e.g. prepaid")
                print("account_uuid = string    # the account UUID, see docs.")
                print("phone_number = string    # phone number to use.")
                sys.exit(78)
            if args.phone is None:
                int(config.phone_number)
                phone = config.phone_number
            else:
                phone = args.phone
        except Exception:
            print("Please configure TelstraCallToCSV in 'config.py':")
            print("payment_type = string    # payment type, e.g. prepaid")
            print("account_uuid = string    # the account UUID, see docs.")
            print("phone_number = string    # phone number to use.")
            sys.exit(78)

        get_parse_json(args.key, phone, int(args.months))


def get_parse_json(key, phone, months):

    print(Fore.BLUE + "\n:: " + Fore.RESET + "Starting export...")

    import requests
    import json
    from datetime import datetime, date
    from dateutil.relativedelta import relativedelta

    today = datetime.now()

    for i in range(months):

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

        print("   (" + str(i + 1) + "/" + str(months) +
              ") " + Fore.BLUE + "🢃 Downloading" + Fore.RESET + " " +
              str(start_date) + "... ", end="")

        headers = {
            'Authorization': 'Bearer ' + key,
            'correlation-id': "0",
            'source-system': 'MyTelstraWeb',
        }

        params = {
            'paymentType': config.payment_type,
            'accountUuid': config.account_uuid,
            'serviceId': phone,
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

        if response.status_code == 401:
            print(Fore.RED + "The remote host returned an HTTP error "
                  + str(response.status_code) + "." + Fore.RESET)
            print(Fore.YELLOW +
                  "         HINT: Log in again and double-check your key." +
                  Fore.RESET
                  )

            print()

            print(Fore.RED + ":: " + Fore.RESET + "Cleaning up...")
            for files in glob.glob("*.csv"):
                os.remove(files)
            print(Fore.RED + ":: " + Fore.RESET + "Finished all jobs.")
            sys.exit(76)

        if response.status_code == 403:
            print(Fore.RED + "The remote host returned an HTTP error "
                  + str(response.status_code) + "." + Fore.RESET)
            print(Fore.YELLOW +
                  "         HINT: Check that config.py is correct." +
                  Fore.RESET
                  )

            print()

            print(Fore.RED + ":: " + Fore.RESET + "Cleaning up...")
            for files in glob.glob("*.csv"):
                os.remove(files)
            print(Fore.RED + ":: " + Fore.RESET + "Finished all jobs.")
            sys.exit(76)

        elif response.status_code != 200:
            print(Fore.RED + "The remote host returned an HTTP error "
                  + str(response.status_code) + "." + Fore.RESET)

            print(Fore.YELLOW +
                  "         HINT: We may be being rate limited.\n" +
                  "         HINT: Please run the program again.\n" +
                  "         HINT: Otherwise, please file a bug report." +
                  Fore.RESET
                  )

            print()

            print(Fore.RED + ":: " + Fore.RESET + "Cleaning up...")
            for files in glob.glob("*.csv"):
                os.remove(files)
            print(Fore.RED + ":: " + Fore.RESET + "Finished all jobs.")
            sys.exit(76)

        print("Done.")

        filename = str(start_date) + ".csv"

        print("         " + Fore.GREEN + "🖫 Saving" +
              Fore.RESET + " " + filename + "... ", end="")

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

        print(" Done.")

        pages = jparser["data"]["strategicUsageHistory"]["totalPages"]

        if pages == 1:
            print()

        else:

            for i in range(pages - 1):

                print("         " + Fore.CYAN + "🗐 Proccessing page " +
                      str(i+2) + Fore.RESET + "... ", end="")

                headers = {
                    'Authorization': 'Bearer ' + key,
                    'correlation-id': "0",
                    'source-system': 'MyTelstraWeb',
                }

                params = {
                    'paymentType': config.payment_type,
                    'accountUuid': config.account_uuid,
                    'serviceId': phone,
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

                if response.status_code == 401:
                    print(Fore.RED + "The remote host returned an HTTP error "
                          + str(response.status_code) + "." + Fore.RESET)
                    print(Fore.YELLOW +
                          "         HINT: Log in again and "
                          "double-check your key." +
                          Fore.RESET
                          )

                    print()

                    print(Fore.RED + ":: " + Fore.RESET + "Cleaning up...")
                    for files in glob.glob("*.csv"):
                        os.remove(files)
                    print(Fore.RED + ":: " + Fore.RESET + "Finished all jobs.")
                    sys.exit(76)

                if response.status_code == 403:
                    print(Fore.RED + "The remote host returned an HTTP error "
                          + str(response.status_code) + "." + Fore.RESET)
                    print(Fore.YELLOW +
                          "         HINT: Check that config.py is correct." +
                          Fore.RESET
                          )

                    print()

                    print(Fore.RED + ":: " + Fore.RESET + "Cleaning up...")
                    for files in glob.glob("*.csv"):
                        os.remove(files)
                    print(Fore.RED + ":: " + Fore.RESET + "Finished all jobs.")
                    sys.exit(76)

                elif response.status_code != 200:
                    print(Fore.RED + "The remote host returned an HTTP error "
                          + str(response.status_code) + "." + Fore.RESET)

                    print(Fore.YELLOW +
                          "         HINT: We may be being rate limited.\n" +
                          "         HINT: Please run the program again.\n" +
                          "         HINT: Otherwise, please file a bug report."
                          + Fore.RESET
                          )

                    print()

                    print(Fore.RED + ":: " + Fore.RESET + "Cleaning up...")
                    for files in glob.glob("*.csv"):
                        os.remove(files)
                    print(Fore.RED + ":: " + Fore.RESET + "Finished all jobs.")
                    sys.exit(76)

                jparser = json.loads(response.text)

                day_no = 0

                ext_page_filename = str(start_date) + "pg" + str(i+2) + ".csv"

                write_data = open(ext_page_filename, "w")
                write_data.write("Entry, Date, Caller, Recipient,"
                                 " Time taken, Amount charged")

                while True:
                    try:
                        write_data.write("\n" + str(day_no + 1) + ","
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

                write_data.close()

                print("Done.")
                print()


if __name__ == "__main__":

    try:
        main()
        print(Fore.GREEN + "\n:: " + Fore.RESET + "Finished all jobs.")

    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n\n:: " + Fore.RESET + "Aborted. Cleaning up...")
        for files in glob.glob("*.csv"):
            os.remove(files)
        print(Fore.GREEN + ":: " + Fore.RESET + "Finished all jobs.")
