from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
import json
# from __future__ import print_function
import os
from googleapiclient.discovery import build
from googleapiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools
from oauth2client.client import GoogleCredentials
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import logout
# from django.contrib.auth.forms import UserCreationForm
# from django.urls import reverse_lazy
# from django.views import generic
# Create your views here.

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
# The ID and range of a sample spreadsheet.
PRODUCT_SHEET_ID = '1Ps28slkRXoWNG2y6jbxLnuy3yBUfO5ksBOHoB0n-RX8'
INVENTORY_SHEET_ID = '15gmF9DuVpUCFmZB3_iIBZi-KAcZ4D3QiRtWQWGKl7cQ'
UOM_SHEET_ID = '16uzVIVgVMMz33EGzGhdF071UcA7okxGrS9tsXFGjpio'
product_sheet_name = 'product'
inventory_sheet_name = 'inventory'
uom_sheet_name = 'uom'

def register(request):
	if request.method == 'POST':
		form = UserCreationForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data.get('username')
			messages.success(request, 'Your account has been created! You are availble to login now.')
			return redirect('login')
	else:
		form = UserCreationForm()
	return render(request, 'inventory/register.html', {'form':form})


def inventory(request):
	if request.user.is_authenticated:
		template = loader.get_template('inventory/inventory.html')
		return HttpResponse(template.render())
	else:
		return redirect('login')

def getUOMs(request):
	if request.method == 'POST':
		BASE_DIR = os.path.dirname(os.path.abspath(__file__))

		token_path = os.path.join(BASE_DIR, "templates/inventory/token.json")
		store = file.Storage(token_path)
		creds = store.get()

		if not creds or creds.invalid:

			path = os.path.join(BASE_DIR, "templates/inventory/credentials.json")
			flow = client.flow_from_clientsecrets(path, SCOPES)
			creds = tools.run_flow(flow, store)

		service = build('sheets', 'v4', http=creds.authorize(Http()))

		# Call the Sheets API
		sheet = service.spreadsheets()

		uoms = []
		uom1 = []
		uom2 = []

		sheet_row_index = 2
		check_while = True
		while check_while:
			SAMPLE_RANGE_NAME = uom_sheet_name + '!A'+ str(sheet_row_index) +':C'+ str(sheet_row_index)
			result = sheet.values().get(spreadsheetId=UOM_SHEET_ID, range=SAMPLE_RANGE_NAME).execute()
			values = result.get('values', [])
			if not values:
				print (uoms)
				uoms.append(uom1)
				uoms.append(uom2)
				return HttpResponse(json.dumps(uoms), content_type="application/json")
			else:
				for row in values:
					if row[0] == '':
						check_while = False
						break
					if len(row) == 3:
						uom1.append(row[1])
						uom2.append(row[2])
					else:
						uom1.append(row[1])
				sheet_row_index += 1 
		# return HttpResponse(json.dumps(uoms), content_type="application/json")
	else :
		return HttpResponse('failed')

def ajaxGetBarcode(request):
	if request.method == 'POST':
		barcode = request.POST.get('barcode')

		response_data = {}

		BASE_DIR = os.path.dirname(os.path.abspath(__file__))

		token_path = os.path.join(BASE_DIR, "templates/inventory/token.json")
		store = file.Storage(token_path)
		creds = store.get()

		if not creds or creds.invalid:

			path = os.path.join(BASE_DIR, "templates/inventory/credentials.json")
			flow = client.flow_from_clientsecrets(path, SCOPES)
			creds = tools.run_flow(flow, store)

		service = build('sheets', 'v4', http=creds.authorize(Http()))

		# Call the Sheets API
		sheet = service.spreadsheets()

		sheet_row_index = 2
		check_while = True
		while check_while:
			SAMPLE_RANGE_NAME = product_sheet_name + '!A'+ str(sheet_row_index) +':G'+ str(sheet_row_index)
			result = sheet.values().get(spreadsheetId=PRODUCT_SHEET_ID, range=SAMPLE_RANGE_NAME).execute()
			values = result.get('values', [])
			if not values:
				return HttpResponse('failed')
			else:	
				for row in values:
					if row[0] == '':
						check_while = False
					if row[6] == barcode :
						response_data['title'] = row[1]
						response_data['unit1_count'] = row[2]
						response_data['uom1'] = row[3]
						response_data['unit2_count'] = row[4]
						response_data['uom2'] = row[5]
						response_data['barcode'] = row[6]

						return HttpResponse(json.dumps(response_data), content_type="application/json")
				sheet_row_index += 1 
	else :
		return HttpResponse('failed')
	
def add(request) :
	if request.method == 'POST':
		barcode = request.POST.get('barcode')
		uom1_count = request.POST.get('uom1_count')
		uom1_unit = request.POST.get('uom1_unit')
		uom2_count = request.POST.get('uom2_count')
		uom2_unit = request.POST.get('uom2_unit')
		product_name = request.POST.get('product_name')

		product_statue = request.POST.get('statue')

		BASE_DIR = os.path.dirname(os.path.abspath(__file__))

		token_path = os.path.join(BASE_DIR, "templates/inventory/token.json")
		store = file.Storage(token_path)
		creds = store.get()

		if not creds or creds.invalid:
			path_credential = os.path.join(BASE_DIR, "templates/inventory/credentials.json")
			flow = client.flow_from_clientsecrets(path_credential, SCOPES)
			creds = tools.run_flow(flow, store)

		service = discovery.build('sheets', 'v4', http=creds.authorize(Http()))

		# Call the Sheets API
		sheet = service.spreadsheets()

		if product_statue == '0':
			inventory_sheet_row_count = 0
			sheet_row_index = 2
			check_while = True

			while check_while:
				SAMPLE_RANGE_NAME = inventory_sheet_name + '!A'+ str(sheet_row_index) +':G'+ str(sheet_row_index)
		
				result = sheet.values().get(spreadsheetId=INVENTORY_SHEET_ID, range=SAMPLE_RANGE_NAME).execute()
				values = result.get('values', [])

				if not values:
					break
				else:	
					inventory_sheet_row_count = inventory_sheet_row_count + 1
					sheet_row_index += 1 

			values = [inventory_sheet_row_count+1, product_name, uom1_count, uom1_unit, uom2_count, uom2_unit, barcode]
			range_value = inventory_sheet_name + '!A'+ str(inventory_sheet_row_count+1) +':G'+ str(inventory_sheet_row_count+1)
			body = {
					"values": [values],
			}
			result = sheet.values().append(spreadsheetId=INVENTORY_SHEET_ID, range = range_value,valueInputOption= "USER_ENTERED",body=body).execute()

		elif product_statue == '1' :
			product_sheet_row_count = 0
			inventory_sheet_row_count = 0
			sheet_row_index = 2
			check_while = True

			while check_while:
				SAMPLE_RANGE_NAME = inventory_sheet_name + '!A'+ str(sheet_row_index) +':G'+ str(sheet_row_index)
		
				result = sheet.values().get(spreadsheetId=INVENTORY_SHEET_ID, range=SAMPLE_RANGE_NAME).execute()
				values = result.get('values', [])

				if not values:
					break
				else:	
					inventory_sheet_row_count = inventory_sheet_row_count + 1
					sheet_row_index += 1 

			sheet_row_index = 2
			while check_while:
				SAMPLE_RANGE_NAME = product_sheet_name + '!A'+ str(sheet_row_index) +':G'+ str(sheet_row_index)
		
				result = sheet.values().get(spreadsheetId=PRODUCT_SHEET_ID, range=SAMPLE_RANGE_NAME).execute()
				values = result.get('values', [])

				if not values:
					break
				else:	
					product_sheet_row_count = product_sheet_row_count + 1
					sheet_row_index += 1 

			values = [inventory_sheet_row_count+1, product_name, uom1_count, uom1_unit, uom2_count, uom2_unit, barcode]
			range_value = inventory_sheet_name + '!A'+ str(inventory_sheet_row_count+1) +':G'+ str(inventory_sheet_row_count+1)
			body = {
					"values": [values],
			}
			result = sheet.values().append(spreadsheetId=INVENTORY_SHEET_ID, range = range_value,valueInputOption= "USER_ENTERED",body=body).execute()

			values = [product_sheet_row_count+1, product_name, uom1_count, uom1_unit, uom2_count, uom2_unit, barcode]
			range_value = product_sheet_name + '!A'+ str(product_sheet_row_count+1) +':E'+ str(product_sheet_row_count+1)
			body = {
					"values": [values],
			}
			result = sheet.values().append(spreadsheetId=PRODUCT_SHEET_ID, range = range_value,valueInputOption= "USER_ENTERED",body=body).execute()

		return HttpResponse('success')
	else :
		return HttpResponse('failed')
