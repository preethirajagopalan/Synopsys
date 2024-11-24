#!/opt/python-2.7.13/bin/python -u
import requests
from pytz import country_timezones
import datetime
import pytz
from geopy import geocoders

class SynopsysSite(object):

	# static
	g = geocoders.GoogleV3(api_key='AIzaSyCI5yUO1daOwq9_M5TVF3Q5nhftxjYyNss')
	#g = geocoders.GoogleV3()

	# constants
	SITE_LENGTH = 4
	COUNTRY_CODE_LENGTH = 2

	# needed information for connection to Synopsys Lookup API
	LOOKUP_BASE_URL = 'https://lookup.synopsys.com/api'
	LOOKUP_TOKEN = '865668c5-56c9-434b-be50-875cabfce3b5'
	CERT_FILE = '/etc/ssl/certs/ca-bundle.crt'


	def __init__(self, site, file_obj=None):
		"""
		:type site: string
		:type file_obj: file
		:rtype: void

		CONSTRUCTOR:
		User passes in a site string to create a SynopsysSite object. The file_obj can be a opened file, enabled for writing, which will
		be used for logging errors when initializing the timezone.

		EXAMPLE USAGE:
		site = SynopsysSite('US11')
		"""

		# initialize timezone
		self.__timezone = self.__initialize_timezone(site, file_obj)


	def get_timezone(self):
		"""
		:rtype: pytz.timezone

		PUBLIC FUNCTION:
		Returns the timezone of the given site.

		EXAMPLE USAGE:
		site = SynopsysSite('US11')
		timezone = site.get_timezone()
		"""
		return self.__timezone


	def get_offset(self, date=None):
		"""
		:type date: datetime
		:rtype: List(int)

		PUBLIC FUNCTION:
		Allows user to get the UTC offset of the Synopsys site. Uses the get_string_offset function and then parses the output, returning
		the offset as a list of integers with the first index as the hours offset and the second index as the minutes offset.

		If the date is NOT specified, then the current datetime is used. Else, the function will take the given date and convert the timezone
		without actually changing the given date and time (ie. 9/04/97 10:30 UTC turns into 9/04/97 10:30 PST).

		EXAMPLE USAGE:
		site = SynopsysSite('US11')
		offset = site.get_offset()
		"""
		# get the offset in string format
		offset = self.get_string_offset(date)

		if offset == None:
			return None

		# parse the string for hours and minutes information
		hours = int(offset[1:3])
		minutes = int(offset[3:])

		# flips sign accordingly
		return [hours, minutes] if offset[0] == '+' else [-hours, -minutes]


	def get_string_offset(self, date=None):
		"""
		:type date: datetime
		:rtype: string

		PUBLIC FUNCTION:
		Allows user to get the UTC offset of the Synopsys site. Returns this information as a string.

		If the date is NOT specified, then the current datetime is used. Else, the function will take the given date and convert the timezone
		without actually changing the given date and time (ie. 9/04/97 10:30 UTC turns into 9/04/97 10:30 PST).

		EXAMPLE USAGE:
		site = SynopsysSite('US11')
		string_offset = site.get_string_offset()
		"""
		# no timezone found
		if self.__timezone == None:
			return None

		# change the timezone of given date, without changing actual date
		date = datetime.datetime.now(tz=self.__timezone) if date == None else self.__timezone.localize(date)

		return date.strftime('%z')
		#print site, date


	def __report_error(self, message, file_obj):
		"""
		:type message: string
		:type file_obj: file
		:rtype: void

		PRIVATE FUNCTION:
		Used to print and log the message to the given file.

		EXAMPLE USAGE:
		file_obj = open('test.txt', 'w')
		self.__report_error('This is a message I want to log.', file_obj)
		"""
		print message
		if file_obj != None:
			file_obj.write(message + '\n')



	def __initialize_timezone(self, site, file_obj):
		"""
		:type site: string
		:type file_obj: file
		:rtype: pytz.timezone

		PRIVATE FUNCTION:
		Initializes the timezone of the SynopsysSite object. Takes one of two approaches, depending on whether the country has more than one
		possible timezone. If there is just one timezone (these countries are statically defined), then the function looks up the site in a static map. Else, the Synopsys
		Lookup API is used to find the latitude / longitude coordinates of the site and resolves this location to a timezone.

		Caveat:
		Though Germany and China have 1 timezone according to https://www.countries-ofthe-world.com/world-time-zones.html, they both have two entries in the static map
		that is imported from pytz. By default, the function uses the first one, which happens to be the correct timezone in both cases. The extraneous timezones are those of very small
		regions, and are likely included in the map for completeness. The function will print a message that informs the user of multiple timezones. Use sites like DE06 or CN49
		to see the output.

		EXAMPLE USAGE:
		self.__initialize_timezone(site, file_obj)
		"""
		# get effective site code, used to search later on
		if site.startswith('US02') or site.startswith('BLDG') or site.startswith('SV2') or site.startswith('SV1'):
			search_site = 'USSV'
		elif site == 'MDCINET' or site == 'POWERINK' or site == 'ACCESO':
			# just leave these, don't follow convention
			search_site = site
		elif site == 'US1D':
			search_site = 'US8K'
		elif site == 'SDC':
			search_site = 'US1A'
		elif site == 'US6AP2P':
			search_site = 'US6A'
		#elif site == 'AU02':
		#	search_site = 'TW52'
		else:
			# just get the first four characters
			search_site = site[:self.SITE_LENGTH]

		# get country code
		if search_site == 'MDCINET':
			country_code = 'DE'
		elif search_site == 'POWERINK' or search_site == 'ACCESO':
			country_code = 'CN'
		elif search_site == 'LK01':
			country_code = 'IN'
		elif search_site == 'USSV' or search_site == 'SV2' or search_site == 'US02' or search_site == 'SV1':
			country_code = 'US'
		else:
			country_code = search_site[:self.COUNTRY_CODE_LENGTH].upper()


		# just one timezone
		if country_code not in ['RU', 'US', 'CA', 'AU', 'CL', 'PT', 'FR', 'GB', 'DK', 'NZ', 'NL', 'MX', 'BR', 'ID', 'KZ', 'MN', 'CD', 'KI', 'FM', 'ES', 'PT', 'EC']:

			if country_code in country_timezones:
				possible_timezones = country_timezones[country_code]
				if len(possible_timezones) != 1:
					print 'More than one possible timezone, using first one: {0}.'.format(', '.join(possible_timezones))

				timezone = country_timezones[country_code][0]
			else:
				self.__report_error('No timezone found for {0}.'.format(site), file_obj)
				return None
		else:
			# parameters
			r = requests.get(self.LOOKUP_BASE_URL + '/sites/code/' + search_site, headers={'Authorization': 'Token token=' + self.LOOKUP_TOKEN}, verify=self.CERT_FILE)
			#print r.status_code
			#print search_site	
			if r.status_code != 200:
				self.__report_error('Lookup request failed for {0}.'.format(site), file_obj)
				return None

			lookup_dict = r.json()
			#print lookup_dict

			if lookup_dict['status'] == 'success':
				data = lookup_dict['data'][0]

				# use lat, long to find the timezone
				lat = data['latitude']
				lng = data['longitude']
				#print lat
				#print lng

				timezone = str(self.g.timezone((lat, lng)))
				print timezone
			else:
				self.__report_error('Lookup failed for {0}.'.format(site), file_obj)
				return None

		# convert the string into a pytz timezone object
		return pytz.timezone(timezone)
