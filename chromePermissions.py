import os
import sys
import logging



def main(argv):

    if not argv:
        argv = ["https://chromewebstore.google.com/detail/lastpass-free-password-ma/hdokiejnpimakedhajhdlcegeplioahd", "/home/codescan/data/testPermissionsLastPass.json"]

    link = argv[0]
    permissionFileName = argv[1]
    extensionName = permissionFileName.split("/")[-1].strip().removesuffix(".json")

    logging.basicConfig(level=logging.INFO)
    os.popen(f"mkdir temp{extensionName}")
    wgetCommand = f'wget "https://clients2.google.com/service/update2/crx?response=redirect&prodversion=122.0.6261.111&acceptformat=crx2,crx3&x=id%3D{link.split("/")[-1]}%26uc" -q -O {extensionName}.crx'
    logging.debug(wgetCommand)
    wgetOuput = os.popen(wgetCommand)
    logging.debug(wgetOuput.read())
    unzipOutput = os.popen(f"unzip {extensionName}.crx -d temp{extensionName}")
    logging.debug(unzipOutput.read())
    mvOutput = os.popen(f"mv temp{extensionName}/manifest.json {permissionFileName}")
    logging.info(mvOutput.read())
    rm1Output = os.popen(f"rm -r temp{extensionName}")
    logging.info(rm1Output.read())
    rm2Output = os.popen(f"rm {extensionName}.crx")

if __name__ == "__main__":
    main(sys.argv[1:])