from django.db import models

# Create your models here.
from django.db import models

class UploadedFile(models.Model):
    CATEGORY_CHOICES = [
        ('1st_year/notes', '1st Year - Notes'),
        ('1st_year/pyqs', '1st Year - PYQs'),
        ('2nd_year/notes', '2nd Year - Notes'),
        ('2nd_year/pyqs', '2nd Year - PYQs'),
        ('3rd_year/notes', '3rd Year - Notes'),
        ('3rd_year/pyqs', '3rd Year - PYQs'),
        ('final_year/notes', 'Final Year - Notes'),
        ('final_year/pyqs', 'Final Year - PYQs'),
    ]

    file_name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    file_url = models.URLField()  # Store file URL from Firebase
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file_name
