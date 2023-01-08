from sys import argv
import datetime
import socket
import ssl

if __name__ == '__main__':
    #cert = ssl.get_server_certificate((host, '443'))
    #print(cert)

    host =  argv[1]
    ssl_context = ssl.create_default_context()
    ssl_host = ssl_context.wrap_socket(socket.socket(), server_hostname=host)
    ssl_host.connect((host, 443))

    raw_expire_date = ssl_host.getpeercert()['notAfter']
    parsed_expire_date = datetime.datetime.strptime(raw_expire_date, "%b %d %X %Y %Z")
    todays_date = datetime.datetime.now()
    time_left = parsed_expire_date - todays_date

    print("{} SSL certificate expires in {} days.".format(host, time_left.days))
