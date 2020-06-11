# Critical USG - backend app
## Create user from python interpreter   
```python
# run python in (.env)
from app import db
from db.model import User
jimmy = User("jimmy@choo.io", "jimmyh")
db.session.add(jimmy)
db.session.commit()
exit()
# local admin sas@kodzi.io :: sas
# local user jimmy@choo.io :: jimmyh
```
