from django.db import models

# Create your models here.
class Student(models.Model):
    username = models.CharField(max_length=20, unique=True)
    email = models.EmailField(max_length=30, unique=True)
    password = models.CharField(max_length=20)

    def __str__(self):
        return str(self.username)

class Professor(models.Model):
    professorcode = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=30)

    def __str__(self):
        return str(self.professorcode + ", Professor " + self.name)

class Module(models.Model):
    modulecode = models.CharField(max_length=30, primary_key=True)
    name = models.CharField(max_length=30)
    content = models.CharField(max_length=100)


    def __str__(self):
        return str(self.modulecode + ": " + self.name)

class Professor_Module(models.Model):
    year = []
    for j in range(2000,2500):
        year.append((j, j))
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    professors = models.ManyToManyField(Professor)
    year = models.IntegerField(choices=year)
    semester = models.IntegerField(choices=[(1, 'First Semester'), (2, "Second Semester")])

    def __str__(self):
        return str(self.module.modulecode)+": "+str(self.module.name)+", "\
               +"Year: "+str(self.year)+", Semester:"+str(self.semester)+", taught by "\
               +", ".join([str(i.professorcode)+", Professor "+str(i.name) for i in self.professors.all()])




class Rate(models.Model):
    score = []
    for j in range(1,6):
        score.append((j,j))
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
    module = models.ForeignKey(Professor_Module, on_delete=models.CASCADE)
    ratingScore = models.IntegerField(choices=score)

    def __str__(self):
        return str(self.module.module.modulecode)+": "+str(self.module.module.name)+", "\
               +"Year: "+str(self.module.year)+", Semester:"+str(self.module.semester)+", taught by "\
               +str(self.professor.professorcode)+", Professor "+str(self.professor.name)+" is rated "\
               +str(self.ratingScore)+" by Student "+str(self.student.username)



