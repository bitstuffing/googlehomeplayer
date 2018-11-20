import logging
import urllib
import os

from django import shortcuts
from django.http import HttpResponse
from django.http import JsonResponse

logger = logging.getLogger(__name__)

class AdministrationUtils():

	@staticmethod
	def render(request,url,context):
		logger.info("rendering url %s" % url)
		return shortcuts.render(request,url,context)

	@staticmethod
	def redirect(url,context={}):
		logger.info("redirecting to %s" % url)
		return shortcuts.redirect(url,context)

	@staticmethod
	def jsonResponse(data):
		logger.debug("returning json response with %s bytes" % str(len(str(data))))
		return JsonResponse(data)

	@staticmethod
	def httpResponse(data):
		logger.debug("returning http response with %s bytes" % str(len(str(data))))
		return HttpResponse(data)

	@staticmethod
	def download(request, path, filename=''):
		#file_path = os.path.join(settings.MEDIA_ROOT, path)
		if filename=='':
			filename = path
		try: #python 2
			filename = urllib.quote_plus(filename)
		except: #python 3 issues
			filename = urllib.parse.quote_plus(filename)
			pass
		if os.path.exists(path):
			with open(path, 'rb') as fh:
				response = HttpResponse(fh.read(), content_type="application/octet-stream")
				response['Content-Disposition'] = 'inline; filename=' + os.path.basename(filename)
				return response
		raise Http404
