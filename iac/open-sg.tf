resource "aws_s3_bucket" "bad_example" {
  bucket = "my-unsecure-bucket"
  acl    = "public-read"  # Public access, flagged

  tags = {
    Name        = "PublicBucket"
    Environment = "Dev"
  }
}

resource "aws_security_group" "example" {
  name        = "allow_all"
  description = "Security group with open ports"
  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Open to the world
  }
}
