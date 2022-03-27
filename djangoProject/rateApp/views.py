from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponse
from .models import Student, Professor, Module, Professor_Module, Rate
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import user_passes_test
from functools import wraps
import re

# Create your views here.



@csrf_exempt
def register(request):
    try:
        if request.session.get('is_login', None):
            return HttpResponse("You has logged in, register action is denied.")
        if request.method == "POST":
            username = request.POST["username"]
            email = request.POST["email"]
            password = request.POST["password"]
            passwordAgain = request.POST["passwordAgain"]
            if password != passwordAgain:
                return HttpResponse("You must input the same password.")
            if Student.objects.filter(username=username):
                return  HttpResponse("Username is taken.")
            if len(username) == 0 or len(username)>20:
                return  HttpResponse("Username should contain 1~20 characters.")
            if Student.objects.filter(email=email):
                return HttpResponse("Email is taken.")
            if len(password)<6 or len(password)>20:
                return  HttpResponse("Password should contain 6~20 characters.")
            newUser = Student.objects.create(username=username,
                                             email=email,
                                             password=password)
            newUser.save()
            return HttpResponse("")

    except Exception as e:
        print(e)
        return HttpResponse("Something went wrong!")


@csrf_exempt
def login(request):
    try:
        if request.session.get('is_login', None):
            return HttpResponse("You has logged in, register action is denied.")
        username = request.POST["username"]
        password = request.POST["password"]
        user = Student.objects.filter(username=username)
        if user:
            if user.filter(password=password):
                request.session["is_login"] = True
                request.session["logged_user"] = username
                return HttpResponse("")
            else:
                return HttpResponse("Wrong password!")
        else:
            return HttpResponse("User does not exist!")

    except Exception as e:
        print(e)
        return HttpResponse("Something went wrong!")


@csrf_exempt
def logout(request):
    try:
        if not request.session.get('is_login', None):
            return HttpResponse("You should login first.")
        request.session.flush()
        return HttpResponse("")
    except Exception as e:
        print(e)
        return HttpResponse("Something went wrong!")

@csrf_exempt
def checkStatus(request):
    try:
        if request.session.get('is_login', None):
            return HttpResponse(request.session["logged_user"])
        else:
            return HttpResponse("")
    except Exception as e:
        print(e)
        return HttpResponse("Something went wrong!")


@csrf_exempt
def list(request):
    try:
        if not request.session.get('is_login', None):
            return HttpResponse("You should login first.")
        return HttpResponse("\n".join([str(i) for i in Professor_Module.objects.all()]))
    except Exception as e:
        print(e)
        return HttpResponse("Something went wrong!")


@csrf_exempt
def view(request):
    try:
        if not request.session.get('is_login', None):
            return HttpResponse("You should login first.")
        allProfessors = Professor.objects.all()
        if len(allProfessors) == 0:
            return HttpResponse("No professor record in the database!")
        allRating = Rate.objects.all()
        if len(allRating) == 0:
            return HttpResponse("No rating record in the database!")
        ratingList = []
        for oneProfessor in allProfessors:
            ratedRecord = Rate.objects.filter(professor=oneProfessor)
            recordNum = len(ratedRecord)
            if recordNum == 0:
                ratingList.append("No rating record for Professor "+oneProfessor.name+"("+oneProfessor.professorcode+")")
            else:
                scoreAll = 0
                for i in ratedRecord:
                    scoreAll += i.ratingScore
                averageRating = round(scoreAll/recordNum)
                stars = averageRating * "*"
                message = "The rating of Professor "+oneProfessor.name+"("+oneProfessor.professorcode+") is "+stars
                ratingList.append(message)
        return HttpResponse("\n".join([i for i in ratingList]))

    except Exception as e:
        print(e)
        return HttpResponse("Something went wrong!")

@csrf_exempt
def average(request):
    try:
        pId = request.POST["professorcode"]
        mId = request.POST["modulecode"]
        professor = Professor.objects.filter(professorcode=pId)
        if len(professor) == 0:
            return HttpResponse("Fake Professor Id!")
        module = Module.objects.filter(modulecode=mId)
        if len(module) == 0:
            return HttpResponse("No such module!")
        moduleInstance = Professor_Module.objects.filter(module=module[0])
        if len(moduleInstance) == 0:
            return HttpResponse("No module instance found for the given module id!")
        instanceList = []
        for m in range(len(moduleInstance)):
            for n in moduleInstance[m].professors.all():
                if n.professorcode == pId:
                    instanceList.append(moduleInstance[m])
                    break
        if len(instanceList) == 0:
            return HttpResponse("Professor "+professor[0].name+"("+professor[0].professorcode+") "+
                                " has no module instance for the module "+module[0].name+"("+module[0].modulecode+")!")

        totalRatingNum = 0
        totalRatingScore = 0
        for instance in instanceList:
            ratingInstance = Rate.objects.filter(module=instance).filter(professor=professor[0])
            totalRatingNum += len(ratingInstance)
            for i in ratingInstance:
                totalRatingScore += i.ratingScore

        if totalRatingNum == 0:
            return HttpResponse("No rating record for the Professor"+professor[0].name+"("+professor[0].professorcode+") "+
                                "in the module "+module[0].name+"("+module[0].modulecode+")!")
        averageRating = round(totalRatingScore / totalRatingNum)
        stars = averageRating * "*"
        return HttpResponse("The rating of " + "Professor " + professor[0].name + "(" + professor[0].professorcode + ") "
                            + "in module " +module[0].name+"("+module[0].modulecode+") "+ "is " + stars)

    except Exception as e:
        print(e)
        return HttpResponse("Something went wrong!")



@csrf_exempt
def rate(request):
    try:
        if not request.session.get('is_login', None):
            return HttpResponse("You should login first.")
        professorcode = request.POST["professorcode"]
        modulecode = request.POST["modulecode"]
        year = request.POST["year"]
        semester = request.POST["semester"]
        rating = request.POST["rating"]
        if not year.isnumeric():
            return HttpResponse("The year must be a number!")
        year = eval(year)
        if isinstance(year,float):
            return HttpResponse("The year must be an integer!")
        if not semester.isnumeric():
            return HttpResponse("The semester must be a number!")
        semester = eval(semester)
        if isinstance(semester, float):
            return HttpResponse("The semester must be an integer!")
        if semester<1 or semester>2:
            return HttpResponse("Thw semester must be 1 or 2!")
        professor = Professor.objects.filter(professorcode=professorcode)
        module = Professor_Module.objects.filter(module=modulecode).filter(year=year).filter(semester=semester)
        if not len(module):
            return HttpResponse("NO such module instance!")
        if not len(professor):
            return HttpResponse("Fake Professor Id!")
        if not rating.isnumeric():
            return HttpResponse("The rating score must be a number!")
        rating = eval(rating)
        if isinstance(rating,float):
            return HttpResponse("The rating score must be an integer!")
        if rating<1 or rating>5:
            return HttpResponse("Thw rating score must be 1~5!")

        findProfessor = False
        for m in range(len(module)):
            for n in module[m].professors.all():
                if n.professorcode == professorcode:
                    professor = n
                    findProfessor = True
                    break
            if findProfessor:
                break
        if not findProfessor:
            return HttpResponse("This module is not taught by the Professor "+professor[0].name)
        moduleInstance = module[m]
        student = Student.objects.filter(username=request.session["logged_user"])[0]
        ratingCase = Rate.objects.filter(student=student).filter(professor=professor).filter(module=moduleInstance)
        if len(ratingCase):
            ratingCase[0].ratingScore=rating
            ratingCase[0].save()
            return HttpResponse("You have change your rating successfully!")
        newRatingCase = Rate.objects.create(student=student,
                                            professor=professor,
                                            module=moduleInstance,
                                            ratingScore=rating)
        newRatingCase.save()
        return HttpResponse("New Rate Successfully!")

    except Exception as e:
        print(e)
        return HttpResponse("Something went wrong!")