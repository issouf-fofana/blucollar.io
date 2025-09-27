from django.shortcuts import render
from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import requests


def home(request: HttpRequest):
    return render(request, 'index.html')


def fsm_platform(request: HttpRequest):
    return render(request, 'fsm_platform.html')


def mapping(request: HttpRequest):
    return render(request, 'Ecotrak+SF-api_payload_mapping.html')


def _sf_headers():
    api_key = settings.SERVICE_FUSION_API_KEY
    return {
        'Authorization': f'Bearer {api_key}' if api_key else '',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }


def _sf_base():
    return settings.SERVICE_FUSION_BASE_URL


def sf_search_customers(request: HttpRequest):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    if not _sf_base():
        return JsonResponse({'error': 'Service Fusion not configured'}, status=500)
    q = request.GET.get('q', '').strip()
    if not q:
        return JsonResponse([])
    
    try:
        # Search customers with locations and contacts
        url = f"{_sf_base()}/customers"
        params = {
            'query': q,
            'include': 'locations,contacts',  # Include related data
            'limit': 10
        }
        r = requests.get(url, headers=_sf_headers(), params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        
        # Transform data to match frontend expectations
        customers = []
        if isinstance(data, dict) and 'data' in data:
            customers = data['data']
        elif isinstance(data, list):
            customers = data
            
        # Ensure each customer has the expected structure
        for customer in customers:
            # Normalize customer name field
            if 'customer_name' not in customer and 'name' in customer:
                customer['customer_name'] = customer['name']
            if 'name' not in customer and 'customer_name' in customer:
                customer['name'] = customer['customer_name']
                
        return JsonResponse(customers, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=502)


@csrf_exempt
def sf_create_job(request: HttpRequest):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    if not _sf_base():
        return JsonResponse({'error': 'Service Fusion not configured'}, status=500)
    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    try:
        # Map minimal fields according to your front-end payload
        sf_payload = {
            'customer_id': payload.get('customer_id'),
            'customer_name': payload.get('customer_name'),
            'location_name': (payload.get('service_location') or {}).get('name'),
            'street_1': (payload.get('service_location') or {}).get('address'),
            'city': (payload.get('service_location') or {}).get('city'),
            'state_prov': (payload.get('service_location') or {}).get('state'),
            'postal_code': (payload.get('service_location') or {}).get('zip'),
            'priority': payload.get('priority'),
            'category': payload.get('category'),
            'description': payload.get('problem_details'),
            'contact_first_name': (payload.get('contact') or {}).get('name'),
            'contact_phone': (payload.get('contact') or {}).get('phone'),
            'contact_email': (payload.get('contact') or {}).get('email'),
        }
        url = f"{_sf_base()}/jobs"
        r = requests.post(url, headers=_sf_headers(), json=sf_payload, timeout=30)
        r.raise_for_status()
        data = r.json()
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=502)

# Create your views here.
