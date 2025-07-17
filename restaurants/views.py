from django.shortcuts import render

def restaurant_list(request):
    restaurants = [
        {'name': 'Ресторан 1', 'description': 'Краткое описание ресторана 1.'},
        {'name': 'Ресторан 2', 'description': 'Краткое описание ресторана 2.'},
        {'name': 'Ресторан 3', 'description': 'Краткое описание ресторана 3.'},
    ]
    return render(request, 'restaurants/restaurant_list.html', {'restaurants': restaurants})