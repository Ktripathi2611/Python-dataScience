import pandas as pd
import plotly.graph_objects as go
from typing import Dict, List, Optional
import json
from datetime import datetime, timedelta
import os

class ReportGenerator:
    def __init__(self):
        self.report_types = {
            'security_overview': self._generate_security_overview,
            'threat_analysis': self._generate_threat_analysis,
            'network_activity': self._generate_network_activity,
            'user_education': self._generate_education_report
        }
    
    def generate_report(self, report_type: str, data: Dict, output_format: str = 'html') -> Optional[str]:
        """Generate a report of the specified type."""
        if report_type not in self.report_types:
            return None
        
        report_generator = self.report_types[report_type]
        report_content = report_generator(data)
        
        if output_format == 'html':
            return self._format_as_html(report_content)
        elif output_format == 'json':
            return json.dumps(report_content, indent=2)
        return None
    
    def _generate_security_overview(self, data: Dict) -> Dict:
        """Generate a comprehensive security overview report."""
        return {
            'title': 'Security Overview Report',
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_threats_detected': data.get('total_threats', 0),
                'threats_blocked': data.get('blocked_threats', 0),
                'risk_level': self._calculate_risk_level(data),
                'active_protections': data.get('active_protections', [])
            },
            'threat_breakdown': self._categorize_threats(data.get('threats', [])),
            'recommendations': self._generate_recommendations(data),
            'charts': self._generate_overview_charts(data)
        }
    
    def _generate_threat_analysis(self, data: Dict) -> Dict:
        """Generate a detailed threat analysis report."""
        return {
            'title': 'Threat Analysis Report',
            'generated_at': datetime.now().isoformat(),
            'analysis': {
                'high_risk_threats': self._analyze_high_risk_threats(data),
                'attack_patterns': self._identify_attack_patterns(data),
                'vulnerability_assessment': self._assess_vulnerabilities(data)
            },
            'timeline': self._generate_threat_timeline(data),
            'mitigation_status': self._get_mitigation_status(data),
            'charts': self._generate_threat_charts(data)
        }
    
    def _generate_network_activity(self, data: Dict) -> Dict:
        """Generate a network activity report."""
        return {
            'title': 'Network Activity Report',
            'generated_at': datetime.now().isoformat(),
            'network_summary': {
                'total_connections': data.get('total_connections', 0),
                'unique_ips': len(data.get('unique_ips', [])),
                'bandwidth_usage': self._analyze_bandwidth(data),
                'active_services': self._analyze_services(data)
            },
            'connection_analysis': self._analyze_connections(data),
            'charts': self._generate_network_charts(data)
        }
    
    def _generate_education_report(self, data: Dict) -> Dict:
        """Generate a user education progress report."""
        return {
            'title': 'User Education Report',
            'generated_at': datetime.now().isoformat(),
            'progress_summary': {
                'completed_modules': data.get('completed_modules', []),
                'in_progress_modules': data.get('in_progress_modules', []),
                'recommended_modules': data.get('recommended_modules', [])
            },
            'assessment_results': self._analyze_assessments(data),
            'charts': self._generate_education_charts(data)
        }
    
    def _calculate_risk_level(self, data: Dict) -> str:
        """Calculate overall risk level based on threat data."""
        threat_count = data.get('total_threats', 0)
        high_risk_threats = len([t for t in data.get('threats', []) 
                               if t.get('severity') == 'high'])
        
        if high_risk_threats > 5 or threat_count > 20:
            return 'Critical'
        elif high_risk_threats > 2 or threat_count > 10:
            return 'High'
        elif high_risk_threats > 0 or threat_count > 5:
            return 'Medium'
        return 'Low'
    
    def _categorize_threats(self, threats: List[Dict]) -> Dict:
        """Categorize threats by type and severity."""
        categories = {}
        for threat in threats:
            threat_type = threat.get('type', 'unknown')
            if threat_type not in categories:
                categories[threat_type] = {
                    'count': 0,
                    'severity_breakdown': {'high': 0, 'medium': 0, 'low': 0}
                }
            categories[threat_type]['count'] += 1
            severity = threat.get('severity', 'low')
            categories[threat_type]['severity_breakdown'][severity] += 1
        return categories
    
    def _generate_overview_charts(self, data: Dict) -> List[Dict]:
        """Generate charts for security overview."""
        charts = []
        
        # Threat trend chart
        threat_trend = go.Figure(data=[
            go.Scatter(x=data.get('dates', []), 
                      y=data.get('threat_counts', []),
                      mode='lines+markers')
        ])
        threat_trend.update_layout(title='Threat Trend Over Time')
        charts.append({
            'title': 'Threat Trend',
            'plot': threat_trend.to_html()
        })
        
        # Add more charts as needed
        return charts
    
    def _analyze_high_risk_threats(self, data: Dict) -> List[Dict]:
        """Analyze high risk threats in detail."""
        high_risk_threats = [
            threat for threat in data.get('threats', [])
            if threat.get('severity') == 'high'
        ]
        return [{
            'id': threat.get('id'),
            'type': threat.get('type'),
            'timestamp': threat.get('timestamp'),
            'details': threat.get('details'),
            'mitigation_status': threat.get('mitigation_status')
        } for threat in high_risk_threats]
    
    def _identify_attack_patterns(self, data: Dict) -> List[Dict]:
        """Identify patterns in attack data."""
        threats = data.get('threats', [])
        patterns = {}
        
        for threat in threats:
            pattern_key = f"{threat.get('type')}_{threat.get('source')}"
            if pattern_key not in patterns:
                patterns[pattern_key] = {
                    'count': 0,
                    'first_seen': threat.get('timestamp'),
                    'last_seen': threat.get('timestamp'),
                    'sources': set()
                }
            patterns[pattern_key]['count'] += 1
            patterns[pattern_key]['last_seen'] = threat.get('timestamp')
            patterns[pattern_key]['sources'].add(threat.get('source'))
        
        return [{
            'pattern': k,
            'count': v['count'],
            'duration': v['last_seen'] - v['first_seen'],
            'unique_sources': len(v['sources'])
        } for k, v in patterns.items()]
    
    def _format_as_html(self, report_content: Dict) -> str:
        """Format report content as HTML."""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .section {{ margin-bottom: 20px; }}
                .chart {{ margin: 20px 0; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>{title}</h1>
            <p>Generated at: {generated_at}</p>
            {content}
        </body>
        </html>
        """
        
        content = self._dict_to_html(report_content)
        return html_template.format(
            title=report_content['title'],
            generated_at=report_content['generated_at'],
            content=content
        )
    
    def _dict_to_html(self, data: Dict, level: int = 1) -> str:
        """Convert dictionary content to HTML."""
        html = ""
        for key, value in data.items():
            if key == 'charts':
                for chart in value:
                    html += f'<div class="chart">{chart["plot"]}</div>'
            elif isinstance(value, dict):
                html += f'<h{level}>{key.replace("_", " ").title()}</h{level}>'
                html += self._dict_to_html(value, level + 1)
            elif isinstance(value, list):
                html += f'<h{level}>{key.replace("_", " ").title()}</h{level}>'
                html += '<ul>'
                for item in value:
                    if isinstance(item, dict):
                        html += f'<li>{self._dict_to_html(item, level + 1)}</li>'
                    else:
                        html += f'<li>{item}</li>'
                html += '</ul>'
            else:
                html += f'<p><strong>{key.replace("_", " ").title()}:</strong> {value}</p>'
        return html
    
    def save_report(self, report_content: str, output_path: str):
        """Save the generated report to a file."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
    
    def _generate_recommendations(self, data: Dict) -> List[str]:
        """Generate security recommendations based on threat data."""
        recommendations = []
        threat_types = set(t.get('type') for t in data.get('threats', []))
        
        if 'malware' in threat_types:
            recommendations.append('Update antivirus definitions and perform full system scan')
        if 'network_attack' in threat_types:
            recommendations.append('Review firewall rules and network security settings')
        if 'phishing' in threat_types:
            recommendations.append('Conduct phishing awareness training for users')
        
        return recommendations
    
    def _analyze_bandwidth(self, data: Dict) -> Dict:
        """Analyze bandwidth usage patterns."""
        return {
            'total_bytes': data.get('total_bytes', 0),
            'average_speed': data.get('average_speed', 0),
            'peak_usage': data.get('peak_usage', 0),
            'peak_time': data.get('peak_time')
        }
    
    def _analyze_services(self, data: Dict) -> List[Dict]:
        """Analyze active network services."""
        services = data.get('services', [])
        return [{
            'name': service.get('name'),
            'port': service.get('port'),
            'connections': service.get('connections', 0),
            'bandwidth': service.get('bandwidth', 0)
        } for service in services]
    
    def _analyze_connections(self, data: Dict) -> Dict:
        """Analyze network connections."""
        connections = data.get('connections', [])
        return {
            'total': len(connections),
            'by_protocol': self._group_by_protocol(connections),
            'by_status': self._group_by_status(connections),
            'top_destinations': self._get_top_destinations(connections)
        }
    
    def _analyze_assessments(self, data: Dict) -> Dict:
        """Analyze user education assessment results."""
        assessments = data.get('assessments', [])
        return {
            'average_score': sum(a.get('score', 0) for a in assessments) / len(assessments) if assessments else 0,
            'completed_count': len(assessments),
            'by_module': self._group_by_module(assessments)
        }
    
    def _group_by_protocol(self, connections: List[Dict]) -> Dict:
        """Group connections by protocol."""
        protocols = {}
        for conn in connections:
            protocol = conn.get('protocol', 'unknown')
            protocols[protocol] = protocols.get(protocol, 0) + 1
        return protocols
    
    def _group_by_status(self, connections: List[Dict]) -> Dict:
        """Group connections by status."""
        status = {}
        for conn in connections:
            conn_status = conn.get('status', 'unknown')
            status[conn_status] = status.get(conn_status, 0) + 1
        return status
    
    def _get_top_destinations(self, connections: List[Dict], limit: int = 10) -> List[Dict]:
        """Get top connection destinations."""
        destinations = {}
        for conn in connections:
            dest = conn.get('destination', 'unknown')
            destinations[dest] = destinations.get(dest, 0) + 1
        
        return sorted(
            [{'destination': k, 'count': v} for k, v in destinations.items()],
            key=lambda x: x['count'],
            reverse=True
        )[:limit]
    
    def _group_by_module(self, assessments: List[Dict]) -> Dict:
        """Group assessment results by module."""
        modules = {}
        for assessment in assessments:
            module = assessment.get('module', 'unknown')
            if module not in modules:
                modules[module] = {
                    'count': 0,
                    'total_score': 0,
                    'average_score': 0
                }
            modules[module]['count'] += 1
            modules[module]['total_score'] += assessment.get('score', 0)
            modules[module]['average_score'] = (
                modules[module]['total_score'] / modules[module]['count']
            )
        return modules
