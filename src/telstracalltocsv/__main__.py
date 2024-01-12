#!/usr/bin/env python

import glob
import os
import json
import sys

from colorama import Fore, Style


def main():
    # Module imports

    import argparse

    # Argument parser

    parser = argparse.ArgumentParser(
        prog="TelstraCallToCSV",
        description="""A simple Python program to export Telstra call"""
        """ histories to CSV files.""",
        epilog=(
            "TelstraCallToCSV\n"
            "Copyright (c) 2023 capta1nt0ad.\n"
            "This program comes with ABSOLUTELY NO WARRANTY; for details"
            " type `telstracall --copying`.\n"
            "This is free software, and you are welcome to redistribute it"
            "\nunder the conditions of the GNU General Public License v3."
        ),
    )

    parser.add_argument(
        "-c", "--copying", help="show the license information", action="store_true"
    )

    parser.add_argument(
        "-v", "--version", help="show the version information", action="store_true"
    )

    parser.add_argument(
        "-C",
        "--clean",
        help="clean all CSV files in the current directory- use with caution!",
        action="store_true",
    )

    parser.add_argument(
        "--configure", help="write/create the configuration file", action="store_true"
    )

    parser.add_argument(
        "-P", "--phone", help="override the default account phone number in the config"
    )

    parser.add_argument(
        "-M",
        "--months",
        help="specify how many months back to download (default: 6, the max)",
        default=6,
    )

    parser.add_argument("key", help="My Telstra session key", nargs="?")

    # parser.add_argument(
    #     'output',
    #     help='location of output file (default: ./out.csv)',
    #     type=argparse.FileType('w'),
    #     default="./out.csv",
    #     nargs='?'
    # )

    args = parser.parse_args()

    if args.copying:
        print("TelstraCallToCSV is licensed under the GNU General Public License version 3 (or later).")
        print("See https://www.gnu.org/licenses/gpl-3.0-standalone.html for more information.")

    if args.version:
        print("TelstraCallToCSV version 2.0.0")

    if args.clean:
        if glob.glob("*.csv") != []:
            print(Fore.BLUE + ":: " + Fore.RESET + "Cleaning up...")
            for files in glob.glob("*.csv"):
                os.remove(files)
            print(Fore.GREEN + ":: " + Fore.RESET + "Finished all jobs.")

        else:
            print(Fore.BLUE + ":: " + Fore.RESET + "Nothing to clean up.")

    if args.configure:
        configurator()

    if args.copying or args.version or args.clean:
        sys.exit(0)

    # Config file

    if not os.path.isfile(os.path.join(os.path.expanduser("~"), ".telstracall")):
        print(
            Fore.RED
            + "TelstraCallToCSV has not been configured."
            + Fore.RESET
        )

        print(
            Fore.YELLOW
            + "HINT: You may be running TelstraCallToCSV for the first time.\n"
            + "HINT: Please run the program with the '--configure' argument.\n"
            + "HINT: For more information, refer to the documentation."
            + Fore.RESET
        )

        print()

        print(Fore.RED + ":: " + Fore.RESET + "Finished all jobs.")
        sys.exit(78)

    else:
        with open(os.path.join(os.path.expanduser("~"), ".telstracall"), "r") as config_file:
            config_content = json.load(config_file)

        config_account_uuid = config_content["account_uuid"]
        config_phone_number = config_content["phone_number"]

    if args.key is None:
        print(
            Fore.RED + "error:" + Fore.RESET + " the following arguments "
            "are required: " + Style.BRIGHT + "key" + Style.RESET_ALL + "\n"
        )
        parser.print_help()

        exit(78)

    if args.phone is None:
        phone = config_phone_number
    else:
        phone = args.phone

    get_parse_json(args.key, phone, config_account_uuid, int(args.months))


def get_parse_json(key, phone, uuid, months):
    print(Fore.BLUE + "\n:: " + Fore.RESET + "Starting export...")

    import requests
    from datetime import datetime, date
    from dateutil.relativedelta import relativedelta

    today = datetime.now()

    for i in range(months):
        if i == 0:
            start_date = str(today.strftime("%Y")) + str(today.strftime("%m"))

            end_date = str(
                date(int(today.strftime("%Y")), int(today.strftime("%m")), 1)
                + relativedelta(months=1)
            )
            end_date = end_date.replace("-", "")
            end_date = end_date[:-2]

        else:
            start_date = str(
                date(int(today.strftime("%Y")), int(today.strftime("%m")), 1)
                - relativedelta(months=i)
            )
            start_date = start_date.replace("-", "")
            start_date = start_date[:-2]

            end_date = str(
                date(int(today.strftime("%Y")), int(today.strftime("%m")), 1)
                - relativedelta(months=i - 1)
            )
            end_date = end_date.replace("-", "")
            end_date = end_date[:-2]

        print(
            "   ("
            + str(i + 1)
            + "/"
            + str(months)
            + ") "
            + Fore.BLUE
            + "🢃 Downloading"
            + Fore.RESET
            + " "
            + str(start_date)
            + "... ",
            end="",
        )

        headers = {
            "Authorization": "Bearer " + key,
            "correlation-id": "0",
            "source-system": "MyTelstraWeb",
        }

        params = {
            "paymentType": "prepaid",
            "accountUuid": uuid,
            "serviceId": phone,
            "startDate": start_date + "01",
            "endDate": end_date + "01",
            "usageGroup": "CALL",
            "pageNumber": "1",
        }

        response = requests.get(
            "https://tapi.telstra.com/presentation/v1/mytelstra-web/"
            "strategic-prepaid/usage-history/itemised",
            params=params,
            headers=headers,
        )

        if response.status_code == 401:
            print(
                Fore.RED
                + "The remote host returned an HTTP error "
                + str(response.status_code)
                + "."
                + Fore.RESET
            )
            print(
                Fore.YELLOW
                + "         HINT: Log in again and double-check your key."
                + Fore.RESET
            )

            print()

            print(Fore.RED + ":: " + Fore.RESET + "Cleaning up...")
            for files in glob.glob("*.csv"):
                os.remove(files)
            print(Fore.RED + ":: " + Fore.RESET + "Finished all jobs.")
            sys.exit(76)

        if response.status_code == 403:
            print(
                Fore.RED
                + "The remote host returned an HTTP error "
                + str(response.status_code)
                + "."
                + Fore.RESET
            )
            print(
                Fore.YELLOW
                + "         HINT: Check the configuration (--configure)."
                + Fore.RESET
            )

            print()

            print(Fore.RED + ":: " + Fore.RESET + "Cleaning up...")
            for files in glob.glob("*.csv"):
                os.remove(files)
            print(Fore.RED + ":: " + Fore.RESET + "Finished all jobs.")
            sys.exit(76)

        elif response.status_code != 200:
            print(
                Fore.RED
                + "The remote host returned an HTTP error "
                + str(response.status_code)
                + "."
                + Fore.RESET
            )

            print(
                Fore.YELLOW
                + "         HINT: We may be being rate limited.\n"
                + "         HINT: Please run the program again.\n"
                + "         HINT: Otherwise, please file a bug report."
                + Fore.RESET
            )

            print()

            print(Fore.RED + ":: " + Fore.RESET + "Cleaning up...")
            for files in glob.glob("*.csv"):
                os.remove(files)
            print(Fore.RED + ":: " + Fore.RESET + "Finished all jobs.")
            sys.exit(76)

        print("Done.")

        filename = str(start_date) + ".csv"

        print(
            "         "
            + Fore.GREEN
            + "🖫 Saving"
            + Fore.RESET
            + " "
            + filename
            + "... ",
            end="",
        )

        jparser = json.loads(response.text)

        day_no = 0

        write_data = open(filename, "w")
        write_data.write(
            "Entry, Date, Caller, Recipient," " Time taken, Amount charged"
        )
        while True:
            try:
                write_data.write(
                    "\n"
                    + str(day_no + 1)
                    + ","
                    + jparser["data"]["strategicUsageHistory"]["usageHistory"][day_no][
                        "eventDateAndTime"
                    ]
                    + ","
                    + jparser["data"]["strategicUsageHistory"]["serviceId"]
                    + ","
                    + jparser["data"]["strategicUsageHistory"]["usageHistory"][day_no][
                        "calledPartyNumber"
                    ]
                    + ","
                    + jparser["data"]["strategicUsageHistory"]["usageHistory"][day_no][
                        "usageDisplay"
                    ]
                    + ","
                    + jparser["data"]["strategicUsageHistory"]["usageHistory"][day_no][
                        "chargeAmount"
                    ]
                )

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
                print(
                    "         "
                    + Fore.CYAN
                    + "🗐 Proccessing page "
                    + str(i + 2)
                    + Fore.RESET
                    + "... ",
                    end="",
                )

                headers = {
                    "Authorization": "Bearer " + key,
                    "correlation-id": "0",
                    "source-system": "MyTelstraWeb",
                }

                params = {
                    "paymentType": "prepaid",
                    "accountUuid": uuid,
                    "serviceId": phone,
                    "startDate": start_date + "01",
                    "endDate": end_date + "01",
                    "usageGroup": "CALL",
                    "pageNumber": str(i + 2),
                }

                response = requests.get(
                    "https://tapi.telstra.com/presentation/v1/mytelstra-web/"
                    "strategic-prepaid/usage-history/itemised",
                    params=params,
                    headers=headers,
                )

                if response.status_code == 401:
                    print(
                        Fore.RED
                        + "The remote host returned an HTTP error "
                        + str(response.status_code)
                        + "."
                        + Fore.RESET
                    )
                    print(
                        Fore.YELLOW + "         HINT: Log in again and "
                        "double-check your key." + Fore.RESET
                    )

                    print()

                    print(Fore.RED + ":: " + Fore.RESET + "Cleaning up...")
                    for files in glob.glob("*.csv"):
                        os.remove(files)
                    print(Fore.RED + ":: " + Fore.RESET + "Finished all jobs.")
                    sys.exit(76)

                if response.status_code == 403:
                    print(
                        Fore.RED
                        + "The remote host returned an HTTP error "
                        + str(response.status_code)
                        + "."
                        + Fore.RESET
                    )
                    print(
                        Fore.YELLOW
                        + "         HINT: Check the configuration (--configure)."
                        + Fore.RESET
                    )

                    print()

                    print(Fore.RED + ":: " + Fore.RESET + "Cleaning up...")
                    for files in glob.glob("*.csv"):
                        os.remove(files)
                    print(Fore.RED + ":: " + Fore.RESET + "Finished all jobs.")
                    sys.exit(76)

                elif response.status_code != 200:
                    print(
                        Fore.RED
                        + "The remote host returned an HTTP error "
                        + str(response.status_code)
                        + "."
                        + Fore.RESET
                    )

                    print(
                        Fore.YELLOW
                        + "         HINT: We may be being rate limited.\n"
                        + "         HINT: Please run the program again.\n"
                        + "         HINT: Otherwise, please file a bug report."
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

                ext_page_filename = str(start_date) + "pg" + str(i + 2) + ".csv"

                write_data = open(ext_page_filename, "w")
                write_data.write(
                    "Entry, Date, Caller, Recipient," " Time taken, Amount charged"
                )

                while True:
                    try:
                        write_data.write(
                            "\n"
                            + str(day_no + 1)
                            + ","
                            + jparser["data"]["strategicUsageHistory"]["usageHistory"][
                                day_no
                            ]["eventDateAndTime"]
                            + ","
                            + jparser["data"]["strategicUsageHistory"]["serviceId"]
                            + ","
                            + jparser["data"]["strategicUsageHistory"]["usageHistory"][
                                day_no
                            ]["calledPartyNumber"]
                            + ","
                            + jparser["data"]["strategicUsageHistory"]["usageHistory"][
                                day_no
                            ]["usageDisplay"]
                            + ","
                            + jparser["data"]["strategicUsageHistory"]["usageHistory"][
                                day_no
                            ]["chargeAmount"]
                        )

                        day_no = day_no + 1

                    except IndexError:
                        break

                write_data.close()

                print("Done.")
                print()


def configurator():
    print(Fore.BLUE + "\n:: " + Fore.RESET + "Please configure TelstraCallToCSV.")
    print("Need help? See the documentation.\n")
    configurator_uuid = input(" > Account UUID: ")
    phone_number = input(" > Phone Number: ")

    configuration = {
        "account_uuid": configurator_uuid,
        "phone_number": phone_number
    }

    with open(os.path.join(os.path.expanduser("~"), ".telstracall"), "w") as config_file:
        json.dump(configuration, config_file)

    print(Fore.GREEN + "\n:: " + Fore.RESET + "Finished all jobs.")
    exit(0)


if __name__ == "__main__":
    try:
        main()
        print(Fore.GREEN + "\n:: " + Fore.RESET + "Finished all jobs.")

    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n\n:: " + Fore.RESET + "Aborted. Cleaning up...")
        for files in glob.glob("*.csv"):
            os.remove(files)
        print(Fore.GREEN + ":: " + Fore.RESET + "Finished all jobs.")
