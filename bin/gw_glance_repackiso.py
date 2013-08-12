#!/usr/bin/python
import shutil, tempfile, os, optparse, logging

usage = "usage: %prog [options]"
parser = optparse.OptionParser(usage=usage)
parser.add_option("-i", "--isofile", help="ISO image", dest="isoimg")
parser.add_option("-d", "--domainid", help="Domain id ", dest="domainid")
parser.add_option("-n", "--gwname", help="GW name", dest="gwname")
parser.add_option("-m", "--primgmtip", help="Primary Management Ip address", dest="primgmtip")
parser.add_option("-o", "--secmgmtip", help="Secondary Management Ip address", dest="secmgmtip")
parser.add_option("-s", "--mgmtsubnet", help="Management Subnet", dest="mgmtsubnet")
parser.add_option("-g", "--gateway", help="Management gateway", dest="mgmtgateway")
parser.add_option("-p", "--password", help="Admin account password", dest="adminpasswd")
parser.add_option("-r", "--gwrole", help="GW Role, primary ,secondary or standalone", dest="gwrole")
parser.add_option("-v", "--vsmip", help="VSM IP", dest="vsmip")
parser.add_option("-a", "--vsmprimac", help="VSM Primary Mac", dest="vsmprimac")
parser.add_option("-u", "--vsmstdbymac", help="VSM standby mac", dest="vsmstdbymac")
parser.add_option("-c", "--uplinkppname", help="Uplink PortProfile name", dest="uplinkppname")
parser.add_option("-e", "--vsmencapppname", help="VSM encapsulated port profile name", dest="vsmencapppname")
parser.add_option("-f", "--file", help="Repackaged file", dest="repackediso")
(options, args) = parser.parse_args()

isoimg = options.isoimg
domainid = int(options.domainid)
gwname = options.gwname
primgmtip = options.primgmtip
secmgmtip = options.secmgmtip
mgmtsubnet = options.mgmtsubnet
mgmtgateway = options.mgmtgateway
adminpasswd = options.adminpasswd
gwrole = options.gwrole
vsmip = options.vsmip
vsmprimac = options.vsmprimac
vsmstdbymac = options.vsmstdbymac
uplinkppname = options.uplinkppname
vsmencapppname = options.vsmencapppname
repackediso = options.repackediso


class Command(object):
   """Run a command and capture it's output string, error string and exit status"""
   def __init__(self, command):
       self.command = command

   def run(self, shell=True):
       import subprocess as sp
       process = sp.Popen(self.command, shell = shell, stdout = sp.PIPE, stderr = sp.PIPE)
       self.pid = process.pid
       self.output, self.error = process.communicate()
       self.failed = process.returncode
       return self

   @property
   def returncode(self):
       return self.failed

def createOvfEnvXmlFile(domain, gateway, hostname, primary_ip, sec_ip, subnet, password, gw_mode, vsm_ip, vsm_p_mac, vsm_s_mac, uplink_pp, vsm_pp):
        #TODO: write a proper xml
        ovf_f = tempfile.NamedTemporaryFile(delete=False)

        st = '<?xml version="1.0" encoding="UTF-8"?> \n'
        st += '<Environment \n'
        st += 'xmlns="http://schemas.dmtf.org/ovf/environment/1" \n'
        st += 'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" \n'
        st += 'xmlns:oe="http://schemas.dmtf.org/ovf/environment/1" \n'
        st += 'xmlns:ve="http://www.vmware.com/schema/ovfenv" \n'
        st += 'oe:id=""> \n'
        st += '<PlatformSection> \n'
        st += '<Kind>CPPA</Kind> \n'
        st += '<Version></Version> \n'
        st += '<Vendor>Cisco Systems, Inc.</Vendor> \n'
        st += '<Locale>en</Locale> \n'
        st += '</PlatformSection> \n'
        st += '<PropertySection> \n'
        st += '<Property oe:key="DomainId" oe:value="%s" /> \n' % (domain)
        st += '<Property oe:key="EnableTelnet" oe:value="True" /> \n'
        st += '<Property oe:key="PriMgmtIpV4" oe:value="%s" /> \n' % (primary_ip)
        st += '<Property oe:key="PriMgmtIpV4Subnet" oe:value="%s" /> \n' % (subnet)
        st += '<Property oe:key="PriGatewayIpV4" oe:value="%s" /> \n' % (gateway)
        st += '<Property oe:key="SecMgmtIpV4" oe:value="%s" /> \n' % (sec_ip)
        st += '<Property oe:key="SecMgmtIpV4Subnet" oe:value="%s" /> \n' % (subnet)
        st += '<Property oe:key="SecGatewayIpV4" oe:value="%s" /> \n' % (gateway)
        st += '<Property oe:key="HostName" oe:value="%s" /> \n' % (hostname)
        st += '<Property oe:key="Password" oe:value="%s" /> \n' % (password)
        st += '<Property oe:key="HARole" oe:value="%s" /> \n' % (gw_mode)
        st += '<Property oe:key="VSMIpv4" oe:value="%s" /> \n' % (vsm_ip)
        st += '<Property oe:key="VSMPriMac" oe:value="%s" /> \n' % (vsm_p_mac)
        st += '<Property oe:key="VSMStdbyMac" oe:value="%s" /> \n' % (vsm_s_mac)
        st += '<Property oe:key="UplinkPPName" oe:value="%s" /> \n' % (uplink_pp)
        st += '<Property oe:key="VSMEncapPPName" oe:value="%s" /> \n' % (vsm_pp)
        st += '<Property oe:key="OvfDeployment" oe:value="installer" /> \n'
        #if vsm_mode == "primary":
        #    st += '<Property oe:key="HARole" oe:value="%s" /> \n' % (vsm_mode)
        #else:
        #   st += '<Property oe:key="HARole" oe:value="standalone" /> \n'
        st += '</PropertySection> \n'
        st += '</Environment> \n'

        ovf_f.write(st)
        ovf_f.close()
        return ovf_f

def main():
    """ repackages the iso file, with modified ovf file """

    #logger = logging.getLogger('myapp')
    #hdlr = logging.FileHandler('/tmp/myapp.log')
    #formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    #hdlr.setFormatter(formatter)
    #logger.addHandler(hdlr) 
    #logger.setLevel(logging.DEBUG)

    ovf_f = createOvfEnvXmlFile(domain=domainid, gateway=mgmtgateway, hostname=gwname, primary_ip=primgmtip, sec_ip=secmgmtip, subnet=mgmtsubnet, password=adminpasswd, gw_mode=gwrole, vsm_ip=vsmip, vsm_p_mac=vsmprimac, vsm_s_mac=vsmstdbymac, uplink_pp=uplinkppname, vsm_pp=vsmencapppname)

    mntdir = tempfile.mkdtemp()
    ddir = tempfile.mkdtemp()

    cret = Command('sudo /bin/mount -o loop -t iso9660 %s %s' % (isoimg, mntdir)).run()
    #logger.info("%s %s" % (cret.output, cret.error))
    cret = Command('cp -r %s/* %s' % (mntdir, ddir)).run()
    #logger.info("%s %s" % (cret.output, cret.error))

    cret = Command('sudo /bin/umount %s' % (mntdir)).run()
    #logger.info("%s %s" % (cret.output, cret.error))

    cret = Command('cp %s %s/ovf-env.xml' % (ovf_f.name, ddir)).run()
    #logger.info("%s %s" % (cret.output, cret.error))


    if os.path.exists('%s/isolinux/isolinux.bin' % (ddir)):
        cret = Command('cd %s; sudo /usr/bin/mkisofs -uid 0 -gid 0 -J -R -A Cisco_Nexus_1000V_GW -b isolinux/isolinux.bin -no-emul-boot -boot-load-size 4 -boot-info-table -o %s .' % (ddir, repackediso)).run()
        #logger.info("%s %s" % (cret.output, cret.error))
    else:
        cret = Command('cd %s; sudo /usr/bin/mkisofs -uid 0 -gid 0 -J -R -A Cisco_Nexus_1000V_GW -b boot/grub/iso9660_stage1_5 -no-emul-boot -boot-load-size 4 -boot-info-table -o %s .' % (ddir, repackediso)).run()
        #logger.info("%s %s" % (cret.output, cret.error))

    os.unlink(ovf_f.name)
    shutil.rmtree(mntdir)
    shutil.rmtree(ddir)

if __name__ == "__main__":
    main()

