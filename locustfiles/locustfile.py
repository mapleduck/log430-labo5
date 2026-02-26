"""
Locustfile for load testing store_manager.py
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""
import random
from locust import HttpUser, task, between

class FlaskAPIUser(HttpUser):
    # Wait time between requests (1-3 seconds)
    wait_time = between(1, 3)
    
    def on_start(self):
        """Called every time a Locust user spawns"""
        print("Welcome, user!")

    # @task(1)
    # def test_rate_limit(self):
    #     """Test pour vérifier le rate limiting"""
    #     payload = {
    #         "user_id": random.randint(1, 3),
    #         "items": [{"product_id": random.randint(1, 4), "quantity": random.randint(1, 10)}] 
    #     }   
        
    #     response = self.client.post(
    #         "/store-manager-api/orders",
    #         json=payload
    #     )
        
    #     if response.status_code == 503:  # HTTP 503 Service Unavailable
    #         print("Rate limit atteint!")

    @task(1) 
    def orders(self):
        """Test POST /store-manager-api/orders endpoint (write)"""
        random_user = random.randrange(1, 10)
        random_prod = random.randrange(1, 5)
        random_qty = random.randrange(1, 3)
        
        mock_order = {
            "user_id": random_user,
            "items": [{"product_id": random_prod, "quantity": random_qty}] 
        }   

        with self.client.post("/store-manager-api/orders", 
                            json=mock_order, 
                            headers={"Content-Type": "application/json"},
                            catch_response=True) as response:
            try:
                if response.status_code in [200, 201]:
                    data = response.json()
                    if "order_id" in data:
                        response.success()
                    else:
                        response.failure("Aucun ID renvoyé")
                elif response.status_code == [429, 503]:
                    response.failure("Limite atteinte ou Service indisponible (KrakenD)")
                else:
                    response.failure(f"Erreur {response.status_code}: {response.text}")
            except Exception as e:
                response.failure(f"Erreur inattendue: {e}")

    @task(2) 
    def get_one_order(self):
        random_id = random.randint(1, 100)
        self.client.get(f"/store-manager-api/orders/{random_id}")