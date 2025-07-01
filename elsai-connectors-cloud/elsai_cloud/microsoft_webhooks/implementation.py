"""
Microsoft Graph Webhooks (Subscriptions) Management Implementation
"""
from typing import Dict, List, Optional, Any
import requests
from datetime import datetime, timedelta,timezone
from elsai_cloud.config import get_access_token, setup_logger

class MSGraphWebhooksImplementation:
    def __init__(self, base_url: str = "https://graph.microsoft.com/v1.0", client_id:str = None, client_secret: str = None, tenant_id: str = None):
        """
        Initialize MSGraphWebhooks with base URL
        
        Args:
            base_url (str): Base URL for Microsoft Graph API
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id

        self.base_url = base_url
        self.logger = setup_logger()
        self._update_headers()
        self.logger.info("MSGraphWebhooks initialized with base URL: %s", base_url)

    def _update_headers(self) -> None:
        """Update the headers with a fresh access token"""
        try:
            access_token = get_access_token(client_id=self.client_id, client_secret=self.client_secret, tenant_id=self.tenant_id)
            self.headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            self.logger.debug("Successfully updated headers with new access token")
        except Exception as e:
            self.logger.error("Failed to update headers: %s", str(e))
            raise

    def create_subscription(self, 
                          change_type: str,
                          notification_url: str,
                          resource: str,
                          expiration_date_time: Optional[datetime] = None,
                          client_state: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new subscription
        
        Args:
            change_type (str): The type of change that will trigger the webhook
            notification_url (str): The URL that will receive the webhook notifications
            resource (str): The resource to monitor (e.g., "/me/messages")
            expiration_date_time (datetime, optional): When the subscription expires
            client_state (str, optional): Custom state to be passed in notifications
            
        Returns:
            Dict[str, Any]: Created subscription details
        """
        self.logger.info("Creating new subscription for resource: %s", resource)
        try:
            if expiration_date_time is None:
                expiration_date_time = datetime.now(timezone.utc) + timedelta(days=3)
                expiration_date_time = expiration_date_time.replace(microsecond=0)
                
            payload = {
                "changeType": change_type,
                "notificationUrl": notification_url,
                "resource": resource,
                "expirationDateTime": expiration_date_time.isoformat().replace("+00:00", "Z"),
            }
            print(payload)
            if client_state:
                payload["clientState"] = client_state
                
            self._update_headers()
            response = requests.post(
                f"{self.base_url}/subscriptions",
                headers=self.headers,
                json=payload,
                timeout=30  # Set a timeout for the request
            )
            response.raise_for_status()
            result = response.json()
            self.logger.info("Successfully created subscription with ID: %s", result.get('id'))
            return result
        except Exception as e:
            self.logger.error("Failed to create subscription: %s", str(e))
            raise

    def list_subscriptions(self) -> List[Dict[str, Any]]:
        """
        List all active subscriptions
        
        Returns:
            List[Dict[str, Any]]: List of subscription details
        """
        self.logger.info("Fetching list of all subscriptions")
        try:
            self._update_headers()
            response = requests.get(
                f"{self.base_url}/subscriptions",
                headers=self.headers,
                timeout=30  # Set a timeout for the request
            )
            response.raise_for_status()
            subscriptions = response.json().get('value', [])
            self.logger.info("Successfully retrieved %d subscriptions", len(subscriptions))
            return subscriptions
        except Exception as e:
            self.logger.error("Failed to list subscriptions: %s", str(e))
            raise

    def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """
        Get details of a specific subscription
        
        Args:
            subscription_id (str): ID of the subscription to retrieve
            
        Returns:
            Dict[str, Any]: Subscription details
        """
        self.logger.info("Fetching details for subscription: %s", subscription_id)
        try:
            self._update_headers()
            response = requests.get(
                f"{self.base_url}/subscriptions/{subscription_id}",
                headers=self.headers,
                timeout=30  # Set a timeout for the request
            )
            response.raise_for_status()
            result = response.json()
            self.logger.info("Successfully retrieved subscription details")
            return result
        except Exception as e:
            self.logger.error("Failed to get subscription details: %s", str(e))
            raise

    def update_subscription(self, 
                          subscription_id: str,
                          expiration_date_time: Optional[datetime] = None,
                          notification_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Update an existing subscription
        
        Args:
            subscription_id (str): ID of the subscription to update
            expiration_date_time (datetime, optional): New expiration time
            notification_url (str, optional): New notification URL
            
        Returns:
            Dict[str, Any]: Updated subscription details
        """
        self.logger.info("Updating subscription: %s", subscription_id)
        try:
            payload = {}
            
            if expiration_date_time:
                payload["expirationDateTime"] = expiration_date_time.isoformat() + "Z"
            if notification_url:
                payload["notificationUrl"] = notification_url
                
            self._update_headers()
            response = requests.patch(
                f"{self.base_url}/subscriptions/{subscription_id}",
                headers=self.headers,
                json=payload,
                timeout=30  # Set a timeout for the request
            )
            response.raise_for_status()
            result = response.json()
            self.logger.info("Successfully updated subscription")
            return result
        except Exception as e:
            self.logger.error("Failed to update subscription: %s", str(e))
            raise

    def delete_subscription(self, subscription_id: str) -> None:
        """
        Delete a subscription
        
        Args:
            subscription_id (str): ID of the subscription to delete
        """
        self.logger.info("Deleting subscription: %s", subscription_id)
        try:
            self._update_headers()
            response = requests.delete(
                f"{self.base_url}/subscriptions/{subscription_id}",
                headers=self.headers,
                timeout=30  # Set a timeout for the request
            )
            response.raise_for_status()
            self.logger.info("Successfully deleted subscription")
        except Exception as e:
            self.logger.error("Failed to delete subscription: %s", str(e))
            raise

    def reauthorize_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """
        Reauthorize a subscription
        
        Args:
            subscription_id (str): ID of the subscription to reauthorize
            
        Returns:
            Dict[str, Any]: Reauthorized subscription details
        """
        self.logger.info("Reauthorizing subscription: %s", subscription_id)
        try:
            self._update_headers()
            response = requests.post(
                f"{self.base_url}/subscriptions/{subscription_id}/reauthorize",
                headers=self.headers,
                timeout=30  # Set a timeout for the request
            )
            response.raise_for_status()
            
            # Handle empty response
            if not response.content:
                # If reauthorization was successful but returned no content,
                # get the subscription details to return
                return self.get_subscription(subscription_id)
                
            return response.json()
        except Exception as e:
            self.logger.error("Failed to reauthorize subscription: %s", str(e))
            raise 