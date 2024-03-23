output "elb_dns" {
  description = "The IP address of the ELB"
  value       = aws_lb.alb.dns_name
}
