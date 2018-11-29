#!/usr/bin/env python3
from SetUpDb import *
from flask import Flask, render_template, url_for, request, redirect, flash, \
    Markup, jsonify, json
from Authentication import *
import platform
import Google_Oauth2
import fleep
from werkzeug.utils import secure_filename
from titlecase import titlecase

app = Flask(__name__)

try:
    print("Loading Database Catalog.db ...")
    Engine = create_engine('sqlite:///Catalog.db')
    Base.metadata.bind = Engine
    DBSession = sessionmaker(bind=Engine)
    Session = DBSession()
    print("Database loading complete")

except:
    print("The Database could not be loaded. "
          "Did you forget to run Setup.py first?")

# Python interface:

''' Design Note:
    Admin Mode:
        In the python interpreter type in "from application import *"

        Use the Help() function to get a list of all the interface commands and
        their __doc__***Warning*** If you open the app this way, you will be an
        admin. The interface assumes you know what you are doing and you will
        not receive confirmation prompts for edits or deletes. You should take
        care, as you would for a root account.
        Also Admin Mode DOES NOT START THE SERVER, so the web interface will
        not be available.

    Regular User Mode:
        Start the application with python and use the Web Interface via port
        8000. The Web Interface has user authentication safeguards and all
        users are limited to only be able to
        edit there own account.
'''


def man():
    help_message = '''
        Available functions:
        **Add_User**
        {}

        **Edit_User**
        {}

        **Delete_User**
        {}

        **Add_Item**
        {}

        **Edit_Item**
        {}

        **Delete_Item**
        {}

        **Display**
        Display the entire database

        **Display_User**
        Display a selected User

        **Display_Item**
        Display a selected Item

    '''.format(Add_User.__doc__, Edit_User.__doc__, Delete_User.__doc__,
               Add_Item.__doc__, Edit_Item.__doc__, Delete_Item.__doc__)

    print(help_message)


def Add_User(User_Name, Password, First, Last, Email):
    '''
        Adds a User to the database.

        Required Arguments: User_Name, Password, First, Last, Email
        User_ID is automatically assigned.
    '''
    New_User = User(User_Name=User_Name, Password=Create_Hash(Password),
                    First=First, Last=Last, Email=Email)
    Session.add(New_User)
    Session.commit()


def Add_Item(Owner_ID, Name, Category, Description="", Image=""):
    '''
        Adds an Item to the database
        Required arguments: Owner_ID, Name, Category
        Optional arguments: Description, Image
    '''
    New_Item = Item(Owner_ID=Owner_ID,
                    Name=titlecase(Name),
                    Category=titlecase(Category),
                    Description=Description, Image=Image)
    Session.add(New_Item)
    Session.commit()


def Edit_User(ID, User_Name, Password, First, Last, Email):
    '''
        Edit a User in the Database

        Required Arguments: ID, User_Name, Password, First, Last, Email
    '''
    User_To_Edit = Session.query(User).filter(User.ID == ID).one()
    User_To_Edit.User_Name = User_Name
    User_To_Edit.Password = Password
    User_To_Edit.First = First
    User_To_Edit.Last = Last
    User_To_Edit.Email = Email
    Session.add(User_To_Edit)
    Session.commit()


def Edit_Item(ID, Name, Category, Description="", Image=""):
    '''
        Edit an Item in the Database

        Required Arguments: ID, Name, Category
        Optional Arguments: Description, Image
    '''
    Item_To_Edit = Session.query(Item).filter(Item.ID == ID).one()
    Item_To_Edit.Name = titlecase(Name)
    Item_To_Edit.Category = titlecase(Category)
    Item_To_Edit.Description = Description
    Item_To_Edit.Image = Image

    Session.add(Item_To_Edit)
    Session.commit()


def Delete_User(ID):
    Selected_User = Session.query(User).filter_by(ID=ID).one()
    Users_Items = Session.query(Item).filter_by(Owner_ID=ID).all()
    if Users_Items != []:
        for thing in Users_Items:
            Session.delete(thing)
    if Selected_User != []:
        Session.delete(Selected_User)
        Session.commit()


def Delete_Item(ID):
    Selected_Item = Session.query(Item).filter_by(ID=ID).one()
    if Selected_Item != []:
        Session.delete(Selected_Item)
        Session.commit()


def Display():
    Display_User()
    Display_Item()


def Display_User():
    Users = Session.query(User).all()
    print("Users:")
    for Person in Users:
        Output = '''
            ID:{}
            User Name:{}
            Password:{}
            Name:{} {}
            Online:{}
        '''.format(Person.ID, Person.User_Name, Person.Password, Person.First,
                   Person.Last, Person.Logged_In)
        print(Output)


def Display_Item():
    ItemList = Session.query(Item).all()
    print("Items:")
    for item in ItemList:
        Output = '''
            Owner:{}
            Owner_ID:{}
            Category:{}
            Name:{}
            Description:{}
            Image:{}'''.format(
            item.Owner.User_Name,
            item.Owner_ID,
            item.Category,
            item.Name,
            item.Description,
            item.Image)
        print(Output)


def Set_Password(ID, Password):
    Select_User = Session.query(User).filter(User.ID == ID).one()
    if Select_User is not None:
        Select_User.Password = Create_Hash(Password)


# Web Interface

@app.route('/')
def Landing():
    return render_template('Landing.html')


@app.route('/Filters.html')
def Filters():
    Users = Session.query(User)
    Categorys = Session.query(
        Item.Category).distinct(Item.Category).order_by(Item.Category)
    return render_template('Filters.html', Categorys=Categorys, Users=Users)


@app.route('/Register/', methods=['GET', 'POST'])
def Register():
    if request.method == "POST":
        # Corrections_Needed will be set to True if verification fails
        Corrections_Needed = False

        # Verify required fields are filled out
        if request.form['User_Name'] == "":
            Corrections_Needed = True
            flash("You need a unique User Name.")
        else:
            # Verify UserName is unique
            Check_User_Name = Session.query(
                User).filter(
                User.User_Name == request.form['User_Name']).first()
            if Check_User_Name is not None:
                Corrections_Needed = True
                flash("Sorry, but {} is already taken.".format(
                    request.form["User_Name"]))

        if request.form['First'] == "":
            Corrections_Needed = True
            flash("First name is required.")

        if request.form['Last'] == "":
            Corrections_Needed = True
            flash("Last name is required.")

        if request.form['Email'] == "":
            Corrections_Needed = True
            flash("Email is required.")

        if request.form['Password_1'] == "":
            Corrections_Needed = True
            flash("A password is required.")

        elif request.form['Password_2'] == "":
            Corrections_Needed = True
            flash("Please confirm your password.")

        elif request.form['Password_1'] != request.form['Password_2']:
            Corrections_Needed = True
            flash("Your password and the confirmation password didn't match.")

        if Corrections_Needed:
            return render_template('Register.html')

        else:
            Add_User(
                request.form['User_Name'],
                request.form['Password_1'],
                request.form['First'],
                request.form['Last'],
                request.form['Email'])
            Query = Session.query(User).filter(
                User.User_Name == request.form['User_Name']).one()
            Load_Session(Query)
            return redirect("Home")
    else:
        return render_template('Register.html')


@app.route("/Home/")
def Home():
    if Flask_Session.get('gplus_id'):
        print("gplus_id was found")
        Query = Session.query(
            User).filter(User.Email == Flask_Session["Email"]).first()
        if Query is None:
            New_User = User(
                Email=Flask_Session["Email"],
                Google_ID=Flask_Session['gplus_id'],
                User_Name=Flask_Session["User_Name"],
                Password="Password",
                First=Flask_Session["First"],
                Last=Flask_Session["Last"],
                Profile_Pic=Flask_Session["Picture"]
            )

            Session.add(New_User)
            Session.commit()

    return render_template("Home.html", Flask_Session=Flask_Session)


@app.route("/Profile_Editor/", methods=['GET', 'POST'])
def Profile_Editor():
    if request.method == "POST":
        Query = Session.query(User).filter(
            User.ID == Flask_Session["User_ID"]).one()
        if request.form['User_Name'] != "" and \
                request.form['User_Name'] != Flask_Session['User_Name']:
            # Verify UserName is unique
            Check_User_Name = Session.query(User).filter(
                User.User_Name == request.form['User_Name']).first()
            if Check_User_Name is None:
                Query.User_Name = request.form['User_Name']
            else:
                flash("Sorry, but {} is already taken.".format(
                    request.form["User_Name"]))

        if request.form['First'] != "":
            Query.First = request.form['First']
        if request.form['Last'] != "":
            Query.Last = request.form['Last']
        if request.form['Email'] != "":
            Query.Email = request.form['Email']
        if request.form['Password_1'] != "" and request.form['Password_2'] \
                and request.form['Password_1'] == request.form['Password_2']:
            Query.Password = Create_Hash(request.form['Password_1'])
        Session.add(Query)
        flash("Your profile has been updated.")
        Edited_Profile = Session.query(User).filter(
            User.ID == Flask_Session["User_ID"]).one()
        Load_Session(Edited_Profile)

        return redirect(url_for('Home'))
    else:
        return render_template(
            "Profile_Editor.html", Flask_Session=Flask_Session)


@app.route("/Delete_Profile/", methods=['GET', 'POST'])
def Delete_Profile():
    if request.method == "POST":
        Delete_User(Flask_Session["User_ID"])
        return redirect(url_for('Landing'))
    else:
        return render_template("Delete_Profile.html")


@app.route('/Log_In/', methods=['GET', 'POST'])
def Log_In(
    DATA_SCOPE="openid email",
        Client_Secret="Item-Catalog-Google-Oauth.json",
        data_Approvalprompt="force"):

    if request.method == "POST":
        try:
            User_Data = Session.query(User).filter(
                User.User_Name == request.form['User_Name']).one()

        except:
            flash(Markup(
                '''That user doesn't exist. Would you like to
                <a href = '{}'>sign up?</a>'''.format(url_for("Register"))))
            return render_template("Log_In.html")

        Password = request.form['Password']
        if Verify_Hash(Password, User_Data.Password):
            User_Data.Logged_In = True
            Session.add(User_Data)
            Session.commit()
            Load_Session(User_Data)
            return render_template("Home.html", Flask_Session=Flask_Session)
        else:
            flash("Wrong Password")
            return render_template("Log_In.html")

    else:
        DATA_CLIENT_ID = json.loads(
            open(Client_Secret, 'r').read())['web']['client_id']
        # Create anti-forgery state token
        state = ''.join(random.choice(
            string.ascii_uppercase + string.digits) for x in range(32))
        Flask_Session['state'] = state
        return render_template(
            'Log_In.html',
            app=app,
            STATE=state,
            DATA_CLIENT_ID=DATA_CLIENT_ID,
            DATA_SCOPE=DATA_SCOPE,
            data_Approvalprompt=data_Approvalprompt)


def Load_Session(User_Data):
    Flask_Session['User_ID'] = User_Data.ID
    Flask_Session['User_Name'] = User_Data.User_Name
    Flask_Session['First'] = User_Data.First
    Flask_Session['Last'] = User_Data.Last
    Flask_Session['Email'] = User_Data.Email


@app.route('/Log_Out/')
def Log_Out():
    # if(Flask_Session[])
    Flask_Session.clear()
    return render_template('Landing.html')


@app.route('/User/<int:User_ID>/<string:User_Name>/')
def Display_Item_By_User(User_ID, User_Name):
    Query = Session.query(Item).filter(
        Item.Owner_ID == User_ID).order_by(Item.Category)
    return render_template(
        'Items_By_User.html',
        Query=Query,
        User_ID=User_ID,
        User_Name=User_Name,
        Flask_Session=Flask_Session)


@app.route('/<string:Item_Type>/')
def Display_Item_By_Type(Item_Type):
    Query = Session.query(Item).filter(
        Item.Category == Item_Type)

    return render_template(
        'Item_Type.html',
        Query=Query,
        Item_Type=Item_Type,
        Flask_Session=Flask_Session)


@app.route('/New_Item/', methods=['GET', 'POST'])
def New_Item():
    if request.method == 'POST':
        if request.form['Name'] is None or request.form['Category'] is None:
            return render_template(
                'New_Item.html',
                Flask_Session=Flask_Session)
        else:
            file_list = request.files.getlist('file')[0]
            image_path = upload(file_list)

            print(image_path)
            Add_Item(
                Flask_Session['User_ID'],
                request.form['Name'],
                request.form['Category'],
                request.form['Description'],
                image_path)
        return render_template('Update.html')
    else:
        return render_template('New_Item.html', Flask_Session=Flask_Session)


@app.route('/Edit/<int:Item_ID>', methods=['GET', 'POST'])
def Item_Editor(Item_ID):
    Query = Session.query(Item).filter(Item.ID == Item_ID).one()
    if request.method == 'POST':
        file_list = request.files.getlist('file')[0]
        image_path = upload(file_list)
        if image_path is not "" and image_path is not None:
            # check to see if user changed the photo
            if Query.Image is not "" and Query.Image is not None:
                # if the photo is being changed, delete the old one
                delete_file(Query.Image)
        else:
            image_path = Query.Image

        Edit_Item(
            Query.ID,
            request.form['Name'],
            request.form['Category'],
            request.form['Description'],
            image_path)
        return render_template('Update.html')
    else:
        return render_template('Edit.html', Query=Query, Item_ID=Item_ID)


@app.route('/Delete_Item/<int:Item_ID>', methods=['GET', 'POST'])
def Delete_Selected_Item(Item_ID):
    Query = Session.query(Item).filter(Item.ID == Item_ID).one()
    if request.method == 'POST':
        '''Delete_Item'''
        Delete_Item(Item_ID)
        return render_template("Update.html")
    else:
        return render_template(
            'Delete_Item.html',
            Query=Query,
            Item_ID=Item_ID)


'''API for JSON output'''


@app.route('/API/')
def API():
    """This is the help page for the API"""
    return render_template("API.html")


@app.route('/API/item_by_id/<int:Item_ID>')
def api_item_by_id(Item_ID):
    query = Session.query(Item).filter(Item.ID == Item_ID).first()
    if (query is None):
        item = jsonify({'Bad Item ID': None})
    else:
        item = jsonify(Item=query.serialize)

    return item


@app.route('/API/item_by_user/<string:User_Name>')
def api_item_by_user(User_Name):
    selected_user = Session.query(User).filter(
        User.User_Name == User_Name).first()
    ID = selected_user.ID
    query = Session.query(Item).filter(Item.Owner_ID == ID).all()
    if (query is None):
        item_list = jsonify({'No Items Found For That User': User_Name})
    else:
        item_list = jsonify(Item=[i.serialize for i in query])

    return item_list


@app.route('/API/item_by_type/<string:Item_Type>')
def api_item_by_type(Item_Type):
    query = Session.query(Item).filter(Item.Category == Item_Type).all()
    if (query is None):
        item_list = jsonify({'No Items found for that Category': Item_Type})
    else:
        item_list = jsonify(Item=[i.serialize for i in query])

    return item_list


'''Functions for File processing'''


def good_file(File, Allowed_Type="raster-image"):
    """
    checks the magic number of File and returns
    True if File matches the Allowed_Type
    File is a file
    Allowed_Type is one of the following types:
        "3d-image":
            .C4D, .FBX, .MA, .MS3D, .MTL, .OBJ, .PLY, .WRL, .X3D, .XSI
        "archive":
            7Z, DMG, GZ, ISO, RAR, TAR.Z,ZIP
        "audio":
            .AAC, .AC3, .AIFF, .AMR, .AU, .FLAC, .M4A,
            .MIDI, .MKA, .MP3, .OGA, .RA, .VOC, .WAV, .WMA
        "database":
            .SQLITE,
        "document":
            .DOC, .DOCX, .EPUB, .KEY, .NUMBERS, .ODP, .ODS, .ODT,
                .PAGES, .PDF, .PPS, .PPT, .PPTX, .RTF, .XLS, .XLSX, .XML
        "executable":
            .COM, .EXE, .JAR
        "font":
            .OTF, .TTF, .WOFF, .WOFF2
        "raster-image":
            .BMP, .GIF, .ICO, .JP2, .JPEG, .PNG, .PSD, .TIFF, .WEBP
        "raw-image":
            .ARW, .CR2, .CRW, .DNG, .ERF, .NEF, .NRW,
            .ORF, .PEF, .RAF, .RAW, .RW2, .SRW, .X3F
        "system":
            .CAB, .CAT, .DLL, .DRV, .REG, .SDB, .SYS
        "vector-image":
            .AI, .EPS
        "video":
            .3G2, .3GP, .ASF, .AVI, .FLV, .M4V, .MKV,
            .MOV, .MP4, .MPG, .OGV, .SWF, .VOB, .WEBM, .WMV
    """
    info = fleep.get(File.read(128))
    # reset the file so that the file gets saved correctly
    File.seek(0, 0)
    print(info.type)
    print(info.extension)
    print(info.mime)
    return info.type_matches(Allowed_Type)


def upload(file, subfolder='./static', file_type="raster-image"):
    """
    Scans the magic number of a user uploaded file to make sure it is an image
    file if it is then upload saves the file and returns the path on the server
    to the image otherwise it returns None
    """
    target = os.path.join(APP_ROOT, subfolder)
    print(target)

    if not os.path.isdir(target):
        os.mkdir(target)

    file_name = secure_filename(file.filename)
    print(file_name)
    destination = "/".join([target, file_name])
    # destination = target + file_name
    print(destination)

    if good_file(file, file_type):
        file.save(destination)
        return file_name
    else:
        print("That File Type is not allowed")
        return None


def delete_file(file_name, subfolder='static/'):
    target = os.path.join(APP_ROOT, subfolder)
    path = target + file_name
    os.remove(path)


if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.debug = True
    APP_ROOT = os.path.dirname(sys.modules['__main__'].__file__)
    Google_Oauth2.init(app, Flask_Session, "Item-Catalog-Google-Oauth.json")

    if platform.system() == "Linux":
        app.run(host='0.0.0.0', port=8000)
    else:
        app.run(host='localhost', port=8000)
