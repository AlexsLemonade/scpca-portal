output "job_queue_name" {
  description = "Name of Batch Job Queue"
  value = aws_batch_job_queue.scpca_portal_fargate.name
}

output "job_definition_name" {
  description = "Name of Batch Job Definition"
  value = aws_batch_job_definition.scpca_portal_fargate.name
}
