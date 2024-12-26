from django.db import models


class Profile(models.Model):
    STATE_CHOICES = [
        ('start', 'Start'),
        ('choose_language', 'Choose Language'),
        ('register_name', 'Register Name'),
        ('register_phone', 'Register Phone'),
        ('register_age', 'Register Age'),
        ('rent_choose_type', 'Choose Rent Type'),
        ('rent_choose_price', 'Choose Rent Price'),
        ('show_variants', 'Show Variants'),
        ('lease_photos', 'Upload Lease Photos'),
        ('lease_type', 'Choose Lease Type'),
        ('lease_type_custom', 'Custom Lease Type'),
        ('lease_price', 'Enter Lease Price'),
        ('lease_rooms', 'Enter Number of Rooms'),
        ('lease_description', 'Enter Description'),
        ('lease_confirm', 'Confirm Lease'),
        ('contact_moderator', 'Contact Moderator'),
    ]

    rent_types = models.JSONField(default=list, blank=True)
    prices = models.JSONField(default=list, blank=True)
    last_shown_estate_id = models.IntegerField(null=True, blank=True)
    free_ads_remaining = models.IntegerField(default=5)
    language = models.CharField(max_length=2, choices=[('ru', 'Русский'), ('uk', 'Українська')])
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default='start')
    name = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    username = models.CharField(max_length=20, blank=True)
    age = models.IntegerField(default=18)

    def __str__(self):
        return f"{self.username} Profile"


class EstateType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class RealEstate(models.Model):
    ESTATE_TYPE_CHOICES = [
        ('квартира', 'Квартира'),
        ('будинок', 'Будинок'),
        ('кімната', 'Кімната'),
        ('інше', 'Інше'),
    ]

    owner = models.ForeignKey('Profile', on_delete=models.CASCADE)
    estate_type = models.CharField(max_length=50, choices=ESTATE_TYPE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rooms = models.IntegerField()
    description = models.TextField(blank=True)  # Описание на русском
    is_for_rent = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.estate_type} - {self.price}"


class RealEstatePhoto(models.Model):
    real_estate = models.ForeignKey(RealEstate, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='realestate_photos/')

    def __str__(self):
        return f"Photo for {self.real_estate} - {self.id}"


class LeaseDraft(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='lease_draft')
    estate_type = models.CharField(max_length=100, blank=True, null=True)  # Просто текст
    price = models.FloatField(null=True, blank=True)
    rooms = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True)  # Описание на русском

    def __str__(self):
        return f"Draft for Profile {self.profile.username}"


class LeaseDraftPhoto(models.Model):
    lease_draft = models.ForeignKey(LeaseDraft, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='leasedraft_photos/')

    def __str__(self):
        return f"Photo for draft {self.lease_draft} - {self.id}"
