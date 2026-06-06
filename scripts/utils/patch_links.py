import os
import re

templates_dir = 'web_app/templates'

# Mapping of sidebar names to route names
sidebar_routes = {
    'Dashboard': '/operations_dashboard',
    'Patient Access': '/patient_access',
    'Scheduling': '/scheduling',
    'Insurance': '/insurance_verification',
    'Prior Auth': '/prior_authorizations',
    'Revenue Cycle': '/revenue_cycle',
    'AI Assistant': '/ai_assistant',
    'Tasks': '/audit_logs_compliance',  # using audit log as a placeholder for tasks if needed
    'Analytics': '/operational_analytics',
    'Settings': '/settings_accessibility'
}

def patch_sidebar_links():
    for filename in os.listdir(templates_dir):
        if not filename.endswith('.html'):
            continue
            
        filepath = os.path.join(templates_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # We will use regex to find the <a> tags containing these labels and replace href="#" with the correct route.
        # Format in HTML:
        # <a class="..." href="#">
        # <span class="...">...</span>
        # <span class="...">Dashboard</span>
        # </a>
        
        for name, route in sidebar_routes.items():
            # A regex that matches the <a href="#"> tag before the span containing the name
            # This is a bit tricky with regex across newlines.
            # We'll do a simpler replacement: find chunks of <a ... href="#" ...>...<span ...>Name</span>...</a>
            
            # Since HTML is consistent, we can just replace:
            # href="#"
            # <span class="material-symbols-outlined"...
            # <span class="font-label-md text-label-md">Dashboard</span>
            
            # A more robust regex:
            pattern = re.compile(r'(<a[^>]*href=")#[^"]*("[^>]*>\s*<span[^>]*>[^<]*</span>\s*<span[^>]*>)\s*' + name + r'\s*(</span>\s*</a>)', re.IGNORECASE)
            
            # It might also have active styling. Let's just do a simpler search and replace for href="#" if we know it's a sidebar link
            # Actually, let's just find the exact block since they are standard
            pass
            
        # Alternative simpler approach: replace all href="#" in the sidebar area. 
        # But we need to map them correctly.
        # Let's iterate through the links
        for name, route in sidebar_routes.items():
            pattern = r'(<a[^>]*href=")#[^"]*("[^>]*>\s*<span[^>]*>[^<]*</span>\s*<span class="font-label-md text-label-md">)' + name + r'(</span>\s*</a>)'
            content = re.sub(pattern, r'\g<1>' + route + r'\g<2>' + name + r'\g<3>', content)

        # Also patch any generic href="#" just to be safe, maybe point them to /operations_dashboard? No, leave them.
        
        # Finally, let's fix the image source
        content = content.replace('src="https://lh3.googleusercontent.com/aida-public/', 'src="')
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

patch_sidebar_links()
print("Links patched successfully.")
