from datetime import date

from django.db import models

class LineItem(models.Model):
    category = models.CharField(max_length=50, default="other")
    date = models.DateField(default=date.today)
    credit_amount = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    debit_amount = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    name = models.CharField(max_length=200)

    def __str__(self):
        return "{0.name}: ${1} [{0.category}]".format(
            self, self.credit_amount - self.debit_amount)
