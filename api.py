from flask import Flask, request, redirect, url_for
from flask_restful import Resource, Api, reqparse
from werkzeug import secure_filename
import glob, os, sys
from pprint import pprint
from subprocess import call

ALLOWED_EXTENSIONS = set( [ 'rpm', 'srpm' ] )
UPLOAD_FOLDER = './repo'

app = Flask(__name__)
api = Api(app)
app.config['UPLOAD_FOLDER'] = os.path.abspath(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

class rpm(Resource):
    def put(self, project, environment):
        reporoot = os.path.join(app.config['UPLOAD_FOLDER'], project, environment)
        if not os.path.isdir(reporoot):
            os.mkdirs(reporoot)

        file = request.files['file']
        if not file:
            return {'error': 'Upload error'}, 500

        if not allowed_file(file.filename):
            return {'error': 'File extenstion is not allowed'}, 500

        filename = secure_filename(file.filename)

        try:
            file.save(os.path.join(reporoot, filename))
            call(['createrepo','--database', reporoot ])
        except:
            return {'error': 'RPM save error'}, 500

        return {'result':'OK'}, 200


    def get(self, project, environment):
        reporoot = "%s/%s/%s" % (app.config['UPLOAD_FOLDER'], project, environment)
        if not os.path.isdir(reporoot):
            return {'error': 'repository is not exist'}, 404

        repolist = glob.glob("%s/%s" % (reporoot,'*.rpm'))
        repolist = repolist + glob.glob( "%s/%s" % (reporoot, '*.srpm'))

        if not len(repolist):
            return {'error': 'repo is empty'}, 204

        rpmlist = []
        for s in repolist:
            rpmlist.append( os.path.basename(s))

        return { 'rpms': rpmlist }



api.add_resource(rpm, '/rpm/<project>/<environment>')

if __name__ == '__main__':
    DEBUG = os.getenv('YUMY_DEBUG', False)
    app.run(debug=DEBUG)
