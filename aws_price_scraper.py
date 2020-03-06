#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import urllib.request
try:
	import hjson
except:
	print('Install hjson with "pip3 install hjson"')
	quit()
try:
	from tabulate import tabulate
except:
	print('Install tabulate with "pip3 install tabulate"')
	quit()

def get_prices(AMI, instanceType, performance):
	
	req = urllib.request.Request(
		AMI, 
		data=None,
		headers={
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0'
		}
	)
	
	page = urllib.request.urlopen(req)
	
	page_content = page.read().decode('utf-8')
	
	cd = page_content[page_content.find('/*<![CDATA[*/') + 13:page_content.find('/*]]>*/',page_content.find('/*<![CDATA[*/') + 13)]
	
	productId = cd[cd.find('productId: "') + 12:cd.find('"',cd.find('productId: "') + 12)]
	
	hjson_string = cd[cd.find('var awsmpInitialState = ') + 24:cd.find('};',cd.find('var awsmpInitialState = ') + 24) + 1]
	
	hjson_dict = hjson.loads(hjson_string)
	
	prices = {}
	
	for region in hjson_dict['offerIon']['offer']['pricing']['regions']:
		for idx, row in enumerate(hjson_dict['offerIon']['offer']['pricing']['regions'][region][productId]['hourly']['displayElements']['properties']['rows']):
			if hjson_dict['offerIon']['offer']['pricing']['regions'][region][productId]['hourly']['displayElements']['properties']['rows'][idx]['instanceType'] == instanceType:
				hourly_rate = float(hjson_dict['offerIon']['offer']['pricing']['regions'][region][productId]['hourly']['displayElements']['properties']['rows'][idx]['totalRate'])
				results.append([instanceType, region, hourly_rate, round((100000000/performance)*(hourly_rate/3600), 3)])

results_headers = ['Instance Type', 'Region', 'Price per hour', 'Price per 100M passwords']
results = []

get_prices('https://aws.amazon.com/marketplace/pp/B073WHLGMC', 'g3s.xlarge',  4616)
get_prices('https://aws.amazon.com/marketplace/pp/B07TS3S3ZH', 'g4dn.xlarge',  8293)
get_prices('https://aws.amazon.com/marketplace/pp/B07TS3S3ZH', 'p3.2xlarge',  21088)

print(tabulate(results, headers = results_headers))

index_ap = 0
index_eu = 0
index_us = 0
cheapest_ap = 999
cheapest_eu = 999
cheapest_us = 999

for i, x in enumerate(results):
	if (x[1][:2] == 'ap') and (x[3] < cheapest_ap):
		cheapest_ap = x[3]
		index_ap = i
	if (x[1][:2] == 'eu') and (x[3] < cheapest_eu):
		cheapest_eu = x[3]
		index_eu = i
	if (x[1][:2] == 'us') and (x[3] < cheapest_us):
		cheapest_us = x[3]
		index_us = i

print()
print('The cheapest instance in AP: '+str(results[index_ap][0])+' in '+str(results[index_ap][1])+' region. $'+str(results[index_ap][3])+' per 100M passwords ($'+str(results[index_ap][2]*24)+' per day).')
print('The cheapest instance in EU: '+str(results[index_eu][0])+' in '+str(results[index_eu][1])+' region. $'+str(results[index_eu][3])+' per 100M passwords ($'+str(results[index_eu][2]*24)+' per day).')
print('The cheapest instance in US: '+str(results[index_us][0])+' in '+str(results[index_us][1])+' region. $'+str(results[index_us][3])+' per 100M passwords ($'+str(results[index_us][2]*24)+' per day).')