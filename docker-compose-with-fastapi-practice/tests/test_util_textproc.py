def test_url_1(textproc):
    url = "http:// nnati.com/bXW"
    patched_url = textproc.correct_url(url)
    assert patched_url == 'http://nnati.com/bXW'


def test_url_2(textproc):
    url = "https:// bankishind-96.agilecrm.com/ landing/5787555313287168"
    patched_url = textproc.correct_url(url)
    assert patched_url == 'https://bankishind-96.agilecrm.com/landing/5787555313287168'


def test_url_3(textproc):
    url = "https://leadstories.com/hoax-alert/2020/09 " \
          "/fact-check-joe-biden-did-call-service-members " \
          "-stupid-bastards-on-camera-but-he-was -making-a-joke-about-them-not-clapping-for-his -comments.html"
    patched_url = textproc.correct_url(url)
    assert patched_url == 'https://leadstories.com/hoax-alert/2020/09/fact-check-joe-biden-did-call-service-members-stupid-bastards-on-camera-but-he-was-making-a-joke-about-them-not-clapping-for-his-comments.html'


def test_url_with_text_1(textproc):
    url = "The next step is here: http:// nnati.com/bXW\n"
    patched_url = textproc.correct_url(url)
    assert patched_url == 'The next step is here: http://nnati.com/bXW\n'


def test_url_with_text_2(textproc):
    url = "The next step is here: http:// nnati.com/bXW\nCome join us!"
    patched_url = textproc.correct_url(url)
    assert patched_url == 'The next step is here: http://nnati.com/bXW\nCome join us!'


def test_url_with_text_3(textproc):
    url = "PayPal: We have limited your account due to safety concerns. Please visit https://paypal-user-id60\n.com " \
          "before we are forced to close your account."
    patched_url = textproc.correct_url(url)
    assert patched_url == 'PayPal: We have limited your account due to safety concerns. Please visit https://paypal-user-id60.com before we are forced to close your account.'
