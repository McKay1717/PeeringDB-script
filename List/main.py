import requests
import pyasn
import csv

# Will contain the IXLan_id avaidable for peering
Gitoyen_Factory = []
# Name of the routers, it will be use to check route via looking glass
Gitoyen_router_name = ['whiskey', 'vodka', 'x-ray']

AS_GITOYEN = 20766

# Init usefull object
ses = requests.session()
asndb = pyasn.pyasn('asn.db')

# Base head for the csv
head = ['Name', 'ASN', 'Prefix Exemple', 'Number of V4 Prefix', 'whiskey', 'vodka', 'x-ray']
# Row of the futur CSV
rows = {}

# List Gitoyen Factory with IPv6 avaidable
factory_request = ses.get("https://peeringdb.com//api/netixlan?asn=" + str(AS_GITOYEN))
for factory in factory_request.json()['data']:
    if factory['ipaddr6'] is not None:
        Gitoyen_Factory.append(factory['ixlan_id'])
        head.append(factory['name'])

# For each Factory where Gitoyen is
for factory_id in Gitoyen_Factory:
    # List all ASN in Factory
    IX_Data = ses.get("https://peeringdb.com//api/netixlan?ixlan_id=" + str(factory_id))
    data = IX_Data.json()["data"]
    # For each ASN in current factory
    for object in data:
        #We only dual-stack peer and not on RS servers
        if object['ipaddr6'] is None or object['is_rs_peer']:
            continue
        as_number = object['asn']
        row = {}
        #Look For exiting AS in our list
        if as_number in rows:
            row = rows[as_number]
        #If row not found, populate it else just append info from IX
        if len(row) < 1:
            name = (ses.get("https://peeringdb.com//api/net?asn=" + str(as_number))).json()['data'][0]['name']
            row = {'Name':name, 'ASN': as_number }
            #Search For IPv4 prefix to lookup
            result = asndb.get_as_prefixes(as_number)
            if result is not None and len(result) > 0:
                prefix = result.pop()
                row['Prefix Exemple'] = prefix
                row['Number of V4 Prefix'] = len(result)
                #For each router check if transit by defaut for this dest
                for router in Gitoyen_router_name:
                    route = ses.get('https://lg.gitoyen.net/prefix/' + router + '/ipv4?q=' + str(prefix))
                    for line in route.text.split('\n'):
                        if '<a href="/whois?q=' in line:
                            row[router] = 'X'
                            if '[transit_' in line:
                                #TODO: Use regex
                                row[router] = line.split('[transit_')[1].split(']')[0].split(' ')[0]
                            break
        if 'whiskey' in row and 'vodka' in row and 'x-ray' in row:
            if not(row['whiskey'] == 'X' and row['vodka'] == 'X' and row['x-ray'] == 'X'):
                row[object['name']] = [object['ipaddr4'], object['ipaddr6']]
                rows[as_number] = row
                print(row)

# Prepare a file to write possible peer
with open('gitoyen_peer.csv', mode='w') as peer_csv:
    peer_writer = csv.writer(peer_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    peer_writer.writerow(head)
    for row in rows:
        line = []
        for key in head:
            if key not in rows[row]:
                line.append('')
            else:
                line.append(rows[row][key])
        peer_writer.writerow(line)
    peer_csv.close()
