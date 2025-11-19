from datetime import datetime, timedelta
from pathlib import Path
import pickle

import pandas
import psycopg2
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from highcharts_core.chart import Chart
from pandas_highcharts.core import serialize
import os
import geopandas as gpd
import json
import logging

import geojson
from dssatservice.ui.base import AdminBase, Session
from dssatservice.ui.plot import (
    init_stress_chart, get_stress_series_data,
    get_columnRange_series_data,
    init_columnRange_chart, clear_yield_chart, clear_stress_chart,
    current_forecast_yield_plot, current_forecast_stress_plot
)
from highcharts_core.chart import Chart

logger = logging.getLogger('dssat')

BASE_DIR = Path(__file__).resolve().parent.parent
f = open(str(BASE_DIR) + '/data.json', )
config = json.load(f)


def get_session(request):
    """
    Helper function to recreate the Session object from session data.
    """
    con_params = request.session.get('con_params')
    session_data = request.session.get('session_data')

    if not con_params or not session_data:
        return None

    # Re-establish the database connection
    con = psycopg2.connect(**con_params)
    # Recreate the Session object
    return Session(AdminBase(con, session_data['admin1_country'], session_data['admin1_name']))


def connect(dbname):
    con = psycopg2.connect(
        database=config['USERNAME'],
        user=config['DBUSER'],
        password=config['PASSWORD'],
        host=config['HOST'],
        port=5432,
    )
    return con


def to_js_literal(chart_dict):
    return Chart.from_dict(chart_dict).to_js_literal()


def get_user_session(request):
    if not hasattr(request, 'user_session'):
        request.user_session = {}
    return request.user_session


def get_geojson():
    import pandas as pd
    data = pd.read_json('C:\\Users\\gtondapu\\Downloads\\zimbabwe_fewsnet_admin2.geojson')
    import json
    data = json.load(open('C:\\Users\\gtondapu\\Downloads\\zimbabwe_fewsnet_admin2.geojson'))
    return data["result"]


def home(request):
    return render(request, 'index.html', )


@csrf_exempt
def sensitivity_charts(request):
    admin1 = request.POST.get('param1')
    admin1_name = admin1.split('_')[0]
    admin1_country = 'alabama' #admin1.split('_')[1]

    # Store connection and session data in Django session
    con_params = {
        "database": config['USERNAME'],
        "user": config['DBUSER'],
        "password": config['PASSWORD'],
        "host": config['HOST'],
        "port": 5432
    }
    session_data = {
        "admin1_country": admin1_country,
        "admin1_name": admin1_name,
    }
    request.session['con_params'] = con_params
    request.session['session_data'] = session_data

    # Recreate the Session object for initializing charts
    session = get_session(request)

    # Initialize charts
    # anom_chart = init_anomalies_chart()
    print(session)
    r_chart = init_columnRange_chart(session)

    stress_chart_water = init_stress_chart('water')
    stress_chart_nitrogen = init_stress_chart('nitrogen')

    # Set containers
    stress_chart_water["container"] = 'stress_chart_water'
    stress_chart_nitrogen["container"] = 'stress_chart_nitrogen'
    # anom_chart["container"] = 'anomaly_chart'
    r_chart["container"] = 'column_chart'

    # Convert charts to dictionary format and store in session
    request.session['range_chart'] = r_chart
    request.session['sw'] = stress_chart_water
    # request.session['anomaly_chart'] = anom_chart
    request.session['sn'] = stress_chart_nitrogen



    # desc, column, cultivars, x = validation_ch(request, admin1)
    forecast_chart = current_forecast_yield_plot(session)
    forecast_chart["container"] = "forecast_chart"
    forecast_stress_chart = current_forecast_stress_plot(session)
    forecast_stress_chart["container"] = "forecast_stress_chart"
    # cultivars = list(session.adminBase.cultivar_labels.keys())
    cultivar_types = [f"{i} season" for i in session.adminBase.cultivars.index]
    cultivar_codes = [i for i in session.adminBase.cultivars.cultivar]
    desc = ""
    # print(cultivars, cultivars_codes)
    max_date = datetime.today() + timedelta(30)
    # Render the response
    return render(request, 'sensitivity_chart.html', {
        'admin1': admin1_name,
        'admin1_country': admin1_country.title(),
        'cultivar_types': cultivar_types,  # Placeholder, modify as needed
        'cultivar_codes': cultivar_codes,  # Placeholder, modify as needed
        'forecast_chart': to_js_literal(forecast_chart),  # Placeholder, modify as needed
        'forecast_stress_chart': to_js_literal(forecast_stress_chart),
        'range_chart': to_js_literal(r_chart),
        # 'anomaly_chart': to_js_literal(anom_chart),
        'stress_chart_water': to_js_literal(stress_chart_water),
        'stress_chart_nitrogen': to_js_literal(stress_chart_nitrogen),
        'max_date': max_date
    })
@csrf_exempt
def irrigation_charts(request):
    if request.method == 'POST':
        admin1 = request.POST.get('param1')
        admin1_name = admin1.split('_')[0]
        admin1_country = 'alabama'

        conn = psycopg2.connect(
            dbname=config['USERNAME'],
            user=config['DBUSER'],
            password=config['PASSWORD'],
            host=config['HOST'],
            port="5432"
        )

        cultivar = 'long'  # Example: You can dynamically get this value
        soil_type = 'unknown'  # Example: You can dynamically get this value

        with conn.cursor() as cursor:
            # Dropdowns for cultivars and soil types
            cursor.execute("SELECT DISTINCT cultivar FROM alabama.historical_yield ORDER BY cultivar ASC")
            cultivars = [row[0].strip() for row in cursor.fetchall()]

            cursor.execute("SELECT DISTINCT soil_type FROM alabama.soil_type ORDER BY soil_type ASC")
            soil_types = [row[0].strip() for row in cursor.fetchall()]

            # Get FIPS code for the given county
            cursor.execute("SELECT fips_code FROM alabama.county WHERE LOWER(name::text) = LOWER(%s)", (admin1_name,))
            fips_code = cursor.fetchone()[0]

            # Long-term average per crop
            cursor.execute("""
                SELECT crop_name, AVG(rainfed) AS avg_rainfed, AVG(irrigated) AS avg_irrigated
                FROM alabama.historical_yield
                WHERE cultivar = %s AND soil_type = %s AND fips_code = %s
                GROUP BY crop_name
                ORDER BY crop_name;
            """, [cultivar, soil_type, fips_code])
            rows = cursor.fetchall()

            # Extract the categories (crop names) and averages
            categories = [row[0] for row in rows]
            rainfed = [round(row[1]*0.0159, 2) for row in rows]  # Apply unit conversion if necessary
            irrigated = [round(row[2]*0.0159, 2) for row in rows]  # Apply unit conversion if necessary

            # By year for the new chart (no aggregation for means)
            cursor.execute("""
                SELECT year,
                       rainfed,
                       irrigated,
                       precipitation_mean,
                       irrigated_mean
                FROM alabama.historical_yield
                WHERE cultivar = %s AND soil_type = %s AND fips_code = %s
                ORDER BY year;
            """, [cultivar, soil_type, fips_code])
            results = cursor.fetchall()

            # Extract year-based data
            years = [row[0] for row in results]
            rainfed_year = [row[1]*0.0159 for row in results]  # Apply unit conversion if necessary
            irrigated_year = [row[2]*0.0159 for row in results]  # Apply unit conversion if necessary
            precip_mean_year = [row[3]  for row in results]  # Apply unit conversion if necessary
            irrigated_mean_year = [row[4] for row in results]  # Apply unit conversion if necessary

            # Pass the data to the context
            context = {
                'cultivars': cultivars,
                'soil_types': soil_types,
                'categories': json.dumps(categories),
                'rainfed': json.dumps(rainfed),
                'irrigated': json.dumps(irrigated),
                'years': json.dumps(years),
                'rainfed_year': json.dumps(rainfed_year),
                'irrigated_year': json.dumps(irrigated_year),
                'precip_mean_year': json.dumps(precip_mean_year),
                'irrigated_mean_year': json.dumps(irrigated_mean_year),
                'admin1': f"{admin1_name}, Alabama",
                'admin1_country': admin1_country.title(),
            }

        return render(request, 'irrigation_chart.html', context)

    # If GET or other methods, render the page with an empty context
    return render(request, 'irrigation_chart.html', {})




@csrf_exempt
def run_experiment(request):
    # try:
    admin1 = request.POST.get('param1')
    schema = request.POST.get('schema')
    admin1 = request.POST.get('admin1')

    # Retrieve and recreate the session object
    session = get_session(request)
    if session is None:
        return JsonResponse({'error': 'no session'})

    # Retrieve charts from the session
    range_chart = request.session.get('range_chart')
    water_stress_chart = request.session.get('sw')
    nitro_stress_chart = request.session.get('sn')
    # Update session parameters
    logger.debug("Debug message: Entering sample_view")
    logger.debug(request.POST.get('planting_date') + " - Date")
    session.simPars.planting_date = datetime.strptime(request.POST.get('planting_date'), '%Y-%m-%d')
    session.simPars.cultivar = request.POST.get('cultivar')
    session.simPars.nitrogen_rate = [
        int(i) for i in request.POST.getlist('nitrogen_rate[]')
    ]
    session.simPars.nitrogen_dap = [
        int(i) for i in request.POST.getlist('nitrogen_dap[]')
    ]
    session.simPars.irrigation = request.POST.get('irrigation') == "yes"
    print(session.simPars)
    session.run_experiment(fakerun=False, weather_table = 'prism')

    # Update charts with new data
    series_len = len(range_chart["userOptions"]["series"])

    new_chart_data_range = get_columnRange_series_data(
        session, series_len
    ).to_dict()
    range_chart["userOptions"]["series"].append(
        new_chart_data_range
    )

    new_chart_data_water = get_stress_series_data(
        session, stresstype="water"
    )
    # n_exps = len(water_stress_chart["userOptions"]["series"])
    new_chart_data_water["name"] = f"Exp {series_len + 1}"

    new_chart_data_nitro = get_stress_series_data(
        session, stresstype="nitrogen"
    )
    new_chart_data_nitro["name"] = f"Exp {series_len + 1}"

    # Save the updated charts back to the session
    request.session['range_chart'] = range_chart
    request.session['sw'] = water_stress_chart
    request.session['sn'] = nitro_stress_chart

    # Return the response
    return JsonResponse({
        'error': '',
        # 'anomaly_chart': anomaly_chart["userOptions"],
        # 'aseries': new_chart_data_an,
        'rdata': new_chart_data_range,
        'range_chart': range_chart["userOptions"],
        'stress_chart_water': new_chart_data_water,
        'stress_chart_nitrogen': new_chart_data_nitro
    })


def about(request):
    return render(request, 'about.html')


@csrf_exempt
def clear_charts(request, admin1):
    try:
        session = get_session(request)

        # anom_chart = init_anomalies_chart()
        r_chart = init_columnRange_chart(session)
        stress_chart_water = init_stress_chart('water')
        stress_chart_nitrogen = init_stress_chart('nitrogen')
        # Set containers
        stress_chart_water["container"] = 'stress_chart_water'
        stress_chart_nitrogen["container"] = 'stress_chart_nitrogen'
        # anom_chart["container"] = 'anomaly_chart'
        r_chart["container"] = 'column_chart'

        # Convert charts to dictionary format and store in session
        request.session['range_chart'] = r_chart
        request.session['sw'] = stress_chart_water
        # request.session['anomaly_chart'] = anom_chart
        request.session['sn'] = stress_chart_nitrogen
        clear_yield_chart(request.session['range_chart'])
        clear_stress_chart(request.session['sw'])
        clear_stress_chart(request.session['sn'])
        clear_yield_chart(request.session['anomaly_chart'])

        return JsonResponse({
            'error': '',
            'anomaly_chart': request.session['anomaly_chart']["userOptions"],
            'range_chart': request.session['range_chart']["userOptions"],
            'stress_chart_water': request.session['sw']['userOptions'],
            'stress_chart_nitrogen': request.session['sn']["userOptions"]["series"]
        })
    except Exception as e:
        return JsonResponse({'error': str(e)})
