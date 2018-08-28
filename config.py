import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # ...
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = b'\xffX\xb5:\x8b\xa8\xdfFRt\xf0~\xa8\xa9\xa7|\x99\xb6\xbaRM\xfa\x9a\xee' # for WTF-forms and login
    POSTS_PER_PAGE = 21
    BLOGGING_URL_PREFIX = "/article"
    BLOGGING_DISQUS_SITENAME = "TheDailyLedger"
    BLOGGING_SITEURL = "http://thedailyledger.io"
    BLOGGING_SITENAME = "The Daily Ledger"
    BLOGGING_KEYWORDS = ["blog", "meta", "keywords"]
    FILEUPLOAD_IMG_FOLDER = "fileupload"
    FILEUPLOAD_PREFIX = "/fileupload"
    FILEUPLOAD_ALLOWED_EXTENSIONS = ["png", "jpg", "jpeg", "gif"]
