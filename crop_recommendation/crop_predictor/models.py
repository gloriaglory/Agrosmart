from django.db import models

class ClimateCondition(models.Model):
    temperature = models.FloatField()  # in Celsius
    humidity = models.FloatField()     # in percentage
    rainfall = models.FloatField()     # in mm

    def __str__(self):
        return f"Temp: {self.temperature}°C, Humidity: {self.humidity}%, Rainfall: {self.rainfall}mm"

class SoilType(models.Model):
    soil_ph = models.FloatField()
    soil_texture = models.CharField(max_length=100)  # e.g., clay, loam, sand
    soil_moisture = models.FloatField()  # in percentage

    def __str__(self):
        return f"Soil pH: {self.soil_ph}, Texture: {self.soil_texture}"

class CropRecommendation(models.Model):
    crop_name = models.CharField(max_length=100)
    optimal_temperature_min = models.FloatField()
    optimal_temperature_max = models.FloatField()
    optimal_humidity_min = models.FloatField()
    optimal_humidity_max = models.FloatField()
    optimal_rainfall_min = models.FloatField()
    optimal_rainfall_max = models.FloatField()
    soil_type = models.CharField(max_length=100)  # Corresponding soil types for crops

    def __str__(self):
        return f"Crop: {self.crop_name}"
