from django.db import models


class Hvac(models.Model):
    """HVAC model, to handle all home devices"""
    equipment = models.CharField(max_length=200)
    description = models.CharField(max_length=200)

    def __str__(self):
        return self.description


class Command(models.Model):
    """Command model, traceability of commands issued"""

    hvac = models.ForeignKey(Hvac, on_delete=models.CASCADE)
    hvac_webid = models.CharField(max_length=200)
    room_temperature = models.FloatField()
    target_temperature = models.FloatField()
    fan_speed = models.CharField(max_length=10)
    mode = models.CharField(max_length=10)
    date_issued = models.DateTimeField('date issued')

    def __str__(self):
        return "%s - %s" % (self.date_issued, self.mode)
