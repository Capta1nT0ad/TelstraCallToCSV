import json

day_no = 0

read_data = open("data.json", "r")
json_data = read_data.read()
read_data.close()

json_parse_data = json.loads(json_data)

print("Data for", json_parse_data["data"]["strategicUsageHistory"]["serviceType"], json_parse_data["data"]["strategicUsageHistory"]["paymentType"], "plan with phone number", json_parse_data["data"]["strategicUsageHistory"]["serviceId"])
while True:
    try:
        print("\nEntry", day_no + 1)
        print("Date:", json_parse_data["data"]["strategicUsageHistory"]["usageHistory"][day_no]["eventDateAndTime"])
        print("Caller and Recipient:", json_parse_data["data"]["strategicUsageHistory"]["serviceId"], "to", json_parse_data["data"]["strategicUsageHistory"]["usageHistory"][day_no]["calledPartyNumber"])
        print("Time taken:", json_parse_data["data"]["strategicUsageHistory"]["usageHistory"][day_no]["usageDisplay"])
        print("Amount charged:", json_parse_data["data"]["strategicUsageHistory"]["usageHistory"][day_no]["chargeAmount"])
        day_no = day_no + 1
    except IndexError:
        break
day_no = 0
write_data = open("out.csv", "a")
write_data.write("Entry, Date, Caller, Recipient, Time taken, Amount charged")
while True:
    try:
        write_data.write("\n" + str(day_no + 1) + "," + json_parse_data["data"]["strategicUsageHistory"]["usageHistory"][day_no]["eventDateAndTime"] + "," + json_parse_data["data"]["strategicUsageHistory"]["serviceId"] + "," + json_parse_data["data"]["strategicUsageHistory"]["usageHistory"][day_no]["calledPartyNumber"] + "," + json_parse_data["data"]["strategicUsageHistory"]["usageHistory"][day_no]["usageDisplay"] + "," + json_parse_data["data"]["strategicUsageHistory"]["usageHistory"][day_no]["chargeAmount"])

        day_no = day_no + 1
    except IndexError:
        exit(0)
write_data.close()
read_data
