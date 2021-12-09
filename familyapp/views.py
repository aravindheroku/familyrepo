from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.

from . models import *
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def addMembers(request):
    if request.method == 'POST':
        reqObj = request.POST
        print(reqObj)
        try:

            parent = Parent.objects.get(id = reqObj['mparent'])
            
            if reqObj['maddress'] == '':
                address = 'N'
            else:
                address = reqObj['maddress']
            memObj = Members(name = reqObj['mname'],address = address,gender = reqObj['mgender'])
            memObj.save()
            
            if reqObj['mrelation'] == 'sw' or reqObj['mrelation'] == 'dw':
                child = Members.objects.get(id = reqObj['mspouse'])
                if child.gender == 'F':
                    parentObj = Parent(father = memObj,mother = child)
                
                else:
                    parentObj = Parent(father = child,mother = memObj)
                parentObj.save()
            
            else:

                childObj = Childrens(fkParent = parent,fkChild = memObj)
                childObj.save()
            
            return JsonResponse({'message': 'Member Saved...'})
        except Exception as e:
            print(e)
            return JsonResponse({'message':str(e)})
    
    else:
        return render(request,'addMembers.html')


def viewFamily(request):
    family = []
    if request.method == 'POST':
        print(request.POST)
        parent = request.POST['parent']
        
        generations = Childrens.objects.filter(fkParent__id = parent)
        # print(generations)
        for obj in generations:
            isParent = Parent.objects.filter(Q(father = obj.fkChild.id) | Q(mother = obj.fkChild.id)).exists()
            print(isParent)
            if isParent:
                
                if obj.fkChild.gender == 'M':
                    parentObj = Parent.objects.get(father = obj.fkChild.id)
                    familyObj = {
                        "id"      : parentObj.id,
                        "child"   : parentObj.father.name,
                        "inlaw"   : parentObj.mother.name,       
                        "inaddress" : parentObj.mother.address, 
                    }

                    childExist = Childrens.objects.filter(fkParent = parentObj).exists()
                    if childExist == False:
                        familyObj['completed'] = True

                else:
                    parentObj = Parent.objects.get(mother = obj.fkChild.id)

                    familyObj = {
                        "id"        : parentObj.id,
                        "child"     : parentObj.mother.name,
                        "inlaw"     : parentObj.father.name,
                        "inaddress" : parentObj.father.address,         
                    }

                    childExist = Childrens.objects.filter(fkParent = parentObj).exists()

                    if childExist == False:
                        familyObj['completed'] = True
            else:
                
                familyObj = {
                    "id"        : obj.id,
                    "child"     : obj.fkChild.name,
                    'completed' : True
                }
            family.append(familyObj)

        return render(request,'family.html',{"initial" : False,"familyDict":family})
    
    else:
        parentObj = Parent.objects.order_by('id').first()
    
    
        familyObj = {
            "id"        : parentObj.id,
            "child"     : parentObj.father.name,
            "inlaw"     : parentObj.mother.name,     
            "inaddress" : parentObj.mother.address,  
            }
        
        family.append(familyObj)
        return render(request,'family.html',{"initial" : True,"familyDict":family})


def getParents(request):
    key = request.GET['skey']
    print(key)
    parentObj = Parent.objects.filter(Q(father__name__contains = key) | Q(mother__name__contains = key))
    print(parentObj)
    parentList = []
    for obj in parentObj:
        
        pObj = {
            "id":obj.id,
            "pname":obj.father.name + '( '+ obj.father.address +' ) & ' + obj.mother.name + '( '+ obj.mother.address +' )'
        }
        print(pObj)
        parentList.append(pObj)
    
    return JsonResponse({"response":parentList})

def getSpouse(request):
    reqObj = request.GET
    print(reqObj)
    parent   = reqObj['pid']
    relation = reqObj['relation']

    if relation == 'sw':
        gender = 'F'
    
    else:
        gender = 'M'
    
    cObjs = Childrens.objects.filter(Q(fkParent__id = parent) & Q (fkChild__gender = gender))
    print(cObjs)
    spouseList = []
    
    for obj in cObjs:
        isParent = Parent.objects.filter(Q(father = obj.fkChild) | Q(mother = obj.fkChild)).exists()
        print(isParent)
        if isParent == False:
            spObj = {
                "id":obj.fkChild.id,
                "name":obj.fkChild.name + ' ( '+ obj.fkChild.address + ' )'
            }
            spouseList.append(spObj)
    
    return JsonResponse({"response":spouseList})