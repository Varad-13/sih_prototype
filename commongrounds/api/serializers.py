from rest_framework import serializers
from core.models import Userprofile, Service, Venue, Image, Timings, Locality, State, ServiceTypes

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'file']

class TimingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timings
        fields = ['id', 'daysofweek', 'starthour', 'endhour']

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['id', 'state_name', 'state_code']

class LocalitySerializer(serializers.ModelSerializer):
    state = StateSerializer()
    
    class Meta:
        model = Locality
        fields = ['id', 'postcode', 'place_name', 'state']

class ServiceTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceTypes
        fields = ['id', 'service_name', 'service_category']

class UserprofileSerializer(serializers.ModelSerializer):
    profile_image = ImageSerializer()
    
    class Meta:
        model = Userprofile
        fields = ['id', 'user', 'profile_image', 'bio', 'user_type']

    def create(self, validated_data):
        profile_image_data = validated_data.pop('profile_image')
        profile_image, created = Image.objects.get_or_create(**profile_image_data)
        userprofile = Userprofile.objects.create(profile_image=profile_image, **validated_data)
        return userprofile

    def update(self, instance, validated_data):
        profile_image_data = validated_data.pop('profile_image')
        profile_image, created = Image.objects.get_or_create(**profile_image_data)
        instance.profile_image = profile_image
        instance.bio = validated_data.get('bio', instance.bio)
        instance.user_type = validated_data.get('user_type', instance.user_type)
        instance.save()
        return instance

class ServiceSerializer(serializers.ModelSerializer):
    service_type = ServiceTypesSerializer()
    provider = UserprofileSerializer()
    timings = TimingsSerializer()
    locality = LocalitySerializer()

    class Meta:
        model = Service
        fields = ['id', 'service_type', 'provider', 'description', 'timings', 'rate', 'locality']

    def create(self, validated_data):
        service_type_data = validated_data.pop('service_type')
        service_type, created = ServiceTypes.objects.get_or_create(**service_type_data)

        provider_data = validated_data.pop('provider')
        provider, created = Userprofile.objects.get_or_create(**provider_data)

        timings_data = validated_data.pop('timings')
        timings, created = Timings.objects.get_or_create(**timings_data)

        locality_data = validated_data.pop('locality')
        locality, created = Locality.objects.get_or_create(**locality_data)

        service = Service.objects.create(service_type=service_type, provider=provider, timings=timings, locality=locality, **validated_data)
        return service

    def update(self, instance, validated_data):
        service_type_data = validated_data.pop('service_type')
        service_type, created = ServiceTypes.objects.get_or_create(**service_type_data)
        instance.service_type = service_type

        provider_data = validated_data.pop('provider')
        provider, created = Userprofile.objects.get_or_create(**provider_data)
        instance.provider = provider

        timings_data = validated_data.pop('timings')
        timings, created = Timings.objects.get_or_create(**timings_data)
        instance.timings = timings

        locality_data = validated_data.pop('locality')
        locality, created = Locality.objects.get_or_create(**locality_data)
        instance.locality = locality

        instance.description = validated_data.get('description', instance.description)
        instance.rate = validated_data.get('rate', instance.rate)
        instance.save()
        return instance

class VenueSerializer(serializers.ModelSerializer):
    venue_images = ImageSerializer(many=True)
    timings = TimingsSerializer()
    locality = LocalitySerializer()

    class Meta:
        model = Venue
        fields = ['id', 'venue_name', 'venue_images', 'timings', 'description', 'rate', 'locality']

    def create(self, validated_data):
        venue_images_data = validated_data.pop('venue_images')
        venue_images = []
        for image_data in venue_images_data:
            image, created = Image.objects.get_or_create(**image_data)
            venue_images.append(image)

        timings_data = validated_data.pop('timings')
        timings, created = Timings.objects.get_or_create(**timings_data)

        locality_data = validated_data.pop('locality')
        locality, created = Locality.objects.get_or_create(**locality_data)

        venue = Venue.objects.create(timings=timings, locality=locality, **validated_data)
        venue.venue_images.set(venue_images)
        return venue

    def update(self, instance, validated_data):
        venue_images_data = validated_data.pop('venue_images')
        venue_images = []
        for image_data in venue_images_data:
            image, created = Image.objects.get_or_create(**image_data)
            venue_images.append(image)
        instance.venue_images.set(venue_images)

        timings_data = validated_data.pop('timings')
        timings, created = Timings.objects.get_or_create(**timings_data)
        instance.timings = timings

        locality_data = validated_data.pop('locality')
        locality, created = Locality.objects.get_or_create(**locality_data)
        instance.locality = locality

        instance.venue_name = validated_data.get('venue_name', instance.venue_name)
        instance.description = validated_data.get('description', instance.description)
        instance.rate = validated_data.get('rate', instance.rate)
        instance.save()
        return instance
