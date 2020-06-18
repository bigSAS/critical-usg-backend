SET CUSG_TESTING=NO
SET CUSG_DEBUG=NO
:: WIP => prd read CUSG_SECRET & CUSG_DB_CONNETION_STRING from env
SET CUSG_SECRET=TOP-NOTCH-SECRET
SET CUSG_DB_CONNETION_STRING=sqlite:///app.db
.env\Scripts\activate && flask db upgrade && python setup_defaults.py && waitress-serve --call "wsgi:create_app"