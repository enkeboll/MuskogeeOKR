import datetime
import json

from flask import (
    Blueprint,
    jsonify,
    render_template,
    request,
    send_from_directory
)
import requests

from app import config

TEST_LOOK_ID = '5167'

blueprint_http = Blueprint('blueprint_http', __name__, static_folder='build')

@blueprint_http.route('/')
def front_page():
    # return send_from_directory('./build/', 'index.html')
    return render_template('index.html')


@blueprint_http.route('/_status')
def status():
    """ Status endpoint """
    return jsonify({
        "status": "ok"
    })

@blueprint_http.route('/update')
def update():
    email = request.args.get('email')
    look_id = request.args.get('look_id')
    value = _get_looker(look_id)

    betterworks_id = _get_betterworks_user_id(email)
    goal_ids = _get_betterworks_goals_for_uid(betterworks_id)

    resp = _post_betterworks_goal_update(goal_ids[1]['id'], value)

    return jsonify({
        "email": email,
        "look_value": value,
        "post_status": resp.status_code
    })

def _get_looker(look_id=TEST_LOOK_ID):
    auth = {
        'client_id': config.LOOKER_CLIENT_ID,
        'client_secret': config.LOOKER_CLIENT_SECRET
    }

    response = requests.post('{}/login'.format(config.LOOKER_API_URL), data=auth)
    if response.status_code != 200:
        raise RuntimeError

    token = response.json()['access_token']
    header = {'Authorization': 'token {}'.format(token)}

    resp = requests.get('{}/looks/{}/run/json'.format(config.LOOKER_API_URL, look_id), headers=header)
    cont = resp.json()
    # take the first value of the first record.  there should be only one in the look!
    look_val = cont[0].values()[0]

    return look_val

def _get_onelogin_token():
    header = {'Authorization': 'client_id:{}, client_secret:{}'.format(config.ONELOGIN_ID,
                                                                       config.ONELOGIN_SECRET),
              'Content-Type': 'application/json'}
    body = json.dumps({'grant_type': "client_credentials"})

    response = requests.post('{}/auth/oauth2/token'.format(config.ONELOGIN_AUTH_URL), headers=header, data=body)
    
    if response.status_code != 200:
        raise RuntimeError

    return response.json()['data'][0]['access_token']


def _get_onelogin_users(token=None):
    if token is None:
        token = _get_onelogin_token()
    header = {'Authorization': 'bearer:{}'.format(token)}

    users = []

    url = '{}/users?role_id={}&fields=id, username, firstname, email'.format(config.ONELOGIN_API_URL,
                                                                             config.ONELOGIN_ALL_USERS_ROLE_ID)
    while url:
        resp = requests.get(url, headers=header)
        cont = resp.json()
        users.extend(cont['data'])
        url = cont['pagination']['next_link']

    return users

def _get_onelogin_user_apps(userid, token=None):
    if token is None:
        token = _get_onelogin_token()
    header = {'Authorization': 'bearer:{}'.format(token)}

    url = '{}/users/{}/apps'.format(config.ONELOGIN_API_URL, userid)

    resp = requests.get(url, headers=header)
    return resp.json()['data']

def _extract_betterworks_id_from_onelogin(apps=[]):
    for app in apps:
        if app['name'] == config.ONELOGIN_BETTERWORKS_NAME:
            return app['login_id']
    return None


def _get_betterworks_user_id(email_address=''):
    header = {"Authorization": "APIToken {}".format(config.BETTERWORKS_TOKEN)}
    url = "{}/users/{}/".format(config.BETTERWORKS_API_URL,
                                email_address)
    resp = requests.get(url, headers=header)
    return resp.json()['id']

def _get_betterworks_goals_for_uid(user_id):
    header = {"Authorization": "APIToken {}".format(config.BETTERWORKS_TOKEN)}
    url = "{}/goals/filter/?owner={}".format(config.BETTERWORKS_API_URL,
                                             user_id)
    resp = requests.get(url, headers=header)
    goals = _extract_goals_from_resp(resp.json()['results'])
    return goals

def _extract_goals_from_resp(results):
    goals = []
    for result in results:
        if result['is_key_result']:
            goals.append({'id': result['id'],
                          'name': result['name']})
        if 'children' in result:
            goals.extend(_extract_goals_from_resp(result['children']))
    return goals

def _post_betterworks_goal_update(goal_id, goal_value):
    header = {"Authorization": "APIToken {}".format(config.BETTERWORKS_TOKEN)}
    url = "{}/goals/{}/checkin/".format(config.BETTERWORKS_API_URL,
                                        goal_id)
    params = {'value': goal_value}
    resp = requests.post(url, json=params, headers=header)
    return resp



@blueprint_http.errorhandler(404)
def not_found(e):
    return jsonify({
        'page': 'not found'
    }), 404