import json
import datetime

from django.shortcuts import render

from rest_framework import viewsets
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .objects import Home, Auto, Profile
from .serializers import OutputSerializer

current_year = datetime.datetime.now().year


class RiskProfileView(APIView):

    def post(self, request, format=None):

        def define_profile(data):

            age = data.get('age')
            houses = data.get('houses')
            income = data.get('income')
            vehicles = data.get('vehicles')
            dependents = data.get('dependents')
            marital_status = data.get('marital_status')
            risk_questions = data.get('risk_questions')

            base_score = 0

            for answer in risk_questions:
                base_score += answer

            self.life = base_score
            self.disability = base_score
            self.umbrella = base_score
            self.auto = []
            self.home = []

            for house in houses:
                self.home.append(base_score)

            for vehicle in vehicles:
                self.auto.append(base_score)

            def deduct_from_all(qty):
                if (self.life != None):
                    self.life = self.life - qty
                if (self.disability != None):
                    self.disability = self.disability - qty
                if (self.umbrella != None):
                    self.umbrella = self.umbrella - qty
                for index, score in enumerate(self.auto):
                    self.auto[index] = score - qty
                for index, score in enumerate(self.home):
                    self.home[index] = score - qty

            # Rule 1
            if (income == 0 or len(vehicles) == 0 or len(houses) == 0):
                self.disability = None
                self.auto = []
                self.home = []

            # Rule 2
            if (age > 60):
                self.disability = None
                self.life = None

            # Rule 3
            if (age < 30):
                deduct_from_all(2)
            elif (30 <= age < 40):
                deduct_from_all(1)

            # Rule 4
            if (income > 200000):
                deduct_from_all(1)

            # Rule 5
            has_mortgaged = False
            for house in houses:
                if (house['ownership_status'] == 'mortgaged'):
                    for index, score in enumerate(self.home):
                        if (house['key'] == index + 1):
                            self.home[index] = score + 1
                    if (not has_mortgaged):
                        if (self.disability != None):
                            self.disability = self.disability + 1
                        has_mortgaged = True

            # Rule 6
            if (dependents > 0):
                if (self.disability != None):
                    self.disability = self.disability + 1
                if (self.life != None):
                    self.life = self.life + 1

            # Rule 7
            if (marital_status == 'married'):
                if (self.life != None):
                    self.life = self.life + 1
                if (self.disability != None):
                    self.disability = self.disability - 1

            # Rule 8
            for vehicle in vehicles:
                if (vehicle['year'] >= current_year - 5):
                    for index, score in enumerate(self.auto):
                        if (vehicle['key'] == index + 1):
                            self.auto[index] = score + 1

            # Rule 9
            if (len(self.auto) > 0 and len(vehicles) == 1):
                self.auto[0] = self.auto[0] + 1
            if (len(self.home) > 0 and len(houses) == 1):
                self.home[0] = self.home[0] + 1

            # Mappings
            def map_to_plan(score):
                if (score <= 0):
                    return 'economic'
                elif (score == 1 or score == 2):
                    return 'regular'
                elif (score >= 3):
                    return 'responsible'

            def has_economic(items):
                flag = False
                for item in items:
                    if item <= 0:
                        flag = True
                return flag

            # Rule 10
            if (self.umbrella == None):
                self.umbrella = "ineligible"
            elif (self.life != None and self.disability != None):
                if (self.life <= 0 or self.disability <= 0 or has_economic(self.home) or has_economic(self.auto)):
                    self.umbrella = map_to_plan(self.umbrella)
                else:
                    self.umbrella = "ineligible"
            else:
                self.umbrella = "ineligible"

            for index, score in enumerate(self.auto):
                self.auto[index] = Auto(
                    key=index+1,
                    value=map_to_plan(score)).asdict()

            if (self.disability != None):
                self.disability = map_to_plan(self.disability)
            else:
                self.disability = "ineligible"

            for index, score in enumerate(self.home):
                self.home[index] = Home(
                    key=index+1,
                    value=map_to_plan(score)).asdict()

            if (self.life != None):
                self.life = map_to_plan(self.life)
            else:
                self.life = "ineligible"

            return Profile(auto=self.auto, disability=self.disability, home=self.home,
                           life=self.life, umbrella=self.umbrella)

        profile = define_profile(request.data)
        output = OutputSerializer(profile)
        result = OutputSerializer(data=output.data)

        if result.is_valid():
            result.save()
            return Response(result.data, status=status.HTTP_201_CREATED)
        else:
            return Response(result.data, status=status.HTTP_409_CONFLICT)
