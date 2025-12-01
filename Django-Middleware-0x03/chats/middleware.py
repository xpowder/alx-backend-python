import logging
from datetime import datetime, time
from django.http import HttpResponseForbidden, JsonResponse
from django.utils.deprecation import MiddlewareMixin
from collections import defaultdict

# Configure logger for request logging
logger = logging.getLogger('request_logger')
logger.setLevel(logging.INFO)

# Create file handler if it doesn't exist
file_handler = logging.FileHandler('requests.log')
file_handler.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter('%(message)s')
file_handler.setFormatter(formatter)

# Add handler to logger if not already added
if not logger.handlers:
    logger.addHandler(file_handler)


# Task 1: Request Logging Middleware
class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware that logs each user's requests to a file.
    Logs timestamp, user, and request path.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def __call__(self, request):
        # Get user information
        user = request.user.username if request.user.is_authenticated else 'Anonymous'
        
        # Log the request
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        logger.info(log_message)
        
        # Process the request
        response = self.get_response(request)
        
        return response


# Task 2: Restrict Access by Time Middleware
class RestrictAccessByTimeMiddleware(MiddlewareMixin):
    """
    Middleware that restricts access to the messaging app during certain hours.
    Denies access outside 6AM and 9PM (i.e., between 9PM and 6AM).
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def __call__(self, request):
        # Only apply to chat-related endpoints
        if '/chats/' in request.path or '/conversations/' in request.path:
            # Get current server time
            current_time = datetime.now().time()
            
            # Define restricted time window: 9PM (21:00) to 6AM (06:00)
            restricted_start = time(21, 0)  # 9PM
            restricted_end = time(6, 0)      # 6AM
            
            # Check if current time is within restricted hours
            # This handles the case where restricted time spans midnight
            if current_time >= restricted_start or current_time < restricted_end:
                # Deny access with 403 Forbidden
                return HttpResponseForbidden(
                    JsonResponse({
                        'error': 'Access denied. The messaging app is only available between 6AM and 9PM.'
                    }, status=403),
                    status=403
                )
        
        # Allow access during permitted hours or for non-chat endpoints
        response = self.get_response(request)
        return response


# Task 3: Offensive Language Middleware (Rate Limiting by IP)
class OffensiveLanguageMiddleware(MiddlewareMixin):
    """
    Middleware that limits the number of chat messages a user can send
    within a certain time window, based on their IP address.
    Implements rate limiting: 5 messages per minute per IP address.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Store request timestamps per IP address
        self.ip_requests = defaultdict(list)
        super().__init__(get_response)
    
    def __call__(self, request):
        # Only apply rate limiting to POST requests on chat/message endpoints
        if request.method == 'POST' and ('/chats/' in request.path or '/conversations/' in request.path or '/messages/' in request.path):
            # Get client IP address
            ip_address = self.get_client_ip(request)
            
            # Get current timestamp
            current_time = datetime.now()
            
            # Clean old requests (older than 1 minute)
            if ip_address in self.ip_requests:
                self.ip_requests[ip_address] = [
                    req_time for req_time in self.ip_requests[ip_address]
                    if (current_time - req_time).total_seconds() < 60
                ]
            
            # Check if IP has exceeded the limit (5 messages per minute)
            if len(self.ip_requests[ip_address]) >= 5:
                # Block the request and return error
                return HttpResponseForbidden(
                    JsonResponse({
                        'error': 'Rate limit exceeded. Maximum 5 messages per minute allowed.'
                    }, status=403),
                    status=403
                )
            
            # Add current request timestamp
            self.ip_requests[ip_address].append(current_time)
        
        # Process the request
        response = self.get_response(request)
        return response
    
    def get_client_ip(self, request):
        """
        Get the client's IP address from the request.
        Handles proxy headers like X-Forwarded-For.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


# Task 4: Role Permission Middleware
class RolepermissionMiddleware(MiddlewareMixin):
    """
    Middleware that checks the user's role before allowing access to specific actions.
    Only allows admin or moderator roles to access certain endpoints.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def __call__(self, request):
        # Only apply to chat-related endpoints that require admin/moderator access
        if '/chats/' in request.path or '/conversations/' in request.path or '/messages/' in request.path:
            # Check if user is authenticated
            if request.user.is_authenticated:
                # Get user's role
                user_role = getattr(request.user, 'role', None)
                
                # Check if user has admin or moderator role
                # Note: The User model has ADMIN role, checking for both admin and moderator
                if user_role:
                    # Convert to uppercase for comparison (handles both 'ADMIN' and 'admin')
                    role_upper = user_role.upper()
                    
                    # Allow access only for admin or moderator roles
                    # Since the model shows ADMIN, we check for ADMIN
                    # If moderator role exists, it would be checked here too
                    if role_upper not in ['ADMIN', 'MODERATOR']:
                        # Deny access with 403 Forbidden
                        return HttpResponseForbidden(
                            JsonResponse({
                                'error': 'Access denied. Admin or Moderator role required.'
                            }, status=403),
                            status=403
                        )
                else:
                    # User has no role assigned, deny access
                    return HttpResponseForbidden(
                        JsonResponse({
                            'error': 'Access denied. User role not found.'
                        }, status=403),
                        status=403
                    )
            else:
                # User is not authenticated, deny access
                return HttpResponseForbidden(
                    JsonResponse({
                        'error': 'Access denied. Authentication required.'
                    }, status=403),
                    status=403
                )
        
        # Allow access for admin/moderator users or non-chat endpoints
        response = self.get_response(request)
        return response

