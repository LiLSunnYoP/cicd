provider "aws" {
  region = "ap-south-1"
}

resource "aws_s3_bucket" "s3_bucket" {
  bucket = "your-s3-bucket"
}

resource "aws_rds_instance" "rds" {
  allocated_storage    = 20
  engine              = "mysql"
  instance_class      = "db.t3.micro"
  db_name             = "your-database"
  username           = "your-username"
  password           = "your-password"
  publicly_accessible = true
  skip_final_snapshot = true
}

resource "aws_glue_catalog_database" "glue_db" {
  name = "your-glue-database"
}

resource "aws_ecr_repository" "ecr_repo" {
  name = "your-ecr-repo"
}
