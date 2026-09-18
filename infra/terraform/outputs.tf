output "vpc_id" {
  value = aws_vpc.ai_vpc.id
}

output "eks_cluster_name" {
  value = aws_eks_cluster.ai_cluster.name
}

output "database_endpoint" {
  value = aws_db_instance.ai_postgres.endpoint
}

output "redis_endpoint" {
  value = aws_elasticache_cluster.ai_redis.cache_nodes[0].address
}
