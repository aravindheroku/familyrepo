from json import dump, loads
from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.

from . models import *
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
import json
from django.conf import settings
def readJsonFile():
    jsFile = open(settings.STATIC_ROOT+'/mydb.json',"r")
    jsData = jsFile.read()
     
    obj = json.loads(jsData)

    return obj

def writeJsonFile(obj):
    with open(settings.STATIC_ROOT+'/mydb.json',"w") as write:
        json.dump(obj,write)

@csrf_exempt
def addMembers(request):
    if request.method == 'POST':
        
        reqObj = request.POST
        
        
        try:
            obj = readJsonFile()
      
            mlist = obj['Members']
            plist = obj['Parents']
            clist = obj['Childrens']
            
            mlastId = mlist[-1]['id']
            plastId = plist[-1]['id']
            
            if len(clist) == 0:
                clastId = 0
            
            else:
                clastId = clist[-1]['id']
            
            mlist.append({'id':mlastId + 1,'name':reqObj['mname'],'address':reqObj['maddress'],'gender':reqObj['mgender']})
            obj['Members'] = mlist
            
            isParent = False

            if reqObj['mrelation'] == 'sw':
                isParent = False
                
                plist.append({'id':plastId + 1,'father':mlastId + 1,'mother':int(reqObj['mspouse'])})
                obj['Parents'] = plist

                

            elif reqObj['mrelation'] == 'dw':
                isParent = False
                
                plist.append({'id':plastId + 1,'father':int(reqObj['mspouse']),'mother': mlastId + 1})
                obj['Parents'] = plist

                
 
            else:
                clist.append({'id':clastId + 1,'fkParent':int(reqObj['mparent']),'fkChild':mlastId + 1})
                obj['Childrens'] = clist

                
            writeJsonFile(obj)
            
            mobj = Members(id = mlastId + 1,name = reqObj['mname'],address = reqObj['maddress'],gender = reqObj['mgender'])
            mobj.save()
            
            if isParent:
                
                spouse = Members.objects.get(id = reqObj['spouse'])
                
                pobj = Parent(id = plastId + 1, father = spouse,mother = mobj)
                pobj.save()

            pobj = Parent.objects.get(id = reqObj['mparent'])
            
            cobj = Childrens(id = clastId + 1, fkParent = pobj,fkChild = mobj)
            cobj.save()
            
            return JsonResponse({'message': 'Member Saved...'})
        
        except Exception as e:
            print(e)
            return JsonResponse({'message':str(e)})
    
    else:
        return render(request,'addMembers.html')


def clearModels():
    childrens = Childrens.objects.all()
    parents   = Parent.objects.all()
    members   = Members.objects.all()
    for obj in childrens:
        obj.delete()
    
    for obj in parents:
        obj.delete()
    
    for obj in members:
        obj.delete()
    
def createFamily():
    family = readJsonFile()

    members   = family['Members']
    parents   = family['Parents']
    childrens = family['Childrens']

    for obj in members:
        mobj = Members(id = obj['id'],name = obj['name'],address = obj['address'],gender = obj['gender'])
        mobj.save()

    for obj in parents:
        print(obj)
        fobj = Members.objects.get(id = obj['father'])

        print(fobj)
        mobj = Members.objects.get(id = obj['mother'])
       
        pobj = Parent(id = obj['id'],father = fobj,mother = mobj)
        pobj.save()
    
    if len(childrens) != 0:
        for obj in childrens:
            print(obj)
            pobj = Parent.objects.get(id = obj['fkParent'])
            mobj = Members.objects.get(id = obj['fkChild'])

            cobj = Childrens(id = obj['id'],fkParent = pobj,fkChild = mobj)
            cobj.save()

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
        clearModels()
        createFamily()
       
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