variable "auth_url" {
  description = "OpenStack Auth URL"
  type        = string
}

variable "username" {
  description = "OpenStack username"
  type        = string
}

variable "password" {
  description = "OpenStack password"
  type        = string
  sensitive   = true
}

variable "tenant_name" {
  description = "OpenStack tenant/project name"
  type        = string
}

variable "region" {
  description = "OpenStack region"
  type        = string
  default     = "RegionOne"
}

variable "network_name" {
  description = "Network name for instances"
  type        = string
  default     = "private"
}

variable "dns_zone_id" {
  description = "DNS zone ID"
  type        = string
}

variable "dns_domain" {
  description = "DNS domain"
  type        = string
}