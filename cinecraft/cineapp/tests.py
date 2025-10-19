import pyotp
from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import TOTPDevice


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class OTPTests(TestCase):

	def setUp(self):
		self.user = User.objects.create_user(username='tester', email='otp@example.com', password='pass1234')

	def test_request_and_verify_totp(self):
		# ensure no device exist initially
		resp = self.client.post(reverse('request_otp'), {'email': 'otp@example.com'})
		# should redirect to verify page
		self.assertEqual(resp.status_code, 302)

		device = TOTPDevice.objects.get(user=self.user)
		# one email sent
		self.assertEqual(len(mail.outbox), 1)
		# compute current TOTP code from device secret
		code = pyotp.TOTP(device.secret).now()

		# now post verification
		resp2 = self.client.post(reverse('verify_otp'), {'code': code}, follow=True)
		# should land on dashboard and be authenticated
		self.assertTrue(resp2.wsgi_request.user.is_authenticated)


# Create your tests here.
