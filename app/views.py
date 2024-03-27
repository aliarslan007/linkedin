from django.shortcuts import render,HttpResponse,redirect
import requests
from .models import Savesearches
import json


def home(request):
    if request.method == 'GET' and 'search_query' in request.GET:
        # Get the search query from the frontend form
        search_query = request.GET.get('search_query')
        api_key = 'x3DXCsAWpBjbry7LAzgRnA'
        headers = {'Authorization': 'Bearer ' + api_key}
        api_endpoint = 'https://nubela.co/proxycurl/api/v2/linkedin'
        params = {
            'linkedin_profile_url':f'http://www.linkedin.com/in/{search_query}/',
        }
        response = requests.get(api_endpoint, params=params, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=4, separators=(',', ': ')))
            return render(request , 'index.html', {'linkedin_data': data})
        else:
            return HttpResponse('Failed to fetch data from API')
    else:
        return render(request , 'index.html')        


def filter(request):
    if request.method == 'GET' and 'company_name' in request.GET:
        companies = request.GET.get('company_name')
        companies = companies.split(',')
        # company2 = request.GET.get('company_name2')
        job_title = request.GET.get('job_title')  
        job_titles_list = job_title.split(',')
        print(job_titles_list)
        # job2 = request.GET.get('job_title2')
        # companies = company1 + company2
        # job_title = job1 + job2
        results = 0
        request.session['company_name'] = companies
        request.session['job_title'] = job_title
        

        api_key = 'x3DXCsAWpBjbry7LAzgRnA'
        headers = {'Authorization': 'Bearer ' + api_key}
        api_endpoint = 'https://nubela.co/proxycurl/api/linkedin/company/resolve'
        company_data_list = []
        for company in companies:
            params = { 'company_name': company }
            response = requests.get(api_endpoint, params=params, headers=headers)
            data = response.json()
            company_data_list.append(data)

        api_key2 = 'x3DXCsAWpBjbry7LAzgRnA'
        headers = {'Authorization': 'Bearer ' + api_key2}
        api_endpoint = 'https://nubela.co/proxycurl/api/linkedin/company/employees/'
        employee_data_list = []
        company_urls = [d['url'] for d in company_data_list]
        for url in company_urls:
            params = {
                'url': url,
                'country': 'uk',
                'role_search': job_titles_list,
                'employment_status': 'current',
                'enrich_profiles': 'enrich',
            }
            response = requests.get(api_endpoint, params=params, headers=headers)
            data = response.json()
            try:
                if len(data['employees']) > 0:
                    results = results + len(data['employees'])
            except:
                print('')
            employee_data_list.append(data)
        request.session['results'] = results 
        current_url = request.build_absolute_uri()
        request.session['current_url'] = current_url  
        
        return render(request , 'filters.html', {'employee_data_list': employee_data_list})
    return render(request , 'filters.html')

def savesearches(request):
    companies = request.session.get('company_name', None)
    job_title = request.session.get('job_title', None)
    results = request.session.get('results', None)
    current_url = request.session.get('current_url', None)
    search = Savesearches(companies=companies,job_title=job_title, results=results,current_url=current_url)
    search.save()
    return redirect('savedsearches')

def savedsearches(request):
    searches = Savesearches.objects.all()
    return render(request, 'savedsearches.html',{'searches':searches})

def delete_search(request,id):
    if request.method == 'GET':
        searches = Savesearches.objects.get(pk = id)
        searches.delete()
        return redirect('savedsearches')   
    
