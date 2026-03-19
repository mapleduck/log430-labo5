"""
Locustfile for load testing user creation and deletion - store_manager.py
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""
import random
import uuid
from locust import HttpUser, task, between

class UserAPIUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Called every time a Locust user spawns"""
        self.created_user_ids = []

    @task(2)
    def create_user(self):
        """Test POST /users endpoint"""
        unique_id = uuid.uuid4().hex[:8]
        payload = {
            "name": f"Test User {unique_id}",
            "email": f"testuser_{unique_id}@example.ca",
            "user_type_id": random.randint(1, 3)
        }
        with self.client.post(
            "/users",
            json=payload,
            headers={"Content-Type": "application/json"},
            catch_response=True
        ) as response:
            try:
                if response.status_code in [200, 201]:
                    data = response.json()
                    if "user_id" in data:
                        self.created_user_ids.append(data["user_id"])
                        response.success()
                    else:
                        response.failure("Aucun user_id renvoyé")
                else:
                    response.failure(f"Erreur {response.status_code}: {response.text}")
            except Exception as e:
                response.failure(f"Erreur inattendue: {e}")

    @task(1)
    def delete_user(self):
        """Test DELETE /users/:id endpoint"""
        if not self.created_user_ids:
            return
        user_id = self.created_user_ids.pop(0)
        with self.client.delete(
            f"/users/{user_id}",
            catch_response=True
        ) as response:
            try:
                if response.status_code == 200:
                    data = response.json()
                    if data.get("deleted"):
                        response.success()
                    else:
                        response.failure("deleted != true")
                elif response.status_code == 404:
                    response.failure(f"Utilisateur {user_id} introuvable")
                else:
                    response.failure(f"Erreur {response.status_code}: {response.text}")
            except Exception as e:
                response.failure(f"Erreur inattendue: {e}")