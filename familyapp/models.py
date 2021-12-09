from django.db import models

# Create your models here.

class Members(models.Model):
    name    = models.CharField(max_length = 50)
    address = models.CharField(max_length = 100, default = 'N')
    gender   = models.CharField(max_length = 2,default = 'F')

class Parent(models.Model):
    father  = models.ForeignKey(Members,on_delete = models.CASCADE,related_name = 'member11')
    mother  = models.ForeignKey(Members,on_delete = models.CASCADE,related_name = 'member2')
    
class Childrens(models.Model):
    fkParent = models.ForeignKey(Parent,on_delete = models.CASCADE)
    fkChild  = models.ForeignKey(Members,on_delete = models.CASCADE)
    
    
    