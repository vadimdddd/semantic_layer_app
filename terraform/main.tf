terraform {
  required_providers {
    kind = {
      source  = "tehcyx/kind"
      version = "~> 0.2"
    }
    kubectl = {
      source  = "gavinbunney/kubectl"
      version = "~> 1.14"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.9"
    }
  }
  
  backend "local" {
    path = "terraform.tfstate"
  }
}

provider "kind" {}

provider "kubectl" {
  host                   = kind_cluster.this.endpoint
  cluster_ca_certificate = kind_cluster.this.cluster_ca_certificate
  client_certificate     = kind_cluster.this.client_certificate
  client_key             = kind_cluster.this.client_key
  load_config_file       = false
}

provider "helm" {
  kubernetes {
    host                   = kind_cluster.this.endpoint
    cluster_ca_certificate = kind_cluster.this.cluster_ca_certificate
    client_certificate     = kind_cluster.this.client_certificate
    client_key             = kind_cluster.this.client_key
  }
}

resource "kind_cluster" "this" {
  name = "this"
  
  kind_config {
    kind = "Cluster"
    api_version = "kind.x-k8s.io/v1alpha4"
    
    node {
      role = "control-plane"
    }
    
    node {
      role = "worker"
    }
    
    node {
      role = "worker"
    }
  }
}

# Install Ingress NGINX
resource "helm_release" "ingress_nginx" {
  name       = "ingress-nginx"
  repository = "https://kubernetes.github.io/ingress-nginx"
  chart      = "ingress-nginx"
  namespace  = "ingress-nginx"
  create_namespace = true
  
  set {
    name  = "controller.service.type"
    value = "NodePort"
  }
  
  set {
    name  = "controller.watchIngressWithoutClass"
    value = "true"
  }
  
  depends_on = [kind_cluster.this]
}

# Install Prometheus
resource "helm_release" "prometheus" {
  name       = "prometheus"
  repository = "https://prometheus-community.github.io/helm-charts"
  chart      = "prometheus"
  namespace  = "monitoring"
  create_namespace = true
  
  set {
    name  = "server.persistentVolume.enabled"
    value = "false"
  }
  
  depends_on = [kind_cluster.this]
}

# Install Grafana
resource "helm_release" "grafana" {
  name       = "grafana"
  repository = "https://grafana.github.io/helm-charts"
  chart      = "grafana"
  namespace  = "monitoring"
  create_namespace = true
  
  set {
    name  = "persistence.enabled"
    value = "false"
  }
  
  set {
    name  = "service.type"
    value = "NodePort"
  }
  
  set {
    name  = "adminPassword"
    value = "admin123"
  }
  
  depends_on = [helm_release.prometheus]
}

# Install ArgoCD
resource "helm_release" "argocd" {
  name       = "argocd"
  repository = "https://argoproj.github.io/argo-helm"
  chart      = "argo-cd"
  namespace  = "argocd"
  create_namespace = true
  
  set {
    name  = "server.service.type"
    value = "NodePort"
  }
  
  set {
    name  = "server.service.nodePort"
    value = "30080"
  }
  
  set {
    name  = "server.ingress.enabled"
    value = "false"
  }
  
  set {
    name  = "configs.params.server.insecure"
    value = "true"
  }
  
  depends_on = [kind_cluster.this]
}

# Output info
output "cluster_endpoint" {
  value = kind_cluster.this.endpoint
}

output "grafana_password" {
  value = "admin123"
  sensitive = true
}

output "argocd_server" {
  value = "http://localhost:30080"
}

output "argocd_password_command" {
  value = "kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d"
}

output "ollama_status" {
  value = "Ollama installed. Check: kubectl get pods | grep ollama"
}
