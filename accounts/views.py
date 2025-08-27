from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import json
import subprocess
from django.http import JsonResponse, HttpResponse
import google.generativeai as genai
from django.conf import settings
from .models import AIHistory

# configure once (you already have this)
genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-2.5-flash")

@csrf_exempt
def react_register(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')

            if User.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Username already exists'}, status=400)

            User.objects.create_user(username=username, email=email, password=password)
            return JsonResponse({'message': 'User registered successfully'}, status=201)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def react_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({'message': 'Login successful'}, status=200)
            else:
                return JsonResponse({'error': 'Invalid credentials'}, status=401)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    # ✅ Always return something
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def react_logout(request):
    logout(request)
    return JsonResponse({'message': 'Logged out successfully'}, status=200)

@login_required
def check_auth(request):
    return JsonResponse({'user': request.user.username})

@csrf_exempt
@login_required
def ask_ai(request):
    # Only accept POST for JSON payloads
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method. Use POST with JSON."}, status=405)

    # Parse JSON safely
    try:
        body = request.body.decode("utf-8") or "{}"
        data = json.loads(body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body."}, status=400)

    prompt = data.get("prompt", "").strip()
    if not prompt:
        return JsonResponse({"error": "Missing 'prompt' in request body."}, status=400)
    
    if "what" in prompt.lower() and "past" in prompt.lower():
        history = AIHistory.objects.filter(user=request.user).order_by('-timestamp')[:5]
        if not history.exists():
            return JsonResponse({"response": "You have no past interactions with me."})

        # Make it sound conversational
        past_questions = [h.prompt for h in history]
        past_str = ", ".join(past_questions)
        return JsonResponse({
            "response": f"In the past, you asked me about: {past_str}."
        })

    try:
        short_prompt = f"Answer briefly in 1-2 sentences: {prompt}"
        response = model.generate_content(short_prompt)
        answer = response.text.strip()
        AIHistory.objects.create(
            user=request.user,
            prompt=prompt,
            response=response.text,
        )
        return JsonResponse({"response": answer})
    except Exception as e:
        # return error message but don't leak secrets in production
        return JsonResponse({"error": str(e)}, status=500)


