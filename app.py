from flask import Flask
import orm

app = Flask(__name__)
db = orm.DB(5001,
            dbContainerAddress='db-cluster',
            initialValue='docker')

@app.route('/')
def base():
    return '테스트'


@app.route('/w/<text>')
def wdb(text):
    return db.test_add(text)

@app.route('/r/')
def rdb():
    res = db.test_view()
    return db.htmlfy(res)

@app.route('/s/<kwd>')
def sdb(kwd):
    res = db.search(kwd)
    kwds = kwd.split(' ')
    return db.htmlfy(res,highlights=kwds)

@app.route('/sk/')
def skdb():
    return db.return_search_kwd()
    

if __name__ == '__main__':
    app.run()
