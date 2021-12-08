from django.shortcuts import render

# Create your views here.

from . models import *

def addMembers(request):
    reqObj = request.POST['requestData']

def viewFamily(request):
    family = []
    if request.method == 'POST':
        print(request.POST)
        parent = request.POST['parent']
        
        generations = Childrens.objects.filter(fkParent__id = parent)
        # print(generations)
        for obj in generations:
            
            if obj.gender == 'M':
                parentObj = Parent.objects.get(father = obj.fkChild.id)
                familyObj = {
                    "id"      : parentObj.id,
                    "child"   : parentObj.father.name,
                    "inlaw"   : parentObj.mother.name       
                }
                
                childExist = Childrens.objects.filter(fkParent = parentObj).exists()
                if childExist == False:
                    familyObj['completed'] = True

            else:
                parentObj = Parent.objects.get(mother = obj.fkChild.id)

                familyObj = {
                    "id"      : parentObj.id,
                    "child"   : parentObj.mother.name,
                    "inlaw"   : parentObj.father.name       
                }
                
                childExist = Childrens.objects.filter(fkParent = parentObj).exists()
                
                if childExist == False:
                    familyObj['completed'] = True

            family.append(familyObj)

        return render(request,'family.html',{"initial" : False,"familyDict":family})
    
    else:
        parentObj = Parent.objects.get(id = 1)
    
    
        familyObj = {
            "id"      : parentObj.id,
            "child"   : parentObj.father.name,
            "inlaw"   : parentObj.mother.name       
            }
        
        family.append(familyObj)
        return render(request,'family.html',{"initial" : True,"familyDict":family})
