Public available env. variable inside iox container: https://developer.cisco.com/docs/iox/#!application-development-concepts/application-development-concepts

ioxclient package yaml rule ordering: https://developer.cisco.com/docs/iox/#!docker-commands/docker-commands

certification requires that the dnsName is the name of the peer in question (here the central server), one can use the ip if no domain registered (requires to rebuilt certs if changes): https://www.rsyslog.com/doc/v7-stable/tutorials/tls.html

When double NAT works
If all you care about is access to the Internet, then a double NAT setup will work out just fine.
Also, a double NAT setup makes the top-level NAT network — the one hosted by your new router — more secure.
That’s because devices in this network are behind two layers of firewalls and NATs. They are also invisible to those connecting to the lower-level NAT, as mentioned above.


Implementation flux:
1er problème, le WAN du routeur est coonnecté à la sortie LAN de la b-box à l'entrée WAN du routeur privé. Gateway network clashes (both on .1 subnet).
2eme problème, b-box n'accèpte pas les ips (meme privé comme 10.x.x.x) si pas dans son pool (192.168.1.2 to 192.168.1.63). normalement cisco routeur NAT avant mais p-e pas ?
