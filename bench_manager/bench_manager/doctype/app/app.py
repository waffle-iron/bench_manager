# -*- coding: utf-8 -*-
# Copyright (c) 2017, Frappé and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from subprocess import check_output, Popen, PIPE
import sys
import re

class App(Document):
	def validate(self):
		if self.get("__islocal"):
			if self.bypass_flag == 0:
				self.create_app()
			self.bypass_flag = 0
			self.update_app_details()
		else:
			if self.bypass_flag == 0:
				self.update_app_details()

	def create_app(self):
		app_list = check_output("cd ../apps && ls",
			shell=True).split("\n")
		if self.app_name in app_list:
			frappe.throw("App: "+ self.app_name + " already exists, but most\
				likely there isn't a log of this app. Please click sync to\
				refresh your app list!")
		else:
			if ' ' in self.app_name:
				frappe.throw("The app name should be developer friendly, and \
					should not contain spaces !")
			else:
				terminal = Popen("cd .. && bench new-app " + self.app_name,
					stdin=PIPE, shell=True)
				self.app_title = self.app_title + '\n'
				self.app_description = self.app_description + '\n'
				self.app_publisher = self.app_publisher + '\n' 
				self.app_email = self.app_email + '\n'
				self.app_icon = self.app_icon + '\n' if self.app_icon!=None else '\n'
				self.app_color = self.app_color + '\n' if self.app_color!=None else '\n'
				self.app_license = self.app_license + '\n' if self.app_license!=None else '\n'
				terminal.communicate(self.app_title + self.app_description + 
					self.app_publisher + self.app_email + self.app_icon + 
					self.app_color + self.app_license)
				if self.app_title == None:
					self.app_title = self.app_name
					self.app_title = self.app_title.replace('-', ' ')
					self.app_title = self.app_title.replace('_', ' ')

	def on_trash(self):
		if self.bypass_flag == 0:
			frappe.throw('Not allowed!')

	def update_app_details(self):
		try:
			app_data_path = '../apps/'+self.app_name+'/'+self.app_name+'.egg-info/PKG-INFO'
			with open(app_data_path, 'r') as f:
				app_data = f.readlines()
			for data in app_data:
				if 'Version:' in data:
					self.version = ''.join(re.findall('Version: (.*?)\\n', data))
				elif 'Summary:' in data:
					self.app_description = ''.join(re.findall('Summary: (.*?)\\n', data))
				elif 'Author:' in data:
					self.app_publisher = ''.join(re.findall('Author: (.*?)\\n', data))
				elif 'Author-email:' in data:
					self.app_email = ''.join(re.findall('Author-email: (.*?)\\n', data))
			self.app_title = self.app_name
			self.app_title = self.app_title.replace('-', ' ')
			self.app_title = self.app_title.replace('_', ' ')
		except:
			frappe.throw("Hey developer, the app you're trying to create an \
				instance of doesn't actually exist. You could consider setting \
				bypass flag to 0 to actually create the app")