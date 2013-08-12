define vxlangw ($user = $title, 
    $vsmip,
    $domainid,
    $gw_name,
    $gw_role = 'standalone',
    $gw_isoimage,
    $gw_domainid,
    $gw_adminpasswd,
    $gw_primgmtip,
    $gw_secmgmtip,
    $gw_mgmtnetmask,
    $gw_mgmtgateway,
    $vsmprimac,
    $vsmstdbymac,
    $uplinkppname,
    $vsmencapppname)
{


  $d = inline_template('<%= File.basename(gw_isoimage) %>')
  $gw_imgfile  = "/var/spool/vxlangw/$d"


  $xx = generate('/usr/bin/env', '/usr/share/puppet/modules/vxlangw/bin/gw_glance_repackiso.py', "-i$gw_isoimage", "-d$gw_domainid", "-n$gw_name", "-m$gw_primgmtip", "-o$gw_secmgmtip", "-s$gw_mgmtnetmask", "-g$gw_mgmtgateway", "-p$gw_adminpasswd", "-r$gw_role" , "-v$vsmip", "-a$vsmprimac", "-u$vsmstdbymac", "-c$uplinkppname", "-e$vsmencapppname", "-f/etc/puppet/files/${user}_${gw_role}_repacked.iso")
  
  include 'stdlib'
  require glance::api

  $dirpath = "/var/spool/${user}_${gw_role}"
  file { $dirpath:
         owner => 'root',
         group => 'root',
         mode  => '664',
         ensure => directory
  }

  $isopath = "/var/spool/${user}_${gw_role}/${user}_${gw_role}_repacked.iso"

  file { $isopath:
         owner => 'root',
         group => 'root',
         mode => '666',
         source => "puppet:///files/${user}_${gw_role}_repacked.iso",
         require => File[$dirpath]
   }

  $isoname = "${user}_${gw_role}_repacked.iso"
  glance_image {$isoname:
        ensure => present,
        name => $isoname,
        is_public => Yes,
        container_format => ovf,
        disk_format => iso,
        source => $isopath,
        require => Service['glance-api']
  }

#  exec { "add_glance":
#       command => "/usr/bin/glance add name =\"VM_ISO\" disk_format=qcow2 container_format=bare <$isopath",
#       unless => '/usr/bin/glance image-show "VM_ISO"'
#  }


File["$dirpath"] -> File["$isopath"] -> glance_image["$isoname"]
#File["$dirpath"] -> File["$isopath"] -> Exec["add_glance"]


#  glance_image {
#       ensure => present,
#       name => 'gw_image',
#       is_public => No,
#       container_format => ovf, or bare
#       disk_format => 'qcow2',
#       source => "/var/spool/vxlangw/$gw_role_repacked.iso",
#       require => Service['glance-api']
#  }

#File['/var/spool/vxlangw'] -> File["$isoname"] -> glance_image['${gw_role}_repacked.iso']
# File["$isopath"] -> glance_image["$isoname"]

}
