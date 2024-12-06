from locust import HttpUser, task, between
import json
import random

class LicitometroUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Autenticación del usuario al inicio"""
        response = self.client.post("/api/auth/login", json={
            "username": f"test_user_{random.randint(1, 1000)}",
            "password": "test_password"
        })
        if response.status_code == 200:
            self.token = response.json()["access_token"]
        else:
            self.token = None

    @task(3)
    def search_licitaciones(self):
        """Búsqueda de licitaciones"""
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        search_terms = [
            "construcción",
            "servicios",
            "consultoría",
            "mantenimiento",
            "equipamiento"
        ]
        self.client.get(
            f"/api/search?query={random.choice(search_terms)}",
            headers=headers
        )

    @task(2)
    def view_licitacion_details(self):
        """Ver detalles de una licitación específica"""
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        licitacion_ids = list(range(1, 1001))  # Simulación de IDs
        self.client.get(
            f"/api/licitaciones/{random.choice(licitacion_ids)}",
            headers=headers
        )

    @task(1)
    def submit_document(self):
        """Subir un documento"""
        if not self.token:
            return
            
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        document_data = {
            "title": f"Documento de prueba {random.randint(1, 1000)}",
            "content": "Contenido de prueba para carga",
            "metadata": {
                "type": "test",
                "size": random.randint(1000, 10000)
            }
        }
        
        self.client.post(
            "/api/documents",
            headers=headers,
            json=document_data
        )

    @task(1)
    def check_notifications(self):
        """Consultar notificaciones"""
        if not self.token:
            return
            
        headers = {"Authorization": f"Bearer {self.token}"}
        self.client.get("/api/notifications", headers=headers)

class ReconWorker(HttpUser):
    wait_time = between(5, 10)
    
    def on_start(self):
        """Autenticación del worker"""
        response = self.client.post("/api/auth/worker/login", json={
            "worker_id": f"worker_{random.randint(1, 10)}",
            "api_key": "test_api_key"
        })
        if response.status_code == 200:
            self.token = response.json()["access_token"]
        else:
            self.token = None

    @task
    def process_recon_task(self):
        """Procesar tarea de reconocimiento"""
        if not self.token:
            return
            
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        task_data = {
            "type": "document_analysis",
            "source_url": f"https://example.com/doc_{random.randint(1, 1000)}.pdf",
            "priority": random.choice(["high", "medium", "low"])
        }
        
        self.client.post(
            "/api/recon/tasks",
            headers=headers,
            json=task_data
        )
