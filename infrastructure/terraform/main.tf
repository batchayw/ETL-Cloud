terraform {
  required_providers {
    openstack = {
      source  = "terraform-provider-openstack/openstack"
      version = "~> 1.48.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.16.0"
    }
  }
}

provider "openstack" {
  auth_url    = var.auth_url
  user_name   = var.username
  password    = var.password
  tenant_name = var.tenant_name
  region      = var.region
}

resource "openstack_compute_instance_v2" "etl_servers" {
  count           = 3
  name            = "etl-server-${count.index}"
  image_name      = "ubuntu-20.04"
  flavor_name     = "m1.medium"
  key_pair        = openstack_compute_keypair_v2.etl_key.name
  security_groups = ["default", "etl-cluster"]

  network {
    name = var.network_name
  }
}

resource "openstack_networking_secgroup_v2" "etl_cluster" {
  name        = "etl-cluster"
  description = "Security group for ETL cluster"
}

resource "openstack_networking_secgroup_rule_v2" "etl_rules" {
  for_each = {
    "22"    : "tcp",
    "8080"  : "tcp",
    "9090"  : "tcp",
    "9000"  : "tcp",
    "5432"  : "tcp",
    "3000"  : "tcp"
  }

  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = each.value
  port_range_min    = each.key
  port_range_max    = each.key
  security_group_id = openstack_networking_secgroup_v2.etl_cluster.id
}

resource "openstack_blockstorage_volume_v2" "etl_volumes" {
  count       = 3
  name        = "etl-volume-${count.index}"
  size        = 100
  description = "Volume for ETL node ${count.index}"
}

resource "openstack_compute_volume_attach_v2" "etl_attachments" {
  count       = 3
  instance_id = openstack_compute_instance_v2.etl_servers[count.index].id
  volume_id   = openstack_blockstorage_volume_v2.etl_volumes[count.index].id
}

resource "openstack_compute_keypair_v2" "etl_key" {
  name       = "etl-key"
  public_key = file("~/.ssh/id_rsa.pub")
}

resource "openstack_dns_recordset_v2" "etl_dns" {
  zone_id     = var.dns_zone_id
  name        = "etl.${var.dns_domain}"
  type        = "A"
  ttl         = 300
  records     = openstack_compute_instance_v2.etl_servers[*].access_ip_v4
}