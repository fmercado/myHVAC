from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.shortcuts import render, get_object_or_404, reverse
from django.http import Http404
from django.views import generic
from django.utils import timezone
from .models import Hvac, Command
from django.conf import settings
import requests


class IndexView(generic.ListView):
    """Index view, , no special treatment, all HVAC's are shown"""
    template_name = 'hvac/index.html'
    context_object_name = 'list_hvacs'
    model = Hvac


class DetailView(generic.DetailView):
    """Detail view"""
    model = Hvac
    template_name = 'hvac/detail.html'


def command(request, hvac_id):
    """Receive the new HVAC parameters and apply them"""
    hvac = get_object_or_404(Hvac, pk=hvac_id)

    cmd = Command.objects.create(room_temperature=10, target_temperature=request.POST['temp'],
                                 date_issued=timezone.now(), fan_speed=request.POST['fan'], mode=request.POST['mode'],
                                 hvac_webid=hvac.equipment, hvac=hvac
                                 )
    a = BghClient(settings.HVAC_USER, settings.HVAC_PASSWD)
    a.set_mode(hvac.equipment, request.POST['mode'], request.POST['temp'])

    return HttpResponseRedirect(reverse('hvac:index', args=()))


def plot(request, hvac_id):
    """Return a Json object with the history of user targeted temps for the corresponding HVAC"""
    commands = Command.objects.filter(hvac=hvac_id)
    temperatures = []
    for cmd in commands:
        temperatures.append(cmd.target_temperature)
    return JsonResponse({'temperature_data_set': temperatures})


class BghClient():
    """Class to handle the interactions to the HVAC controller endpoint."""

    def __init__(self, email, password):
        self.token = self._login(email, password)

    @staticmethod
    def _login(email, password):
        endpoint = "%s/control/LoginPage.aspx/DoStandardLogin" % settings._BASE_URL
        resp = requests.post(endpoint, json={'user': email, 'password': password})
        return resp.json()['d']

    def _request(self, endpoint, payload=None):
        """Request function will always enforce the auth Tokens."""
        if payload is None:
            payload = {}
        payload['token'] = {'Token': self.token}
        return requests.post(endpoint, json=payload)

    def _get_data_packets(self, home_id):
        """Get data packets as the api calls them."""
        endpoint = "%s/HomeCloudService.svc/GetDataPacket" % settings._API_URL
        payload = {
            'homeID': home_id,
            'serials': {
                'Home': 0,
                'Groups': 0,
                'Devices': 0,
                'Endpoints': 0,
                'EndpointValues': 0,
                'Scenes': 0,
                'Macros': 0,
                'Alarms': 0
            },
            'timeOut': 10000
        }
        resp = self._request(endpoint, payload)
        return resp.json()['GetDataPacketResult']

    def get_homes(self):
        """Get all the homes of the account"""
        endpoint = "%s/HomeCloudService.svc/EnumHomes" % settings._API_URL
        resp = self._request(endpoint)
        return resp.json()['EnumHomesResult']['Homes']

    def get_devices(self, home_id):
        """Get all the devices of a home"""
        data = self._get_data_packets(home_id)
        return data

    def get_HVAC_status(self, endpoint):
        """Get the current status of the HVAC's @ home
            (room_temperature, target_temperature, fan_speed, mode)
        """
        status = {}
        devices = self.get_devices(settings.HVAC_HOMEID)
        for device in devices['EndpointValues']:
            if device['EndpointID'] == endpoint:
                status = self._parse_values(device['Values'])
        return status

    def _set_device_mode(self, device_id, mode):
        """Issue the command to the HVAC endpoint"""
        mode['endpointID'] = device_id
        endpoint = "%s/HomeCloudCommandService.svc/HVACSetModes" % settings._API_URL
        resp = self._request(endpoint, mode)
        return resp

    def set_mode(self, device_id, mode, temp, fan='auto'):
        """Set the mode of a device"""
        config = {
            'desiredTempC': str(temp),
            'fanMode': settings.FAN_MODE[fan],
            'flags': 255,
            'mode': settings.MODE[mode]
        }
        return self._set_device_mode(device_id, config)

    def _parse_values(self, values):
        """Parse values for each device
        Will try to decode MODE and FAN SPEED
        TODO: Show this values in the app."""

        parsed_vals = {}
        # ValueTypes of our interest
        conv_dict = {13: 'RoomTemp', 20: 'TargetTemp', 15: 'FanSpeed', 14: 'HvacMode'}

        for value in values:
            if value['ValueType'] in conv_dict.keys():
                parsed_vals[conv_dict[int(value['ValueType'])]] = value['Value']
        try:
            parsed_vals['HvacMode'] = \
                settings.MODE.keys()[settings.MODE.values().index(int(parsed_vals['HvacMode']))]

            parsed_vals['FanSpeed'] = \
                settings.FAN_MODE.keys()[settings.FAN_MODE.values().index(int(parsed_vals['FanSpeed']))]
        except:
            pass

        return parsed_vals
