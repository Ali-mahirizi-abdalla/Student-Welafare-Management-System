# COMPLETE CODE – Copy and save as `security_scanner.py`

#!/usr/bin/env python
"""
Campus Care Security Scanner with Report Sharing
Run: python security_scanner.py --email your@email.com
"""

import os
import re
import json
import smtplib
import argparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from pathlib import Path

class CampusCareScanner:
    def __init__(self, project_path='.'):
        self.project_path = Path(project_path)
        self.issues = []
        self.scan_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    def scan_all(self):
        """Run all security scans"""
        print("\n" + "="*80)
        print("🔍 CAMPUS CARE SECURITY SCANNER")
        print("="*80)
        print(f"Scan started: {self.scan_date}")
        print("="*80 + "\n")
        
        self.scan_settings()
        self.scan_views()
        self.scan_templates()
        self.scan_models()
        self.scan_urls()
        self.scan_middleware()
        self.scan_env_files()
        
        return self.generate_report()
        
    def add_issue(self, severity, category, file_path, line_no, issue, fix, code_snippet=''):
        self.issues.append({
            'severity': severity,
            'category': category,
            'file': file_path,
            'line': line_no,
            'issue': issue,
            'fix': fix,
            'code': code_snippet[:200] if code_snippet else '',
        })
    
    def scan_settings(self):
        """Scan settings.py for security issues"""
        settings_path = self.project_path / 'swms' / 'settings.py'
        if not settings_path.exists():
            settings_path = self.project_path / 'settings.py'
        
        if settings_path.exists():
            with open(settings_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'DEBUG = True' in content and 'os.getenv' not in content:
                self.add_issue('CRITICAL', 'Configuration', str(settings_path), 0,
                    'DEBUG=True in production - exposes sensitive information',
                    'Change to: DEBUG = os.getenv("DEBUG", "False") == "True"')
            
            if "SECRET_KEY = 'django-insecure-" in content:
                self.add_issue('CRITICAL', 'Configuration', str(settings_path), 0,
                    'Default/insecure SECRET_KEY detected',
                    'Generate new key: from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
            
            if "ALLOWED_HOSTS = ['*']" in content:
                self.add_issue('HIGH', 'Configuration', str(settings_path), 0,
                    'ALLOWED_HOSTS set to wildcard "*"',
                    'Set specific domains: ALLOWED_HOSTS = ["campus-care.co.ke", "www.campus-care.co.ke"]')
    
    def scan_views(self):
        """Scan views.py for security issues"""
        for views_file in self.project_path.rglob('views.py'):
            with open(views_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Find all view functions
            view_pattern = r'def\s+(\w+)\(request'
            views_found = re.findall(view_pattern, content)
            
            for view_name in views_found:
                for i, line in enumerate(lines):
                    if f'def {view_name}(request' in line:
                        context_before = '\n'.join(lines[max(0,i-5):i])
                        if '@login_required' not in context_before and '@role_required' not in context_before:
                            if view_name not in ['login', 'logout', 'register', 'password_reset', 'home']:
                                self.add_issue('HIGH', 'Authorization', str(views_file), i+1,
                                    f'View "{view_name}" missing @login_required',
                                    f'Add @login_required above def {view_name}(request):')
                        break
            
            # Check for raw SQL queries
            sql_matches = re.finditer(r'cursor\.execute\(f["\']', content)
            for match in sql_matches:
                line_no = content[:match.start()].count('\n') + 1
                self.add_issue('CRITICAL', 'SQL Injection', str(views_file), line_no,
                    'Raw SQL query detected - vulnerable to SQL injection',
                    'Use parameterized queries: cursor.execute("SELECT * FROM table WHERE id = %s", [id])')
    
    def scan_templates(self):
        """Scan HTML templates"""
        for template_file in self.project_path.rglob('*.html'):
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            if '<form method="post"' in content and '{% csrf_token %}' not in content:
                for i, line in enumerate(lines):
                    if '<form method="post"' in line:
                        self.add_issue('HIGH', 'CSRF', str(template_file), i+1,
                            'Form missing CSRF token',
                            'Add {% csrf_token %} inside the form tags')
                        break
            
            if '|safe' in content:
                for i, line in enumerate(lines):
                    if '|safe' in line and '{{' in line:
                        self.add_issue('MEDIUM', 'XSS', str(template_file), i+1,
                            'Using |safe filter on user input - possible XSS',
                            'Remove |safe filter or sanitize input first')
                        break
    
    def scan_models(self):
        """Scan models.py"""
        for models_file in self.project_path.rglob('models.py'):
            with open(models_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'class Meta:' in content and 'ordering = ' not in content:
                self.add_issue('LOW', 'Performance', str(models_file), 0,
                    'Model missing default ordering',
                    'Add: class Meta: ordering = ["-created_at"]')
    
    def scan_urls(self):
        """Scan urls.py"""
        pass  # Optional
    
    def scan_middleware(self):
        """Check middleware"""
        settings_path = self.project_path / 'swms' / 'settings.py'
        if settings_path.exists():
            with open(settings_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            required = ['SecurityMiddleware', 'SessionMiddleware', 'CsrfViewMiddleware', 'AuthenticationMiddleware']
            for mw in required:
                if mw not in content:
                    self.add_issue('MEDIUM', 'Security', str(settings_path), 0,
                        f'Missing {mw} in MIDDLEWARE',
                        f'Add "{mw}" to MIDDLEWARE in settings.py')
    
    def scan_env_files(self):
        """Scan for hardcoded credentials"""
        for py_file in self.project_path.rglob('*.py'):
            with open(py_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines):
                if 'API_KEY' in line and '=' in line and 'os.getenv' not in line and '#' not in line:
                    if not any(x in line for x in ['example', 'test', 'demo', 'sample']):
                        self.add_issue('CRITICAL', 'Secrets', str(py_file), i+1,
                            f'Hardcoded API_KEY found',
                            'Move to .env file and use os.getenv()')
                        break
    
    def generate_report(self):
        """Generate report and return summary"""
        critical = len([i for i in self.issues if i['severity'] == 'CRITICAL'])
        high = len([i for i in self.issues if i['severity'] == 'HIGH'])
        medium = len([i for i in self.issues if i['severity'] == 'MEDIUM'])
        low = len([i for i in self.issues if i['severity'] == 'LOW'])
        
        # Create HTML report
        html_report = self.generate_html_report(critical, high, medium, low)
        
        # Save to file
        report_file = f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_report)
        
        # Print console summary
        print("\n" + "="*80)
        print("📊 SECURITY SCAN REPORT")
        print("="*80)
        print(f"\n🔴 CRITICAL: {critical}  🟠 HIGH: {high}  🟡 MEDIUM: {medium}  🔵 LOW: {low}  📦 TOTAL: {len(self.issues)}")
        
        if critical > 0:
            print("\n🔴 CRITICAL ISSUES (Fix Immediately):")
            for issue in [i for i in self.issues if i['severity'] == 'CRITICAL'][:5]:
                print(f"   📁 {issue['file']} (Line {issue['line']})")
                print(f"   ⚠️  {issue['issue']}")
                print(f"   🔧 {issue['fix']}\n")
        
        print(f"\n📄 HTML Report saved to: {report_file}")
        return report_file, {'critical': critical, 'high': high, 'medium': medium, 'low': low, 'total': len(self.issues)}
    
    def generate_html_report(self, critical, high, medium, low):
        """Generate professional HTML report"""
        status_color = '#10B981' if critical == 0 and high == 0 else '#EF4444'
        status_text = 'PASSED' if critical == 0 and high == 0 else 'FAILED - Action Required'
        
        issues_html = ''
        for issue in self.issues:
            severity_color = {'CRITICAL': '#EF4444', 'HIGH': '#F59E0B', 'MEDIUM': '#3B82F6', 'LOW': '#8B5CF6'}.get(issue['severity'], '#64748B')
            issues_html += f'''
            <div class="issue" style="border-left: 4px solid {severity_color}; margin-bottom: 20px; padding: 15px; background: #F8FAFC; border-radius: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <span style="background: {severity_color}; color: white; padding: 4px 12px; border-radius: 40px; font-size: 12px; font-weight: 600;">{issue['severity']}</span>
                    <span style="color: #64748B; font-size: 12px;">{issue['category']}</span>
                </div>
                <div style="font-family: monospace; font-size: 12px; color: #64748B; margin-bottom: 8px;">📁 {issue['file']} (Line {issue['line']})</div>
                <div style="font-weight: 600; margin-bottom: 8px;">⚠️ {issue['issue']}</div>
                <div style="background: #F1F5F9; padding: 10px; border-radius: 6px; font-family: monospace; font-size: 12px;">🔧 {issue['fix']}</div>
            </div>
            '''
        
        return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Campus Care Security Scan Report</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Inter', sans-serif; background: #F1F5F9; padding: 40px; }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        .header {{ background: white; border-radius: 20px; padding: 30px; margin-bottom: 24px; text-align: center; border: 1px solid #E2E8F0; }}
        .logo {{ font-size: 28px; font-weight: 800; background: linear-gradient(135deg, #1E293B, #0D9488); -webkit-background-clip: text; background-clip: text; color: transparent; }}
        .summary {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }}
        .summary-card {{ background: white; border-radius: 16px; padding: 20px; text-align: center; border: 1px solid #E2E8F0; }}
        .summary-number {{ font-size: 32px; font-weight: 800; }}
        .summary-label {{ font-size: 12px; color: #64748B; margin-top: 4px; }}
        .status {{ background: white; border-radius: 16px; padding: 20px; margin-bottom: 24px; text-align: center; border: 1px solid #E2E8F0; }}
        .status-pass {{ color: #10B981; font-size: 24px; font-weight: 700; }}
        .status-fail {{ color: #EF4444; font-size: 24px; font-weight: 700; }}
        .issues-section {{ background: white; border-radius: 20px; padding: 24px; border: 1px solid #E2E8F0; }}
        .footer {{ text-align: center; margin-top: 24px; padding: 20px; color: #94A3B8; font-size: 12px; }}
        hr {{ margin: 20px 0; border: none; border-top: 1px solid #E2E8F0; }}
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <div class="logo">🏥 CAMPUS CARE</div>
        <h2 style="margin-top: 12px;">Security Scan Report</h2>
        <p style="color: #64748B;">Scan Date: {self.scan_date}</p>
    </div>
    
    <div class="summary">
        <div class="summary-card"><div class="summary-number" style="color: #EF4444;">{critical}</div><div class="summary-label">CRITICAL</div></div>
        <div class="summary-card"><div class="summary-number" style="color: #F59E0B;">{high}</div><div class="summary-label">HIGH</div></div>
        <div class="summary-card"><div class="summary-number" style="color: #3B82F6;">{medium}</div><div class="summary-label">MEDIUM</div></div>
        <div class="summary-card"><div class="summary-number" style="color: #8B5CF6;">{low}</div><div class="summary-label">LOW</div></div>
    </div>
    
    <div class="status">
        <div class="status-{'pass' if critical == 0 and high == 0 else 'fail'}">
            {'✅ SYSTEM PASSED' if critical == 0 and high == 0 else '❌ ISSUES FOUND - ACTION REQUIRED'}
        </div>
        <p style="color: #64748B; margin-top: 8px;">Total Issues: {len(self.issues)}</p>
    </div>
    
    <div class="issues-section">
        <h3 style="margin-bottom: 20px;">📋 Detailed Issues</h3>
        {issues_html if issues_html else '<div style="text-align: center; padding: 40px; color: #10B981;">✅ No security issues found! Your system is secure.</div>'}
    </div>
    
    <div class="footer">
        <p>Generated by Campus Care Security Scanner | {self.scan_date}</p>
        <p style="margin-top: 8px;">🔒 Keep this report confidential | Fix critical and high issues immediately</p>
    </div>
</div>
</body>
</html>'''
    
    def send_report_email(self, report_file, recipient_email, summary):
        """Send the report via email"""
        try:
            # Email configuration
            sender_email = "security@campus-care.co.ke"
            sender_password = os.getenv('EMAIL_PASSWORD', '')  # Set this in environment
            
            if not sender_password:
                print("\n⚠️ Email not sent: No EMAIL_PASSWORD set in environment")
                print(f"   Report saved locally: {report_file}")
                return False
            
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = f"Campus Care Security Scan Report - {self.scan_date}"
            
            # Email body
            body = f"""
            Campus Care Security Scan Report
            
            Scan Date: {self.scan_date}
            
            SUMMARY:
            🔴 CRITICAL: {summary['critical']}
            🟠 HIGH: {summary['high']}
            🟡 MEDIUM: {summary['medium']}
            🔵 LOW: {summary['low']}
            📦 TOTAL: {summary['total']}
            
            {'⚠️ ACTION REQUIRED: Critical or High issues found!' if summary['critical'] > 0 or summary['high'] > 0 else '✅ No critical issues found.'}
            
            Attached: Full HTML Report
            
            --
            Campus Care Security Scanner
            """
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach report
            with open(report_file, 'rb') as f:
                attachment = MIMEBase('application', 'octet-stream')
                attachment.set_payload(f.read())
                encoders.encode_base64(attachment)
                attachment.add_header('Content-Disposition', f'attachment; filename={os.path.basename(report_file)}')
                msg.attach(attachment)
            
            # Send email
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
            
            print(f"\n✅ Report emailed to: {recipient_email}")
            return True
            
        except Exception as e:
            print(f"\n❌ Failed to send email: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Campus Care Security Scanner')
    parser.add_argument('--path', default='.', help='Project path to scan')
    parser.add_argument('--email', help='Email address to send report to')
    parser.add_argument('--share', action='store_true', help='Share report via email')
    args = parser.parse_args()
    
    scanner = CampusCareScanner(args.path)
    report_file, summary = scanner.scan_all()
    
    if args.email and args.share:
        scanner.send_report_email(report_file, args.email, summary)
    elif args.email:
        print(f"\n📧 To share report via email, add --share flag")
        print(f"   Example: python security_scanner.py --email {args.email} --share")
    
    print("\n✅ Scan complete!")

if __name__ == "__main__":
    main()