resource "google_compute_instance" "chroma1" {
  project      = var.project_id
  name         = "chroma-1"
  machine_type = var.machine_type
  zone         = var.zone

  tags = ["chroma"]

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
      size  = 20
    }
  }

  network_interface {
    network = "default"

    access_config {
      // Ephemeral public IP
    }
  }

  metadata_startup_script = templatefile("${path.module}/startup.sh", { chroma_release = var.chroma_release })
}

resource "google_compute_firewall" "default" {
  project = var.project_id
  name    = "chroma-firewall"
  network = "default"

  allow {
    protocol = "icmp"
  }

  allow {
    protocol = "tcp"
    ports    = ["8000"]
  }

  # Only allow traffic from internal VPC IPs.
  source_ranges = ["10.128.0.0/9"] # This includes the default VPC address range for Google Cloud. Adjust if your VPC has a different range.

  target_tags = ["chroma"]
}

output "instance_internal_ip" {
  description = "The internal IP address of the instance."
  value       = google_compute_instance.chroma1.network_interface[0].network_ip
}