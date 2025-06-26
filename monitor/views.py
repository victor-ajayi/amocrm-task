import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import Incident


@csrf_exempt
@require_http_methods(["POST"])
def api_register(request):
    """API endpoint for user registration."""
    try:
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")
        email = data.get("email", "")

        if not username or not password:
            return JsonResponse(
                {"error": "Username and password are required"}, status=400
            )

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "Username already exists"}, status=400)

        # Create new user
        user = User.objects.create_user(
            username=username, email=email, password=password
        )

        # Log the user in automatically
        login(request, user)
        return JsonResponse({"message": "Registration successful"})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception:
        return JsonResponse({"error": "Server error"}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_login(request):
    """API endpoint for user login."""
    try:
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return JsonResponse(
                {"error": "Username and password are required"}, status=400
            )

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({"message": "Login successful"})
        else:
            return JsonResponse({"error": "Invalid credentials"}, status=401)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception:
        return JsonResponse({"error": "Server error"}, status=500)


@require_http_methods(["POST"])
def api_logout(request):
    """API endpoint for user logout."""
    logout(request)
    return JsonResponse({"message": "Logout successful"})


def api_incidents(request):
    """API endpoint to get all incidents."""
    try:
        # Simplified query to debug
        incidents = Incident.objects.all().order_by("-start_time")
        incidents_data = []

        for incident in incidents:
            incidents_data.append(
                {
                    "id": incident.id,
                    "machine": incident.machine.name,
                    "type": incident.type,
                    "value": incident.value,
                    "start_time": incident.start_time.isoformat(),
                    "end_time": incident.end_time.isoformat()
                    if incident.end_time
                    else None,
                }
            )

        return JsonResponse(incidents_data, safe=False)
    except Exception as e:
        import traceback

        print(f"Error in api_incidents: {e}")
        traceback.print_exc()
        return JsonResponse({"error": f"Server error: {str(e)}"}, status=500)
