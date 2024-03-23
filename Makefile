# Define colors variables
blue="\033[0;34m"
green="\033[0;32m"
cyan="\033[0;36m"
reset="\033[0;39m"

define check-terraform
	@which terraform > /dev/null || (echo "Terraform is not installed. Please install it first." && exit 1)
endef

check-terraform:
	$(check-terraform)

infra-resources-gcp: check-terraform
	@echo $(blue) "Creating infra resources for GCP ..." $(reset)
	@cd infra/terraform/gcp/resources && terraform init && terraform apply -auto-approve


infra-services-gcp: check-terraform
	@echo $(blue) "Creating infra services for GCP (Cloud Run) ..." $(reset)
	@cd infra/terraform/gcp/services && terraform init && terraform apply -auto-approve

infra-resources-aws: check-terraform
	@echo $(blue) "Creating infra resources for AWS ..." $(reset)
	@cd infra/terraform/aws/resources && terraform init && terraform apply -auto-approve

infra-services-aws: check-terraform
	@echo $(blue) "Creating infra services for AWS (ECS) ..." $(reset)
	@cd infra/terraform/aws/services && terraform init && terraform apply -auto-approve