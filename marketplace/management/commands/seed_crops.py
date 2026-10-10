from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from marketplace.models import CropProduce
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = "Seed sample CropProduce records for testing"

    def handle(self, *args, **kwargs):
        farmers = User.objects.filter(profile__role="farmer")
        if not farmers.exists():
            self.stdout.write(
                self.style.ERROR("No farmers found. Create a farmer user first.")
            )
            return

        crops = [
            ("Wheat", 500, "kg", 85, "Lahore"),
            ("Rice (Basmati)", 200, "kg", 250, "Faisalabad"),
            ("Sugarcane", 40, "maund", 1800, "Multan"),
            ("Cotton", 25, "maund", 8500, "Bahawalpur"),
            ("Maize", 800, "kg", 55, "Sahiwal"),
            ("Potato", 1500, "kg", 45, "Okara"),
            ("Onion", 900, "kg", 60, "Karachi"),
            ("Tomato", 300, "kg", 90, "Peshawar"),
            ("Mango (Sindhri)", 400, "kg", 320, "Multan"),
            ("Chili (Red)", 150, "kg", 280, "Hyderabad"),
        ]

        created_count = 0
        for name, qty, unit, price, loc in crops:
            farmer = random.choice(farmers)
            CropProduce.objects.create(
                farmer=farmer,
                crop_name=name,
                quantity=qty,
                unit=unit,
                price=price,
                harvest_date=date.today() - timedelta(days=random.randint(1, 20)),
                location=loc,
                description=f"Fresh {name} from {loc}.",
                is_available=random.choice([True, True, True, False]),
            )
            created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded {created_count} crops."))
