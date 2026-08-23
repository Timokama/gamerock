import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
try:
    req = urllib.request.Request('http://127.0.0.1:5000/contribution/')
    resp = urllib.request.urlopen(req, timeout=10)
    html = resp.read().decode('utf-8')
    if 'profile-section-sub-header' in html:
        print('profile-section-sub-header: FOUND in rendered HTML')
    else:
        print('profile-section-sub-header: NOT found')
    if 'Deposit Actions' in html:
        print('Deposit Actions: FOUND in rendered HTML')
    else:
        print('Deposit Actions: NOT found')
    if 'Recent Contributions' in html:
        print('Recent Contributions: FOUND in rendered HTML')
    else:
        print('Recent Contributions: NOT found')
    if '+' in html and 'dropdown' in html:
        print('+ dropdown: FOUND in rendered HTML')
    if 'All Member Contributions' in html:
        print('All Member Contributions: FOUND in rendered HTML')
    else:
        print('All Member Contributions: NOT found')
    
    # Check if it's redirecting to login
    if 'login' in html.lower():
        print('Note: Page appears to be redirecting to login')
    
    # Print first 500 chars of body for debugging
    print('\n--- First 500 chars of response ---')
    print(html[:500])
except Exception as e:
    print(f'Error: {e}')
