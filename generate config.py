import requests

GITOYEN_ASN = 20766
PEER_ASN_LIST = [20940,
                 26496,
                 714,
                 13768,
                 8359,
                 2119,
                 36236,
                 36692,
                 14340,
                 2635,
                 19679,
                 6507,
                 3265,
                 14413,
                 36459,
                 25459,
                 39386,
                 29686,
                 55818,
                 3262,
                 42459,
                 7500,
                 200020
                 ]

gitoyen_peering_factory = []

ses = requests.session()

# List Gitoyen Factory with IPv6 avaidable
factory_request = ses.get("https://peeringdb.com//api/netixlan?asn=" + str(GITOYEN_ASN))
for factory in factory_request.json()['data']:
    if factory['ipaddr6'] is not None:
        gitoyen_peering_factory.append(factory)

with open("template", "r") as template:
    template_lines = template.readlines()
    template.close()
    for factory in gitoyen_peering_factory:
        name = (str(factory['name'])).split(' ')[0].lower()
        print("Generation en cours pour " + name)
        with open("bird/" + name + '.conf', "a") as ix4:
            with open("bird6/" + name + '.conf', "a") as ix6:
                for asn in PEER_ASN_LIST:
                    info_request = ses.get(
                        "https://peeringdb.com/api/netixlan?asn=" + str(asn) + "&ix_id=" + str(factory['ix_id']))
                    result = info_request.json()['data']
                    name_request = ses.get('https://peeringdb.com/api/net?asn=' + str(asn))
                    asn_name = name_request.json()['data'][0]['name']
                    for routeur in result:
                        ipv4 = routeur['ipaddr4']
                        ipv6 = routeur['ipaddr6']
                        for lines in template_lines:
                            line = lines.replace("%IX_NAME%", name)
                            line = line.replace("%ASN%", str(asn))
                            line = line.replace("%PEER_NAME%", str(asn_name))
                            if '%ROUTER_IP%' in lines:
                                linesv4 = line.replace('%ROUTER_IP%', str(ipv4))
                                if ipv4 is not None:
                                    ix4.write(linesv4)
                                    print(
                                        "Generation de la config IPV4 à " + name + " pour le routeur " + ipv4 + " de l'AS" + str(
                                            asn) + " " + asn_name)
                                linesv6 = line.replace('%ROUTER_IP%', str(ipv6))
                                if ipv6 is not None:
                                    ix6.write(linesv6)
                                    print(
                                        "Generation de la config IPV6 à " + name + " pour le routeur " + ipv6 + " de l'AS" + str(
                                            asn) + " " + asn_name)
                            else:
                                if ipv4 is not None:
                                    ix4.write(line)
                                if ipv6 is not None:
                                    ix6.write(line)
                ix6.close()
                ix4.close()
