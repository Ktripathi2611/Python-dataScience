from flask import Blueprint, render_template

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/')
def main_dashboard():
    return render_template('dashboard/main_dashboard.html')

@dashboard.route('/ddos-protection')
def ddos_protection():
    return render_template('dashboard/ddos_protection.html')

@dashboard.route('/network-security')
def network_security():
    return render_template('dashboard/network_security.html')

@dashboard.route('/feature-list')
def feature_list():
    return render_template('dashboard/feature_list.html')

@dashboard.route('/upcoming-features')
def upcoming_features():
    return render_template('dashboard/upcoming_features.html')

@dashboard.route('/dashboard/feature_overview')
def feature_overview():
    return render_template('dashboard/feature_overview.html')

@dashboard.route('/dashboard/development_status')
def development_status():
    return render_template('dashboard/development_status.html')

@dashboard.route('/packet-analyzer')
def packet_analyzer():
    return render_template('dashboard/packet_analyzer.html')
