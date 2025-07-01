"""
Microsoft Graph Webhooks (Subscriptions) Management Implementation
"""
from .implementation import MSGraphWebhooksImplementation
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, timezone
import os
class MSGraphWebhooks:
    def __init__(self, base_url: str = "https://graph.microsoft.com/v1.0", client_id:str = None, client_secret: str = None, tenant_id: str = None):
        """
        Initialize MSGraphWebhooks with base URL
        
        Args:
            base_url (str): Base URL for Microsoft Graph API
        """

        self.client_id = client_id or os.getenv("CLIENT_ID")
        self.client_secret = client_secret or os.getenv("CLIENT_SECRET")
        self.tenant_id = tenant_id or os.getenv("TENANT_ID")

        if not all([self.client_id, self.client_secret, self.tenant_id]):
            raise ValueError("All parameters (client_id, client_secret, tenant_id) must be provided or set in environment variables CLIENT_ID, CLIENT_SECRET, TENANT_ID.")
        self._impl = MSGraphWebhooksImplementation(base_url=base_url, client_id=self.client_id, client_secret=self.client_secret, tenant_id=self.tenant_id)

    def _update_headers(self) -> None:
        """Update the headers with a fresh access token"""
        self._impl._update_headers()

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
        return self._impl.create_subscription(
            change_type=change_type,
            notification_url=notification_url,
            resource=resource,
            expiration_date_time=expiration_date_time,
            client_state=client_state
        )

    def list_subscriptions(self) -> List[Dict[str, Any]]:
        """
        List all active subscriptions
        
        Returns:
            List[Dict[str, Any]]: List of subscription details
        """
        return self._impl.list_subscriptions()

    def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """
        Get details of a specific subscription
        
        Args:
            subscription_id (str): ID of the subscription to retrieve
            
        Returns:
            Dict[str, Any]: Subscription details
        """
        return self._impl.get_subscription(subscription_id)

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
        return self._impl.update_subscription(
            subscription_id=subscription_id,
            expiration_date_time=expiration_date_time,
            notification_url=notification_url
        )

    def delete_subscription(self, subscription_id: str) -> None:
        """
        Delete a subscription
        
        Args:
            subscription_id (str): ID of the subscription to delete
        """
        self._impl.delete_subscription(subscription_id)

    def reauthorize_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """
        Reauthorize a subscription
        
        Args:
            subscription_id (str): ID of the subscription to reauthorize
            
        Returns:
            Dict[str, Any]: Reauthorized subscription details
        """
        return self._impl.reauthorize_subscription(subscription_id)