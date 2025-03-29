output "instance_ips" {
  value       = openstack_compute_instance_v2.etl_servers[*].access_ip_v4
  description = "ETL cluster instance IPs"
}

output "dns_record" {
  value       = openstack_dns_recordset_v2.etl_dns.name
  description = "ETL cluster DNS record"
}

output "volume_ids" {
  value       = openstack_blockstorage_volume_v2.etl_volumes[*].id
  description = "ETL volumes IDs"
}