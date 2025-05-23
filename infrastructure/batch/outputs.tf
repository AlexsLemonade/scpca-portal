output "job_queue_name_fargate" {
  description = "Name of Batch Job Queue"
  value = aws_batch_job_queue.scpca_portal_fargate.name
}

output "job_definition_name_fargate" {
  description = "Name of Batch Job Definition"
  value = aws_batch_job_definition.scpca_portal_fargate.name
}

output "job_queue_name_ec2" {
  description = "Name of Batch Job Queue"
  value = aws_batch_job_queue.scpca_portal_ec2.name
}

output "job_definition_name_ec2" {
  description = "Name of Batch Job Definition"
  value = aws_batch_job_definition.scpca_portal_ec2.name
}
