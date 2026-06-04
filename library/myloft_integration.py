import requests
from django.conf import settings

class MyLOFTIntegration:
    """Integration with existing MyLOFT library system"""
    
    def __init__(self):
        self.base_url = "https://myloft.campus-care.co.ke/api"
        self.api_key = getattr(settings, 'MYLOFT_API_KEY', 'dummy_key')
    
    def get_borrowed_books(self, student_id):
        """Fetch borrowed books from MyLOFT"""
        # Note: Since this is an external API that might not actually exist yet
        # we'll add a try-except to avoid breaking the application in case of failure.
        try:
            response = requests.get(
                f"{self.base_url}/borrowed/{student_id}",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            # Fallback to an empty list or mock data
            return []
    
    def calculate_fine(self, book_id, days_overdue):
        """Calculate fine based on MyLOFT rules"""
        daily_fine = 20  # KES per day
        return days_overdue * daily_fine
