variable "aws_region" {
  type    = string
  default = "ap-southeast-1"
}

variable "environment" {
  type    = string
  default = "production"
}

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

variable "eks_role_arn" {
  type    = string
  default = "arn:aws:iam::123456789012:role/eks-cluster-role"
}

variable "subnet_ids" {
  type    = list(string)
  default = ["subnet-11111111", "subnet-22222222"]
}

variable "db_username" {
  type    = string
  default = "ai_admin"
}

variable "db_password" {
  type      = string
  sensitive = true
  default   = "secure_db_pass_123!"
}
