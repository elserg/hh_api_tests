# -*- coding: utf-8 -*-

import os
import io
import json
import requests
import unittest
import jsonschema
import HtmlTestRunner


base_api_url = "https://api.hh.ru"

del_request = {'errors': [{'type': 'method_not_allowed'}]}

def send_request(request, data=None):
    r = requests.get(request, params=data)
    return r.json()

def send_delete(request, data=None):
    r = requests.delete(request, params=data)
    return r.json()

def is_none(instance):
    return instance is None

def is_myinteger(instance):
    val = None
    try:
        val = int(instance)
    except:
        pass
    return isinstance(val, int)

def get_schema_validator(schema_name):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(script_dir, schema_name)) as json_data:
        schema = json.load(json_data)
    checker = jsonschema.FormatChecker()
    checker.checks('none')(is_none)
    checker.checks('myinteger')(is_myinteger)
    validator = jsonschema.Draft4Validator(schema, format_checker=checker)
    return validator

def get_id_by_country_name(name):
    countries = send_request(base_api_url + "/areas/countries")
    for country in countries:
        if country['name'] == name:
            return country['id']



class TestRequests(unittest.TestCase):

    def test_areas_schema(self):
        # Запрос доступных стран /ar​eas
        resp = send_request(base_api_url + "/areas")
        validator = get_schema_validator('schema_areas.json')
        errors = list(validator.iter_errors(resp))
        self.assertFalse(errors, errors)

    def test_delete_areas(self):
        resp = send_delete(base_api_url + "/areas")
        self.assertEqual(resp, del_request)

    def test_employers_schema(self):

        # Запрос поиск ​по компаниям с указанием региона поиска(Россия), по строке "Новые Облачные Технологии"
        russia_id = get_id_by_country_name("Россия")
        resp = send_request(base_api_url + "/employers", data = {'text':'Новые Облачные Технологии', 'area':russia_id})

        validator = get_schema_validator('schema_employers.json')
        errors = list(validator.iter_errors(resp))
        self.assertFalse(errors, errors)

    def test_delete_employer(self):
        russia_id = get_id_by_country_name("Россия")
        resp = send_delete(base_api_url + "/employers", data = {'text':'Новые Облачные Технологии', 'area':russia_id})
        self.assertEqual(resp, del_request)

    def test_vacancies_schema(self):
        # Запрос наличия вакансии "QA Automation Engineer" у компании "Новые Облачные Технологии" в регионе "Санкт-Петербург"
        russia_id = get_id_by_country_name("Россия")
        russia_country = send_request(base_api_url + "/areas/{}".format(russia_id))
        spb_id = None
        for area in russia_country['areas']:
            if area['name'] == "Санкт-Петербург":
                spb_id = area['id']
                break        
        new_cloud_tech = send_request(base_api_url + "/employers", data = {'text':'Новые Облачные Технологии', 'area':russia_id})
        new_cloud_tech_id = new_cloud_tech['items'][0]['id']

        resp = send_request(base_api_url + "/vacancies", data = {'text':'QA A​utomation Engineer', 'area':spb_id, 'employer_id':new_cloud_tech_id})
        validator = get_schema_validator('schema_vacancies.json')
        errors = list(validator.iter_errors(resp))
        self.assertFalse(errors, errors)

    def test_delete_vacancies(self):
        russia_id = get_id_by_country_name("Россия")
        russia_country = send_request(base_api_url + "/areas/{}".format(russia_id))
        spb_id = None
        for area in russia_country['areas']:
            if area['name'] == "Санкт-Петербург":
                spb_id = area['id']
                break       
        new_cloud_tech = send_request(base_api_url + "/employers", data = {'text':'Новые Облачные Технологии', 'area':russia_id})
        new_cloud_tech_id = new_cloud_tech['items'][0]['id']

        resp = send_delete(base_api_url + "/vacancies", data = {'text':'QA A​utomation Engineer', 'area':spb_id, 'employer_id':new_cloud_tech_id})
        self.assertEqual(resp, del_request)

class Test_HTMLTestRunner(unittest.TestCase):

    def test_main(self):
        self.suite = unittest.TestSuite()
        self.suite.addTests([unittest.defaultTestLoader.loadTestsFromTestCase(TestRequests)])
        buf = io.StringIO()

        runner = HtmlTestRunner.HTMLTestRunner(
                    stream=buf,
                    output = 'test_logs'
                    )
        runner.run(self.suite)

if __name__ == '__main__':
    unittest.main(defaultTest ='Test_HTMLTestRunner')
