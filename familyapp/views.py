from json import dump, loads
from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.

from . models import *
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
import json

# def readJsonFile():
#     jsFile = open(settings.STATIC_ROOT+'/mydb.json',"r")
#     jsData = jsFile.read()
     
#     obj = json.loads(jsData)

#     return obj

# def writeJsonFile(obj):
#     with open(settings.STATIC_ROOT+'/mydb.json',"w") as write:
#         json.dump(obj,write)

@csrf_exempt
def addMembers(request):
    if request.method == 'POST':
        
        reqObj = request.POST
        
        
        try:
            # obj = readJsonFile()
      
            # mlist = obj['Members']
            # plist = obj['Parents']
            # clist = obj['Childrens']
            
            # mlastId = mlist[-1]['id']
            # plastId = plist[-1]['id']
            
            # if len(clist) == 0:
            #     clastId = 0
            
            # else:
            #     clastId = clist[-1]['id']
            
            # mlist.append({'id':mlastId + 1,'name':reqObj['mname'],'address':reqObj['maddress'],'gender':reqObj['mgender']})
            # obj['Members'] = mlist
            
            isParent = False

            if reqObj['mrelation'] == 'sw' or  reqObj['mrelation'] == 'dw':
                isParent = True
                
                # plist.append({'id':plastId + 1,'father':mlastId + 1,'mother':int(reqObj['mspouse'])})
                # obj['Parents'] = plist

                
                # plist.append({'id':plastId + 1,'father':int(reqObj['mspouse']),'mother': mlastId + 1})
                # obj['Parents'] = plist

                
 
            #else:
                # clist.append({'id':clastId + 1,'fkParent':int(reqObj['mparent']),'fkChild':mlastId + 1})
                # obj['Childrens'] = clist

                
            # writeJsonFile(obj)
            
            # mobj = Members(id = mlastId + 1,name = reqObj['mname'],address = reqObj['maddress'],gender = reqObj['mgender'])
            # mobj.save()

            mobj = Members(name = reqObj['mname'],address = reqObj['maddress'],gender = reqObj['mgender'])
            mobj.save()
            
            if isParent:
                
                spouse = Members.objects.get(id = reqObj['mspouse'])
                
                # pobj = Parent(id = plastId + 1, father = spouse,mother = mobj)
                # pobj.save()
                
                if spouse.gender == 'F':

                    pobj = Parent(father = mobj,mother = spouse)
                    pobj.save()
                
                else:
                    pobj = Parent(father = spouse,mother = mobj)
                    pobj.save()

            else:

                pobj = Parent.objects.get(id = reqObj['mparent'])
            
            # cobj = Childrens(id = clastId + 1, fkParent = pobj,fkChild = mobj)
            # cobj.save()

                cobj = Childrens(fkParent = pobj,fkChild = mobj)
                cobj.save()
            
            return JsonResponse({'message': 'Member Saved...'})
        
        except Exception as e:
            print(e)
            return JsonResponse({'message':str(e)})
    
    else:
        return render(request,'addMembers.html')


# def clearModels():
#     childrens = Childrens.objects.all()
#     parents   = Parent.objects.all()
#     members   = Members.objects.all()
#     for obj in childrens:
#         obj.delete()
    
#     for obj in parents:
#         obj.delete()
    
#     for obj in members:
#         obj.delete()
    
# def createFamily():
#     family = readJsonFile()

#     members   = family['Members']
#     parents   = family['Parents']
#     childrens = family['Childrens']

#     for obj in members:
#         mobj = Members(id = obj['id'],name = obj['name'],address = obj['address'],gender = obj['gender'])
#         mobj.save()

#     for obj in parents:
        
#         fobj = Members.objects.get(id = obj['father'])

        
#         mobj = Members.objects.get(id = obj['mother'])
       
#         pobj = Parent(id = obj['id'],father = fobj,mother = mobj)
#         pobj.save()
    
#     if len(childrens) != 0:
#         for obj in childrens:
            
#             pobj = Parent.objects.get(id = obj['fkParent'])
#             mobj = Members.objects.get(id = obj['fkChild'])

#             cobj = Childrens(id = obj['id'],fkParent = pobj,fkChild = mobj)
#             cobj.save()

def viewFamily(request):
    family = []
    if request.method == 'POST':
        
        parent = request.POST['parent']
        
        generations = Childrens.objects.filter(fkParent__id = parent)
        # print(generations)
        for obj in generations:
            isParent = Parent.objects.filter(Q(father = obj.fkChild.id) | Q(mother = obj.fkChild.id)).exists()
            
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
        # clearModels()
        # createFamily()
       
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
    
    parentObj = Parent.objects.filter(Q(father__name__contains = key) | Q(mother__name__contains = key))
    
    parentList = []
    for obj in parentObj:
        
        pObj = {
            "id":obj.id,
            "pname":obj.father.name + '( '+ obj.father.address +' ) & ' + obj.mother.name + '( '+ obj.mother.address +' )'
        }
        
        parentList.append(pObj)
    
    return JsonResponse({"response":parentList})

def getSpouse(request):
    reqObj = request.GET
    
    parent   = reqObj['pid']
    relation = reqObj['relation']

    if relation == 'sw':
        gender = 'F'
    
    else:
        gender = 'M'
    
    cObjs = Childrens.objects.filter(Q(fkParent__id = parent) & Q (fkChild__gender = gender))
    
    spouseList = []
    
    for obj in cObjs:
        isParent = Parent.objects.filter(Q(father = obj.fkChild) | Q(mother = obj.fkChild)).exists()
        
        if isParent == False:
            spObj = {
                "id":obj.fkChild.id,
                "name":obj.fkChild.name + ' ( '+ obj.fkChild.address + ' )'
            }
            spouseList.append(spObj)
    
    return JsonResponse({"response":spouseList})

@csrf_exempt
def editMember(request):
    # family = readJsonFile()
    
    if request.method == 'POST':
        reqObj = request.POST
        print(reqObj)
        
        memberObj = Members.objects.get(id = reqObj['mid'])
        memberObj.name    = reqObj['mname']
        memberObj.address = reqObj['maddress']
        memberObj.gender  = reqObj['mgender']
        
        memberObj.save()
        
        
        
        if reqObj['mspouse'] != '0':
           
            spouseObj = Members.objects.get(id = reqObj['mspouse'])
            
            if memberObj.gender == 'F':
                mexist = Parent.objects.filter(mother = reqObj['mid']).exists()
               
                
                if mexist:
                   
                    pobj = Parent.objects.get(mother = reqObj['mid'])
                    pobj.father = spouseObj
                    pobj.save()
                
                else:
                    pobj = Parent(father = spouseObj,mother = memberObj)
                    pobj.save()
            
            else:
                mexist = Parent.objects.filter(father = reqObj['mid']).exists()
                
                if mexist:
                  
                    pobj = Parent.objects.get(father = reqObj['mid'])
                    pobj.mother = spouseObj
                    pobj.save()
                else:
                    pobj = Parent(father = memberObj,mother = spouseObj)
                    pobj.save()
            # for pobj in family['Parents']:
                
            #     if reqObj['mid'] == pobj['father']:
                    
            #         pobj['father'] = reqObj['mid']
            #         pobj['mother'] = reqObj['mspouse']
                
            #     else:
            #         pobj['father'] = reqObj['mspouse']
            #         pobj['mother'] = reqObj['mid']
                  
        if reqObj['mrelation'] == 'sn' or reqObj['mrelation'] == 'dr':

            cobj = Childrens.objects.get(fkChild = reqObj['mid'])
            pobj = Parent.objects.get(id =  reqObj['mparent'])
            cobj.fkParent = pobj
            cobj.save()
        else:
            isExists = Childrens.objects.filter(fkChild = reqObj['mid']).exists()
            if isExists:

                cobj = Childrens.objects.get(fkChild = reqObj['mid'])
                cobj.delete()

        return JsonResponse({'response':True,'message':"updated"})
    
    else:
        return render(request,'edit.html')



def getMembers(request):
    key = request.GET['skey']
    
    try:

        memObj = Members.objects.filter(name__contains = key)
        
        memberList = []
        for obj in memObj:
            
            mObj = {
                "id":obj.id,
                "name":obj.name,
                "gender":obj.gender,
                "address":obj.address,
                
            }
            
            childObj = Childrens.objects.filter(fkChild = obj)

            if len(childObj) > 0:
                
                cobj = childObj[0]
                mObj['pname'] = cobj.fkParent.father.name + '( '+ cobj.fkParent.father.address +' ) & ' + cobj.fkParent.mother.name + '( '+ cobj.fkParent.mother.address +' )'
                mObj['pID'] = cobj.fkParent.id
                
                if obj.gender == 'F':
                    mObj['relation'] = 'dr'
                    isParent = Parent.objects.filter(mother = obj).exists()
                    if isParent:
                        parentObj = Parent.objects.get(mother = obj)
                        mObj['spouse'] = parentObj.father.name
                        mObj['spouseId'] = parentObj.father.id
                    
                
                else:
                    mObj['relation'] = 'sn'
                    
                    isParent = Parent.objects.filter(father = obj).exists()
                    if isParent:
                        parentObj = Parent.objects.get(father = obj)
                        mObj['spouse'] = parentObj.father.name
                        mObj['spouseId'] = parentObj.father.id
                    
            
            else:
                
                if obj.gender == 'F':
                    parentObj = Parent.objects.get(mother = obj)

                    childObj = Childrens.objects.get(fkChild = parentObj.father.id)
                    mObj['relation'] = 'dw'
                    mObj['spouse'] = parentObj.father.name
                    mObj['spouseId'] = parentObj.father.id
                    mObj['pname'] = childObj.fkParent.father.name + '( '+ childObj.fkParent.father.address +' ) & ' + childObj.fkParent.mother.name + '( '+ childObj.fkParent.mother.address +' )'
                    mObj['pID'] = childObj.fkParent.id
                
                else:
                    parentObj = Parent.objects.get(father = obj)
                    childObj = Childrens.objects.get(fkChild = parentObj.mother.id)
                    mObj['relation'] = 'sw'
                    mObj['spouse'] = parentObj.mother.name
                    mObj['spouseId'] = parentObj.mother.id
                    mObj['pname'] = childObj.fkParent.father.name + '( '+ childObj.fkParent.father.address +' ) & ' + childObj.fkParent.mother.name + '( '+ childObj.fkParent.mother.address +' )'
                    mObj['pID'] = childObj.fkParent.id
           
            memberList.append(mObj)
     
        return JsonResponse({"response":memberList})
    except Exception as e:
        print(e)
        return JsonResponse({"response":memberList,'message':str(e)})
    
    