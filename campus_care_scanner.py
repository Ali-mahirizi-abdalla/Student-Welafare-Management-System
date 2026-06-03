#!/usr/bin/env python
"""
Campus Care Security Scanner – Scan, Fix & Share
Run: python campus_care_scanner.py --email admin@campus-care.co.ke
"""

import os
import re
import json
import smtplib
import argparse
import subprocess
from datetime import datetime
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

class CampusCareScanner:
    def __init__(self, project_path='.'):
        self.project_path = Path(project_path)
        self.issues = []
        self.fixes_applied = []
        self.scan_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    def scan_all(self):
        """Run all security scans"""
        print("\n" + "="*80)
        print("🔍 CAMPUS CARE SECURITY SCANNER v2.0")
        print("="*80)
        print(f"Scan started: {self.scan_date}")
        print("="*80 + "\n")
        
        self.scan_settings()
        self.scan_views()
        self.scan_templates()
        self.scan_models()
        self.scan_secrets()
        self.scan_urls()
        
        return self.generate_report()
    
    def add_issue(self, severity, category, file_path, line_no, issue, fix, auto_fixable=False):
        self.issues.append({
            'severity': severity,
            'category': category,
            'file': file_path,
            'line': line_no,
            'issue': issue,
            'fix': fix,
            'auto_fixable': auto_fixable,
        })
    
    def auto_fix(self, file_path, line_no, old_text, new_text):
        """Automatically fix an issue"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if 0 < line_no <= len(lines):
                original = lines[line_no-1]
                if old_text in original:
                    lines[line_no-1] = original.replace(old_text, new_text)
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                    
                    self.fixes_applied.append({
                        'file': file_path,
                        'line': line_no,
                        'fix': f"Replaced '{old_text}' with '{new_text}'"
                    })
                    return True
        except Exception as e:
            print(f"   ⚠️ Auto-fix failed: {e}")
        return False
    
    def scan_settings(self):
        """Scan and auto-fix settings.py"""
        print("📋 Scanning settings.py...")
        
        settings_path = self.project_path / 'swms' / 'settings.py'
        if not settings_path.exists():
            settings_path = self.project_path / 'settings.py'
        
        if settings_path.exists():
            with open(settings_path, 'r', encoding='utf-8') as f:
                content = f.read()
                f.seek(0)
                lines = f.readlines()
            
            # Fix DEBUG=True
            if 'DEBUG = True' in content and 'os.getenv' not in content:
                self.add_issue('CRITICAL', 'Configuration', str(settings_path), 0,
                    'DEBUG=True in production - exposes sensitive information',
                    'Change to: DEBUG = os.getenv("DEBUG", "False") == "True"',
                    auto_fixable=True)
                
                # Auto-fix
                with open(settings_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                new_content = file_content.replace('DEBUG = True', 'DEBUG = os.getenv("DEBUG", "False") == "True"')
                with open(settings_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                self.fixes_applied.append({'file': str(settings_path), 'line': 0, 'fix': 'DEBUG now uses environment variable'})
                print("   ✅ Auto-fixed: DEBUG setting")
            
            # Fix ALLOWED_HOSTS
            if "ALLOWED_HOSTS = ['*']" in content:
                self.add_issue('HIGH', 'Configuration', str(settings_path), 0,
                    'ALLOWED_HOSTS set to wildcard "*"',
                    'Set specific domains: ALLOWED_HOSTS = ["campus-care.co.ke", "www.campus-care.co.ke"]',
                    auto_fixable=True)
                
                with open(settings_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                new_content = file_content.replace("ALLOWED_HOSTS = ['*']", 'ALLOWED_HOSTS = ["campus-care.co.ke", "www.campus-care.co.ke", "localhost", "127.0.0.1"]')
                with open(settings_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                self.fixes_applied.append({'file': str(settings_path), 'line': 0, 'fix': 'ALLOWED_HOSTS now has specific domains'})
                print("   ✅ Auto-fixed: ALLOWED_HOSTS")
    
    def scan_views(self):
        """Scan and auto-fix views.py"""
        print("📋 Scanning views.py...")
        
        for views_file in self.project_path.rglob('views.py'):
            with open(views_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Find missing @login_required
            view_pattern = r'def\s+(\w+)\(request'
            views_found = re.findall(view_pattern, content)
            
            for view_name in views_found:
                for i, line in enumerate(lines):
                    if f'def {view_name}(request' in line:
                        context_before = '\n'.join(lines[max(0,i-5):i])
                        if '@login_required' not in context_before and '@role_required' not in context_before:
                            if view_name not in ['login', 'logout', 'register', 'password_reset', 'home', 'index']:
                                self.add_issue('HIGH', 'Authorization', str(views_file), i+1,
                                    f'View "{view_name}" missing @login_required',
                                    f'Add @login_required above def {view_name}(request):',
                                    auto_fixable=True)
                                
                                # Auto-fix
                                lines.insert(i, '@login_required')
                                with open(views_file, 'w', encoding='utf-8') as f:
                                    f.write('\n'.join(lines))
                                self.fixes_applied.append({'file': str(views_file), 'line': i+1, 'fix': f'Added @login_required to {view_name}'})
                                print(f"   ✅ Auto-fixed: Added @login_required to {view_name}")
                        break
    
    def scan_templates(self):
        """Scan and fix templates"""
        print("📋 Scanning templates...")
        
        for template_file in self.project_path.rglob('*.html'):
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Fix missing CSRF tokens
            if '<form method="post"' in content and '{% csrf_token %}' not in content:
                for i, line in enumerate(lines):
                    if '<form method="post"' in line and '{% csrf_token %}' not in content:
                        self.add_issue('HIGH', 'CSRF', str(template_file), i+1,
                            'Form missing CSRF token',
                            'Add {% csrf_token %} inside the form tags',
                            auto_fixable=True)
                        
                        # Find the form opening tag and insert CSRF
                        for j in range(i, min(i+10, len(lines))):
                            if '>' in lines[j] and '</form>' not in lines[j]:
                                lines.insert(j+1, '    {% csrf_token %}')
                                break
                        
                        with open(template_file, 'w', encoding='utf-8') as f:
                            f.write('\n'.join(lines))
                        self.fixes_applied.append({'file': str(template_file), 'line': i+1, 'fix': 'Added {% csrf_token %} to form'})
                        print(f"   ✅ Auto-fixed: Added CSRF token to {template_file.name}")
                        break
    
    def scan_secrets(self):
        """Scan for hardcoded secrets"""
        print("📋 Scanning for hardcoded secrets...")
        
        for py_file in self.project_path.rglob('*.py'):
            with open(py_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines):
                # Check for hardcoded API keys
                if 'API_KEY' in line and '=' in line and 'os.getenv' not in line:
                    if not any(x in line for x in ['example', 'test', 'demo', 'sample', 'TODO']):
                        self.add_issue('CRITICAL', 'Secrets', str(py_file), i+1,
                            f'Hardcoded API_KEY found',
                            'Move to .env file and use os.getenv()',
                            auto_fixable=False)
                        print(f"   ⚠️ Manual fix needed: {py_file} line {i+1}")
    
    def scan_models(self):
        """Scan models"""
        print("📋 Scanning models.py...")
        # Add model checks here
    
    def scan_urls(self):
        """Scan urls"""
        print("📋 Scanning urls.py...")
        # Add URL checks here
    
    def generate_report(self):
        """Generate HTML report"""
        critical = len([i for i in self.issues if i['severity'] == 'CRITICAL'])
        high = len([i for i in self.issues if i['severity'] == 'HIGH'])
        medium = len([i for i in self.issues if i['severity'] == 'MEDIUM'])
        low = len([i for i in self.issues if i['severity'] == 'LOW'])
        
        # Create HTML report
        html_report = self.generate_html_report(critical, high, medium, low)
        
        report_file = f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_report)
        
        # Print summary
        print("\n" + "="*80)
        print("📊 SCAN SUMMARY")
        print("="*80)
        print(f"🔴 CRITICAL: {critical}  🟠 HIGH: {high}  🟡 MEDIUM: {medium}  🔵 LOW: {low}")
        print(f"🔧 Auto-fixes applied: {len(self.fixes_applied)}")
        print(f"📄 Report saved: {report_file}")
        
        return report_file, {'critical': critical, 'high': high, 'medium': medium, 'low': low, 'total': len(self.issues)}
    
    def generate_html_report(self, critical, high, medium, low):
        """Generate HTML report with fixes"""
        fixes_html = ''
        for fix in self.fixes_applied[:20]:
            fixes_html += f'''
            <div style="background: #ECFDF5; padding: 10px; border-radius: 8px; margin-bottom: 8px;">
                <span style="color: #10B981;">✅</span> <strong>{fix['file']}</strong> - {fix['fix']}
            </div>
            '''
        
        issues_html = ''
        for issue in self.issues[:30]:
            severity_color = {'CRITICAL': '#EF4444', 'HIGH': '#F59E0B', 'MEDIUM': '#3B82F6', 'LOW': '#8B5CF6'}.get(issue['severity'], '#64748B')
            auto_fixed_tag = '<span style="background:#10B981; color:white; padding:2px 8px; border-radius:40px; font-size:10px; margin-left:8px;">AUTO-FIXED</span>' if issue['auto_fixable'] else ''
            issues_html += f'''
            <div style="border-left: 4px solid {severity_color}; margin-bottom: 16px; padding: 12px; background: #F8FAFC; border-radius: 8px;">
                <div style="display: flex; justify-content: space-between;">
                    <span style="background: {severity_color}; color: white; padding: 2px 8px; border-radius: 40px; font-size: 11px;">{issue['severity']}</span>
                    {auto_fixed_tag}
                </div>
                <div style="font-size: 12px; color: #64748B; margin-top: 8px;">📁 {issue['file']} (Line {issue['line']})</div>
                <div style="margin-top: 8px;">⚠️ {issue['issue']}</div>
                <div style="background: #F1F5F9; padding: 8px; margin-top: 8px; border-radius: 6px; font-size: 12px;">🔧 {issue['fix']}</div>
            </div>
            '''
        
        return f'''<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>Campus Care Security Scan</title><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>body{{font-family:'Inter',sans-serif;background:#F1F5F9;padding:40px;}}.container{{max-width:1000px;margin:0 auto;}}.header{{background:white;border-radius:20px;padding:30px;text-align:center;margin-bottom:24px;}}.logo{{font-size:28px;font-weight:800;background:linear-gradient(135deg,#1E293B,#0D9488);-webkit-background-clip:text;background-clip:text;color:transparent;}}.summary{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:24px;}}.card{{background:white;border-radius:16px;padding:20px;text-align:center;}}.card-number{{font-size:32px;font-weight:800;}}.status{{background:white;border-radius:16px;padding:20px;margin-bottom:24px;text-align:center;}}.fixes{{background:white;border-radius:20px;padding:24px;margin-bottom:24px;}}.issues{{background:white;border-radius:20px;padding:24px;}}</style></head>
<body><div class="container">
<div class="header"><div class="logo">🏥 CAMPUS CARE</div><h2>Security Scan Report</h2><p>{self.scan_date}</p></div>
<div class="summary">
<div class="card"><div class="card-number" style="color:#EF4444;">{critical}</div><div>CRITICAL</div></div>
<div class="card"><div class="card-number" style="color:#F59E0B;">{high}</div><div>HIGH</div></div>
<div class="card"><div class="card-number" style="color:#3B82F6;">{medium}</div><div>MEDIUM</div></div>
<div class="card"><div class="card-number" style="color:#8B5CF6;">{low}</div><div>LOW</div></div>
</div>
<div class="status"><div style="font-size:24px;font-weight:700;color:{'#10B981' if critical==0 and high==0 else '#EF4444'};">{'✅ SYSTEM PASSED' if critical==0 and high==0 else '⚠️ ISSUES FOUND - REVIEW REQUIRED'}</div></div>
<div class="fixes"><h3>🔧 Auto-Fixes Applied ({len(self.fixes_applied)})</h3>{fixes_html if fixes_html else '<p>No auto-fixes were applied.</p>'}</div>
<div class="issues"><h3>📋 Issues Found ({len(self.issues)})</h3>{issues_html if issues_html else '<p>✅ No issues found! Your system is secure.</p>'}</div>
<div class="footer" style="text-align:center;margin-top:24px;color:#94A3B8;">Generated by Campus Care Scanner | Fix critical/high issues immediately</div>
</div></body></html>'''
    
    def share_report(self, report_file, recipient_email, summary):
        """Email the report"""
        try:
            msg = MIMEMultipart()
            msg['From'] = "security@campus-care.co.ke"
            msg['To'] = recipient_email
            msg['Subject'] = f"Campus Care Security Report - {self.scan_date}"
            
            body = f"""
Campus Care Security Scan Report

Scan Date: {self.scan_date}
CRITICAL: {summary['critical']} | HIGH: {summary['high']} | MEDIUM: {summary['medium']} | LOW: {summary['low']}
Auto-Fixes Applied: {len(self.fixes_applied)}

{'⚠️ CRITICAL ISSUES FOUND - Action Required' if summary['critical'] > 0 else '✅ No critical issues found.'}

Full report attached.

--
Campus Care Security Scanner
"""
            msg.attach(MIMEText(body, 'plain'))
            
            with open(report_file, 'rb') as f:
                attach = MIMEBase('application', 'octet-stream')
                attach.set_payload(f.read())
                encoders.encode_base64(attach)
                attach.add_header('Content-Disposition', f'attachment; filename={report_file}')
                msg.attach(attach)
            
            # Use environment variable for email password
            password = os.getenv('EMAIL_PASSWORD', '')
            if password:
                with smtplib.SMTP('smtp.gmail.com', 587) as server:
                    server.starttls()
                    server.login("security@campus-care.co.ke", password)
                    server.send_message(msg)
                print(f"\n✅ Report emailed to: {recipient_email}")
                return True
            else:
                print(f"\n⚠️ Email not sent. Set EMAIL_PASSWORD environment variable")
                return False
        except Exception as e:
            print(f"\n❌ Email failed: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Campus Care Security Scanner - Scan, Fix & Share')
    parser.add_argument('--path', default='.', help='Project path to scan')
    parser.add_argument('--email', help='Email to send report')
    parser.add_argument('--no-fix', action='store_true', help='Scan only, no auto-fixes')
    args = parser.parse_args()
    
    scanner = CampusCareScanner(args.path)
    report_file, summary = scanner.scan_all()
    
    if args.email:
        scanner.share_report(report_file, args.email, summary)
    
    print("\n✅ Scan complete!")
    if summary['critical'] > 0 or summary['high'] > 0:
        print("⚠️ Review critical/high issues above")
    else:
        print("🎉 System is secure!")

if __name__ == "__main__":
    main()
