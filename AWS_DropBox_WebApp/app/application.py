from flask import Flask,render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import boto3
import urllib  # the lib that handles the url stuff

application = Flask(__name__)
application.config.from_object('config')

# S3 instance
s3_client = boto3.client('s3',
                         aws_access_key_id=application.config['AWS_ACCESS_KEY_ID'],
                         aws_secret_access_key=application.config['AWS_SECRET_ACCESS_KEY'])

s3_resource = boto3.resource('s3',
                         aws_access_key_id=application.config['AWS_ACCESS_KEY_ID'],
                         aws_secret_access_key=application.config['AWS_SECRET_ACCESS_KEY'])


@application.route('/', methods=['GET','POST'])
def show_files():
    Bucket = s3_resource.Bucket(application.config['S3_BUCKET_NAME'])
    key_list = []
    key_url_dict = {}
    profile_img = ""

    for object in Bucket.objects.all():
        key = object.key
        if key[-1] is not '/':

            if key == "mypic.jpg":
                profile_img = s3_client.generate_presigned_url(
                    ClientMethod='get_object',
                    Params={
                        'Bucket':application.config['S3_BUCKET_NAME'],
                        'Key': key
                    }
                )
            else:
                key_info = {
                    'name': key,
                    'size': object.size/1024
                }
                key_list.append(key_info)
                url = s3_client.generate_presigned_url(
                    ClientMethod='get_object',
                    Params={
                        'Bucket':application.config['S3_BUCKET_NAME'],
                        'Key': key
                    }
                )
                key_url_dict[key] = url

    # info = {'info_box':'The list of files'}
    return render_template('index.html', keyList=key_list,urls=key_url_dict, profileimg=profile_img)
    # for object in s3_resource.Bucket(application.config['S3_BUCKET_NAME']).objects.all():
    #     print(object)

@application.route('/retreivefile', methods=['GET','POST'])
def goto_ret():
    if request.method == 'GET':
        return render_template('retreivetext.html')
    elif request.method == 'POST':
        num = request.form['txtfile']
        file = getTextFile(num)

        if file == None:
            info = {'info_box':'The File you want to retrieve does not exist'}
            render_template('index.html', info=info)
        else:
            print(file)
            myfile = open(file,'r')
            print(myfile)
            # data = file.read()

            render_template('retreivetext.html', data=data)


@application.route('/rangedfile', methods=['GET', 'POST'])
def goto_ranged():
    if request.method == 'GET':
        return render_template('rangedtext.html')


@application.route('/upload', methods=['GET','POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        number = request.form['number']
        print(number)
        if file.filename == "":
            info = {'info_box': 'No Files Selected'}
            return render_template('index.html',info=info)
        elif file:
            filename = secure_filename(file.filename)
            filename = filename[:-4] + "_" + number + filename[-4:]
            s3_client.upload_fileobj(file,application.config['S3_BUCKET_NAME'],filename)
            redirect(url_for('show_files'))

        return redirect(url_for('show_files'))

@application.route('/delete/<name>')
def delete_object(name):
    s3_client.delete_object(
        Bucket=application.config["S3_BUCKET_NAME"],
        Key=name
    )

    return redirect(url_for('show_files'))

@application.route('/showimage')
def show_image():
    Bucket = s3_resource.Bucket(application.config['S3_BUCKET_NAME'])
    key_list = []
    key_url_dict = {}

    for object in Bucket.objects.all():
        key = object.key
        if key[-1] is not '/':
            key_info = {
                'name': key,
                'size': object.size / 1024
            }
            key_list.append(key_info)
            url = s3_client.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': application.config['S3_BUCKET_NAME'],
                    'Key': key
                }
            )
            key_url_dict[key] = url

    # info = {'info_box':'The list of files'}
    return render_template('index.html', fileList=key_list, imgurl=key_url_dict)


def getTextFile(num):
    Bucket = s3_resource.Bucket(application.config['S3_BUCKET_NAME'])
    thefile = None

    for file in Bucket.objects.all():
        filename = file.key

        if filename[-3:] == "txt":
            if len(num) == 2:
                if filename[-6:-4] == num :
                    thefile = generateURL(filename)
            elif len(num) == 1:
                if filename[-6] == '-' and filename[-5] == num:
                    thefile = generateURL(filename)

    return thefile


def generateURL(filename):
    url = s3_client.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': application.config['S3_BUCKET_NAME'],
            'Key': filename
        }
    )

    return url

if __name__ == '__main__':
    application.run(debug=True)
