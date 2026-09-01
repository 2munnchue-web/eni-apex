provider "digitalocean" {
  token = var.do_token
}

resource "digitalocean_droplet" "team_server" {
  name   = "team-server"
  region = "nyc1"
  size   = "s-4vcpu-8gb"
  image  = "ubuntu-22-04-x64"
  ssh_keys = [var.ssh_fingerprint]
}

resource "digitalocean_droplet" "redirector" {
  count  = 2
  name   = "redirector-${count.index+1}"
  region = "nyc1"
  size   = "s-1vcpu-1gb"
  image  = "ubuntu-22-04-x64"
  ssh_keys = [var.ssh_fingerprint]
}

output "team_server_ip" {
  value = digitalocean_droplet.team_server.ipv4_address
}
