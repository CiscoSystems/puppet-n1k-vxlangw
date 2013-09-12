class vxlangw (
    $gw_isoimage,
    $os_password,
    $controller_ip)
{

  include 'stdlib'
  require glance::api
  $b = inline_template('<%= File.basename(gw_isoimage) %>')
  $xx = generate("/usr/bin/sudo", "/bin/cp", "$gw_isoimage", "/etc/puppet/files/$b")

  $dirpath = "/var/spool/vxlangw/"
  $isopath = "/etc/vxlangw/$b"

  include vxlangw::deploy

}
