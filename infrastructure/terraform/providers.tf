terraform {
  required_version = ">= 1.4.0"

  required_providers {
    openstack = {
      source  = "terraform-provider-openstack/openstack"
      version = "~> 1.48.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.16.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.8.0"
    }
  }

  backend "swift" {
    container         = "terraform-state"
    archive_container = "terraform-state-archive"
  }
}

provider "openstack" {
  auth_url    = "https://auth.cloud.ovh.net/v3"
  region      = var.region
  user_name   = var.os_username
  password    = var.os_password
  tenant_name = var.os_tenant_name
  domain_name = var.os_domain_name
}

provider "kubernetes" {
  host                   = data.openstack_containerinfra_cluster_v1.k8s.endpoint
  client_certificate     = data.openstack_containerinfra_cluster_v1.k8s.kubeconfig.client_certificate
  client_key             = data.openstack_containerinfra_cluster_v1.k8s.kubeconfig.client_key
  cluster_ca_certificate = data.openstack_containerinfra_cluster_v1.k8s.kubeconfig.cluster_ca_certificate
}

provider "helm" {
  kubernetes {
    host                   = data.openstack_containerinfra_cluster_v1.k8s.endpoint
    client_certificate     = data.openstack_containerinfra_cluster_v1.k8s.kubeconfig.client_certificate
    client_key             = data.openstack_containerinfra_cluster_v1.k8s.kubeconfig.client_key
    cluster_ca_certificate = data.openstack_containerinfra_cluster_v1.k8s.kubeconfig.cluster_ca_certificate
  }
}