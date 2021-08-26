from django.db import models


class CategoriesManager(models.Manager):
    def is_category_existed(self, category_id):
        return self.filter(id=category_id).exists()


class CategoriesModel(models.Model):
    category_name = models.CharField(max_length=64, null=False)
    objects = CategoriesManager()

    def __str__(self):
        return self.category_name

    class Meta:
        db_table = "categories_tb"
