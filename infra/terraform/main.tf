terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# 1. Virtual Private Cloud (VPC)
resource "aws_vpc" "ai_vpc" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "ai-platform-vpc"
    Environment = var.environment
  }
}

# 2. Kubernetes Cluster (EKS)
resource "aws_eks_cluster" "ai_cluster" {
  name     = "ai-platform-${var.environment}"
  role_arn = var.eks_role_arn

  vpc_config {
    subnet_ids = var.subnet_ids
  }
}

# 3. Relational Database with pgvector
resource "aws_db_instance" "ai_postgres" {
  identifier          = "ai-platform-db-${var.environment}"
  allocated_storage   = 50
  engine              = "postgres"
  engine_version      = "16.1"
  instance_class      = "db.r6g.xlarge"
  username            = var.db_username
  password            = var.db_password
  skip_final_snapshot = true
}

# 4. Redis Cache & Queue
resource "aws_elasticache_cluster" "ai_redis" {
  cluster_id           = "ai-redis-${var.environment}"
  engine               = "redis"
  node_type            = "cache.m6g.large"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379
}

# 5. Secrets Manager for LLM API keys
resource "aws_secretsmanager_secret" "llm_api_keys" {
  name = "ai-platform-api-keys-${var.environment}"
}
