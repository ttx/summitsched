
def session_to_form(session):
    form = session.copy()
    form['description'] = form['description'].replace('<br />','\n')
    return form

def form_to_session(formdata):
    session = formdata.copy()
    session['description'] = session['description'].replace('\n','<br />')
    return session
