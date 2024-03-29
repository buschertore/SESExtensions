import os
import sys
import logging



def main(argv):

    if not argv:
        argv = ["https://chromewebstore.google.com/detail/lastpass-free-password-ma/hdokiejnpimakedhajhdlcegeplioahd", "/home/codescan/data/testPermissionsLastPass.json"]

    link = argv[0]
    permissionFileName = argv[1]

    logging.basicConfig(level=logging.INFO)
    os.popen("mkdir temp")
    wgetCommand = f'wget "https://clients2.google.com/service/update2/crx?response=redirect&prodversion=122.0.6261.111&acceptformat=crx2,crx3&x=id%3D{link.split("/")[-1]}%26uc" -q -O extension.crx'
    logging.debug(wgetCommand)
    wgetOuput = os.popen(wgetCommand)
    logging.debug(wgetOuput.read())
    unzipOutput = os.popen("unzip extension.crx -d temp")
    logging.debug(unzipOutput.read())
    mvOutput = os.popen(f"mv temp/manifest.json {permissionFileName}")
    logging.info(mvOutput.read())
    rm1Output = os.popen("rm -r temp")
    logging.info(rm1Output.read())
    rm2Output = os.popen("rm extension.crx")

if __name__ == "__main__":
    main(sys.argv[1:])