class n1k-vxlangw::deploy {

  file { '/etc/vxlangw':
         owner => 'root',
         group => 'root',
         mode  => '664',
         ensure => directory,
  }

  file { $isopath:
         owner => 'root',
         group => 'root',
         mode => '666',
         source => "puppet:///files/$b",
         require => File['/etc/vxlangw']
  }

  $qcowpath = "/etc/vxlangw/$b"
  exec {"add_glance":
        command => "/usr/bin/glance image-create --name=$b --is-public=true --property hw_vif_model=e1000 --property hw_disk_bus=ide --property hw_cdrom_bus=ide --container-format=ovf --disk-format=qcow2 < $qcowpath",
        environment => ["OS_USERNAME=admin","OS_TENANT_NAME=admin","OS_PASSWORD=$os_password","OS_AUTH_URL=http://$controller_ip:5000/v2.0/"],
        unless => "/usr/bin/glance index | grep -c $b",
     }

File["/etc/vxlangw"] ->  File["$isopath"] -> Exec["add_glance"]


}
