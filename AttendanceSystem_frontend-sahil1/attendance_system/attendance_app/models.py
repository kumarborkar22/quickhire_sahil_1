from django.db import models

class Attendance(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="attendance_images/")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.timestamp}"