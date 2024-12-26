from django.contrib import admin

from estate_bot.models import Profile, RealEstate, EstateType, RealEstatePhoto, LeaseDraft, LeaseDraftPhoto

admin.site.register(Profile)
admin.site.register(RealEstate)
admin.site.register(EstateType)
admin.site.register(RealEstatePhoto)
admin.site.register(LeaseDraft)
admin.site.register(LeaseDraftPhoto)
