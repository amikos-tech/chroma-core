terraform {
  required_providers {
    render = {
      source = "jackall3n/render"
      version = "~> 1.3.0"
    }
  }
}

variable "render_api_token" {
  sensitive   = true
}

variable "render_user_email" {
  sensitive   = true
}

provider "render" {
  api_key = var.render_api_token
}

data "render_owner" "render_owner" {
  email = var.render_user_email
}

resource "render_service" "chroma" {
  name = "chroma"
  owner = data.render_owner.render_owner.id
  type = "web_service"
  auto_deploy = true

  image = {
    owner_id = data.render_owner.render_owner.id
    image_path = "docker.io/chromadb/chroma:${var.chroma_release}"
  }

  web_service_details = {
    env = "image"
    plan = var.render_plan
    region = var.region
    health_check_path = "/api/v1/heartbeat"
    disk = {
      name = var.chroma_data_volume_device_name
      mount_path = "/chroma-data"
      size_gb = var.chroma_data_volume_size
    }
    docker = {
      command = "uvicorn chromadb.app:app --reload --workers 1 --host 0.0.0.0 --port 80 --log-config chromadb/log_config.yml"
      path = "./Dockerfile"
    }
  }
}

resource "render_service_environment" "chroma_env" {
  service = render_service.chroma.id

  variables = [{
      key = "IS_PERSISTENT"
      value = "1"
    },
    {
      key = "PERSIST_DIRECTORY"
      value = "/chroma-data"
    },
    {
      key = "CHROMA_SERVER_AUTH_CREDENTIALS_PROVIDER"
      value = "chromadb.auth.token.TokenConfigServerAuthCredentialsProvider"
    },
    {
      key = "CHROMA_SERVER_AUTH_CREDENTIALS"
      value = local.token_auth_credentials.token
    },
    {
      key = "CHROMA_SERVER_AUTH_PROVIDER"
      value = "token"
    }]
}


#Necessary workaround for Render Bug related to env vars

data "http" "redeploy_chroma" {
  url = "https://api.render.com/v1/services/${render_service.chroma.id}/deploys"
  method = "POST"
  request_headers = {
    "accept" = "application/json"
    "authorization" = "Bearer ${var.render_api_token}"
    content_type = "application/json"
  }

  request_body = "{\"clearCache\":\"clear\"}"

  depends_on = [render_service_environment.chroma_env]
}


output "instance_url" {
  value = render_service.chroma.web_service_details.url
}

output "chroma_auth_token" {
  value     = random_password.chroma_token.result
  sensitive = true
}
