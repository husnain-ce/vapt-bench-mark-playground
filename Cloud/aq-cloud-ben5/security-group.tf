# ROOT CAUSE: this ingress rule exposes the internal Backup Manager admin API
# (tcp/9105) to the ENTIRE internet. It should have been scoped to the VPC CIDR.
resource "aws_security_group_rule" "backup_mgr_ingress" {
  type              = "ingress"
  from_port         = 9105
  to_port           = 9105
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]        # <-- FIX: ["10.0.0.0/16"] (VPC only)
  security_group_id = aws_security_group.backup_mgr.id
  description       = "backup manager admin API"
}
